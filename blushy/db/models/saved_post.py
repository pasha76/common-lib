from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from blushy.db.models import Base
from sqlalchemy import inspect

class SavedPost(Base):
    __tablename__ = 'saved_posts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False,index=True)
    user=relationship('User', back_populates='saved_posts')
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False,index=True)
    post=relationship('Post', back_populates='saved_posts')
    created_at = Column(DateTime, default=datetime.utcnow) 
    
