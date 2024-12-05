from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from blushy.db.models import Base
from sqlalchemy import inspect

class MasterStatus(Base): 
    __tablename__ = 'master_statuses'
    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True, nullable=False)  # e.g., "Active", "Draft", etc.

    items = relationship('Item', back_populates='master_status')