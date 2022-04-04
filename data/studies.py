import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Studie(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'studies'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    main_images = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("images.id"))
    main_name = sqlalchemy.Column(sqlalchemy.String)
    images = sqlalchemy.Column(sqlalchemy.String)
    texts = sqlalchemy.Column(sqlalchemy.String)
    made_data = sqlalchemy.Column(sqlalchemy.DateTime)
    description = sqlalchemy.Column(sqlalchemy.String)
    commemts = orm.relation("Comment", back_populates='studie', lazy='subquery')
    ratings = orm.relation("Rating", back_populates='studie', lazy='subquery')
    user = orm.relation('User')
    image = orm.relation('Image')
