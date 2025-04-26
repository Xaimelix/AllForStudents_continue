import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin


class Room(SqlAlchemyBase, UserMixin):
    __tablename__ = 'room'


    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    hostel_id = sqlalchemy.Column(sqlalchemy.Integer)
    square = sqlalchemy.Column(sqlalchemy.Float)
    max_cnt_student = sqlalchemy.Column(sqlalchemy.Integer)
    cur_cnt_student = sqlalchemy.Column(sqlalchemy.Integer)
    floor = sqlalchemy.Column(sqlalchemy.Integer)
    sex = sqlalchemy.Column(sqlalchemy.Boolean)
    side = sqlalchemy.Column(sqlalchemy.String)

    student = sqlalchemy.orm.relationship('student', back_populates='room')
