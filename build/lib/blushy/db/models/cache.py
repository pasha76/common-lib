
from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from blushy.db.models import Base
from sqlalchemy import inspect
import json


class Cache(Base):
    
    
    __tablename__ = 'caches'
    id = Column(Integer, primary_key=True) 
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False,index=True)
    post=relationship('Post', back_populates='caches')
    response_text= Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime, nullable=False)