import sqlalchemy
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Student(SqlAlchemyBase, UserMixin):
    __tablename__ = 'student'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    login = sqlalchemy.Column(sqlalchemy.String, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    name = sqlalchemy.Column(sqlalchemy.String)
    surname = sqlalchemy.Column(sqlalchemy.String)
    room_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('room.id'), nullable=True)
    course = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    sex = sqlalchemy.Column(sqlalchemy.Boolean)

    room = sqlalchemy.orm.relationship('Room', back_populates='students')
    application_request = sqlalchemy.orm.relationship('Application_request', back_populates='student')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password, method='pbkdf2')

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)