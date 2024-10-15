
from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from blushy.db.models import Base
from sqlalchemy import inspect

class SearchHistory(Base):
    __tablename__ = 'search_histories'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False,index=True)
    user=relationship('User', back_populates='invitations')
    keywords = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

