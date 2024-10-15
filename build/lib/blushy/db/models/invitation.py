
from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from blushy.db.models import Base
from sqlalchemy import inspect

class Invitation(Base):
    __tablename__ = 'invitations'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False,index=True)
    user=relationship('User', back_populates='invitations')
    invitation_key = Column(String(5), nullable=False,unique=True,index=True)
    instagram_username = Column(String(50), nullable=False)
    youtube_username = Column(String(50), nullable=False)
    tiktok_username = Column(String(50), nullable=False)
    invitation_status = Column(Integer,default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

