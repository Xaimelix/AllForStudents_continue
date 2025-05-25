import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin


class HelpRequests(SqlAlchemyBase, UserMixin):
    __tablename__ = 'help_requests'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, nullable=True, unique=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    status = sqlalchemy.Column(sqlalchemy.String, nullable=False, default='open')
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    reply = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    is_replied = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
