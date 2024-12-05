from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from common.db.models import Base
from sqlalchemy import inspect

class MasterStyle(Base):
    __tablename__ = 'master_styles'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), unique=True, nullable=False)
    post_labels = relationship('Label', back_populates='master_style')
    image_labels = relationship('ImageLabel', back_populates='master_style')