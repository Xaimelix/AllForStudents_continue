import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin


class Hostel(SqlAlchemyBase, UserMixin):
    __tablename__ = 'hostel'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    address = sqlalchemy.Column(sqlalchemy.String)
    district = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.Text)

    # общежития с фотографиями
    # общежития с описанием

    room = sqlalchemy.orm.relationship('Room', back_populates='hostel')