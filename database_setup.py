import sys
import os
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from datetime import datetime
from sqlalchemy import desc

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Item(Base):
    __tablename__ = "item"
    name = Column(String(40), nullable=False)
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String(1500), nullable=False)
    category = Column(String(40), nullable=False)
    views = Column(Integer, default=0)
    created_at = Column(String(50), default=(
        datetime.utcnow().strftime('%Y-%m-%d %H:%M')))
    img_path = Column(String(1000), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user_email = Column(String(250), nullable=False)
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'views': self.views,
            'created_at': self.created_at,
            'id': self.id,
        }


engine = create_engine(
  'sqlite:///item.dp')
Base.metadata.create_all(engine)
