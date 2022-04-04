import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Image(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'images'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    image = sqlalchemy.Column(sqlalchemy.BLOB)
    user = orm.relation("User", back_populates='image', lazy='subquery')
    studie = orm.relation("Studie", back_populates='image', lazy='subquery')
