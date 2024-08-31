from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from common.db.models import Base
from sqlalchemy import inspect

class SeenPost(Base):
    __tablename__ = 'seen_posts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    count = Column(Integer, nullable=False,default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship('User', back_populates='seen_posts')
    post = relationship('Post', back_populates='seen_posts')

