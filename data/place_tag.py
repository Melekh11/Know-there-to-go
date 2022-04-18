import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class PlaceTag(SqlAlchemyBase):
    __tablename__ = 'place_tag'
    place_id = sqlalchemy.Column(sqlalchemy.ForeignKey('places.id'), primary_key=True)
    tag_id = sqlalchemy.Column(sqlalchemy.ForeignKey('tags.id'), primary_key=True)
    # extra_data = Column(String(50))
    place = orm.relation("Places", back_populates="tag")
    tag = orm.relation("Tags", back_populates="place")
