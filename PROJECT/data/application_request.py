import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin


class Application_request(SqlAlchemyBase, UserMixin):
    __tablename__ = 'application_request'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    student_id = sqlalchemy.Column(sqlalchemy.Integer)
    room_id = sqlalchemy.Column(sqlalchemy.Integer)
    status = sqlalchemy.Column(sqlalchemy.String)
    date_entr = sqlalchemy.Column(sqlalchemy.Date)
    date_exit = sqlalchemy.Column(sqlalchemy.Date)