import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from werkzeug.security import check_password_hash
from flask_login import UserMixin

# class User(SqlAlchemyBase):
#     __tablename__ = 'users'
#     id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
#     name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
#     about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
#     email = sqlalchemy.Column(sqlalchemy.String, index=True, nullable=True, unique=True)
#     hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
#     created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
#     users = orm.relationship('News')


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    position = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    speciality = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    address = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)