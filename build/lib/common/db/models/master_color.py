from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from common.db.models import Base
from sqlalchemy import inspect


class MasterColor(Base):
    __tablename__ = 'master_colors'
    id = Column(Integer, primary_key=True)
    title = Column(String(10), unique=True, nullable=False)

    #colors = relationship('Color', back_populates='master_colors')
    labels = relationship('Label', back_populates='master_color')
    image_labels = relationship('ImageLabel', back_populates='master_color')