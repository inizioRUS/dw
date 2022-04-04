import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Rating(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'ratings'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    id_studie = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    id_user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("studies.id"))
    score = sqlalchemy.Column(sqlalchemy.Integer)
    studie = orm.relation('Studie')
    user = orm.relation('User')
