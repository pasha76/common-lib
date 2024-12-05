
from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from blushy.db.models import Base
from sqlalchemy import inspect

class FavoritedPost(Base):
    __tablename__ = 'favorited_posts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False,index=True)
    user=relationship('User', back_populates='favorited_posts')
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False,index=True)
    post=relationship('Post', back_populates='favorited_posts')
    created_at = Column(DateTime, default=datetime.utcnow)

