from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from common.db.models import Base
from sqlalchemy import inspect

                            
class UserStatus(Base):
    __tablename__ = 'user_statuses'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    users = relationship('User', back_populates='user_status')