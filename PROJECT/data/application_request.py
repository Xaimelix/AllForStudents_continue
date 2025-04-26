import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin


class Application_request(SqlAlchemyBase, UserMixin):
    __tablename__ = 'application_request'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    status = sqlalchemy.Column(sqlalchemy.String)
    date_entr = sqlalchemy.Column(sqlalchemy.Date)
    date_exit = sqlalchemy.Column(sqlalchemy.Date)
    room_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('room.id'))
    student_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('student.id'))

    student = sqlalchemy.orm.relationship('Student', back_populates='application_request')
    room = sqlalchemy.orm.relationship('Room', back_populates='application_request')