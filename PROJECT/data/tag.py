import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin

class Tag(SqlAlchemyBase, UserMixin):
    __tablename__ = 'tag'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)