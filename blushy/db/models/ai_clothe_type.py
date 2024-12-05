from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from blushy.db.models import Base
from sqlalchemy import inspect

class AIClotheType(Base):
    __tablename__ = 'ai_clothe_types'
    id = Column(Integer, primary_key=True)
    name = Column(String(200),  nullable=False)
    master_clothe_type_id = Column(Integer, ForeignKey('master_clothe_types.id')) 
    master_clothe_type = relationship('MasterClotheType', back_populates='ai_clothe_types')
    post_labels=relationship("Label",back_populates="ai_clothe_type")
    items=relationship("Item",back_populates="ai_clothe_type")

