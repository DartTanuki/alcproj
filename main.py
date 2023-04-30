from flask import Flask, render_template, redirect, abort, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user


from data.db_session import global_init
from data.db_session import create_session

from data.users import User
from data.work import Jobs
from data.departaments import Departament

from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, EmailField, BooleanField, StringField, IntegerField
from wtforms.validators import DataRequired

from werkzeug.security import generate_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

global_init('db/task.db')
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    db_sess = create_session()
    return db_sess.query(User).get(user_id)


#  Формы
class RegisterForm(FlaskForm):
    email = EmailField('Login / Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    repeat_password = PasswordField('Repeat Password', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    age = StringField('Age')
    position = StringField('Position')
    speciality = StringField('Speciality')
    address = StringField('Address')
    submit = SubmitField('Button')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class AddJobForm(FlaskForm):
    job = StringField('Job Title', validators=[DataRequired()])
    team_leader = IntegerField('Team Leader id', validators=[DataRequired()])
    work_size = StringField('Work Size', validators=[DataRequired()])
    collaborators = StringField('Collaborators', validators=[DataRequired()])
    is_finished = BooleanField('Is job finished?')

    submit = SubmitField('Submit')


@app.route('/')
def main_page():
    db_sess = create_session()
    jobs = db_sess.query(Jobs).all()
    return render_template('main.html', jobs=jobs)


@app.route('/departments')
def departments_page():
    db_sess = create_session()
    departments = db_sess.query(Departament).all()
    return render_template('departments_main.html', departments=departments)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = create_session()
        userr = db_sess.query(User).filter(User.email == form.email.data).first()
        if userr and userr.check_password(form.password.data):
            login_user(userr, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.repeat_password.data:
            return render_template('register.html', form=form, message="Пароли не совпадают!")
        db_sess = create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', form=form, message='Такой пользователь уже есть!')
        user = User(name=form.name.data, surname=form.surname.data, email=form.email.data,
                    age=form.age.data, position=form.position.data, speciality=form.speciality.data,
                    address=form.address.data, hashed_password=generate_password_hash(form.password.data))
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', form=form, message="")


@app.route('/addjob', methods=['GET', 'POST'])
def addjob():
    add_form = AddJobForm()
    if add_form.validate_on_submit():
        db_sess = create_session()
        jobs = Jobs(
            job=add_form.job.data,
            team_leader=add_form.team_leader.data,
            work_size=add_form.work_size.data,
            collaborators=add_form.collaborators.data,
            is_finished=add_form.is_finished.data
        )
        db_sess.add(jobs)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('add_job.html', title='Adding a job', form=add_form)


@app.route('/jobs/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = AddJobForm()
    if request.method == "GET":
        db_sess = create_session()
        jobs = db_sess.query(Jobs).filter(Jobs.id == id,
                                          ((Jobs.team_leader == current_user.id) | (current_user.id == 1))).first()
        if jobs:
            form.job.data = jobs.job
            form.team_leader.data = jobs.team_leader
            form.work_size.data = jobs.work_size
            form.collaborators.data = jobs.collaborators
            form.is_finished.data = jobs.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = create_session()
        jobs = db_sess.query(Jobs).filter(Jobs.id == id,
                                          ((Jobs.team_leader == current_user.id) | (current_user.id == 1))).first()
        if jobs:
            jobs.job = form.job.data
            jobs.team_leader = form.team_leader.data
            jobs.work_size = form.work_size.data
            jobs.collaborators = form.collaborators.data
            jobs.is_finished = form.is_finished.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('add_job.html',
                           title='Редактирование новости',
                           form=form)


@app.route('/delete_jobs/<int:id>')
@login_required
def delete_job(id):
    db_sess = create_session()
    job = db_sess.query(Jobs).filter(Jobs.id == id,
                                     ((Jobs.team_leader == current_user.id) | (current_user.id == 1))).first()
    if job:
        db_sess.delete(job)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")



class DepartmentForm(FlaskForm):
    title = StringField('Department Title', validators=[DataRequired()])
    chief = IntegerField('Chief ID', validators=[DataRequired()])
    members = StringField('Members', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    submit = SubmitField('Добавить')

@app.route('/add_departments', methods=['GET', 'POST'])
@login_required
def creating_department():
    form = DepartmentForm()
    if form.validate_on_submit():
        db_sess = create_session()
        departments = db_sess.query(Departament).filter(Departament.email == form.email.data).first()

        if departments:
            return render_template('add_department.html', form=form, title='Adding Department',
                                   message='Департамент с таким email уже существует!')

        department = Departament(title=form.title.data, chief=form.chief.data, members=form.members.data,
                                 email=form.email.data)
        db_sess.add(department)
        db_sess.commit()
        return redirect('/departments')
    return render_template('add_department.html', form=form, title='Adding Department', message='')


@app.route('/departments/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_departments(id):
    form = DepartmentForm()
    if request.method == "GET":
        db_sess = create_session()
        deps = db_sess.query(Departament).filter(Departament.id == id,
                                          ((Departament.chief == current_user.id) | (current_user.id == 1))).first()
        if deps:
            form.title.data = deps.title
            form.chief.data = deps.chief
            form.members.data = deps.members
            form.email.data = deps.email
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = create_session()
        deps = db_sess.query(Departament).filter(Departament.id == id,
                                          ((Departament.chief == current_user.id) | (current_user.id == 1))).first()
        if deps:
            deps.title = form.title.data
            deps.chief = form.chief.data
            deps.members = form.members.data
            deps.email = form.email.data
            db_sess.commit()
            return redirect('/departments')
        else:
            abort(404)
    return render_template('add_department.html',
                           title='Редактирование новости',
                           form=form)


@app.route('/delete_departments/<int:id>')
@login_required
def delete_department(id):
    db_sess = create_session()
    dep = db_sess.query(Departament).filter(Departament.id == id,
                                     ((Departament.chief == current_user.id) | (current_user.id == 1))).first()
    if dep:
        db_sess.delete(dep)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/departments')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)