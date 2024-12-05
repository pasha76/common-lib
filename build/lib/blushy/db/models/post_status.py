from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from blushy.db.models import Base
from sqlalchemy import inspect


class PostStatus(Base):
    __tablename__ = 'post_statuses'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), unique=True, nullable=False)
    posts = relationship('Post', back_populates='post_status')