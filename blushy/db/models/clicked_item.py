from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from blushy.db.models import Base
from sqlalchemy import inspect


class ClickedItem(Base):
    __tablename__ = 'clicked_items'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    preview = Column(Integer,default=0)
    visit = Column(Integer,default=0)
    link = Column(String(800),nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship('User', back_populates='clicked_items')
    item = relationship('Item', back_populates='clicked_items')
    post = relationship('Post', back_populates='clicked_items')

