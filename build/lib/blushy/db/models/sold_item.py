from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from common.db.models import Base
from sqlalchemy import inspect


class SoldItem(Base):
    __tablename__ = 'sold_items'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship('User', back_populates='sold_items')
    item = relationship('Item', back_populates='sold_items')
    post = relationship('Post', back_populates='sold_items')
