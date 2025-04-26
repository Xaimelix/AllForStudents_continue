import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin


class StudentAndTag(SqlAlchemyBase, UserMixin):
    __tablename__ = 'studentANDtags'

    id = sqlalchemy.Column(sqlalchemy.Integer, unique=True, primary_key=True)
    student_id = sqlalchemy.Column(sqlalchemy.Integer)
    tag_id = sqlalchemy.Column(sqlalchemy.Integer)
