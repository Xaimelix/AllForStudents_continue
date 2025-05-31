import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin


class Application_Eviction(SqlAlchemyBase, UserMixin):
    __tablename__ = 'application_eviction'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    status = sqlalchemy.Column(sqlalchemy.String)
    date = sqlalchemy.Column(sqlalchemy.Date)
    student_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('student.id'))
    comment = sqlalchemy.Column(sqlalchemy.String)

    student = sqlalchemy.orm.relationship('Student', back_populates='application_eviction')
    