
from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from blushy.db.models import Base
from sqlalchemy import inspect

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False,index=True)
    user=relationship('User', back_populates='comments')
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False, index=True)
    post = relationship('Post', back_populates='comments')
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

