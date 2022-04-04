import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Comment(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    studie_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("studies.id"))
    made_data = sqlalchemy.Column(sqlalchemy.DateTime)
    text = sqlalchemy.Column(sqlalchemy.String)
    check_this = sqlalchemy.Column(sqlalchemy.Boolean)
    studie = orm.relation('Studie')
    user = orm.relation('User')
