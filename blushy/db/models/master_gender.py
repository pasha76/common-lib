from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from blushy.db.models import Base
from sqlalchemy import inspect


class MasterGender(Base):
    __tablename__ = 'master_genders'
    id = Column(Integer, primary_key=True)
    name = Column(String(10), unique=True, nullable=False)

    users = relationship('User', back_populates='master_gender')
    posts=relationship('Post', back_populates="master_gender")
    items=relationship('Item', back_populates="master_gender")
    


