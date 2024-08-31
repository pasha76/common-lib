from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from blushy.db.models import Base
from sqlalchemy import inspect

class AIClotheType(Base):
    __tablename__ = 'ai_clothe_types'
    id = Column(Integer, primary_key=True)
    name = Column(String(200),  nullable=False)
    source = Column(String(100),  nullable=False)
    master_clothe_type_id = Column(Integer, ForeignKey('master_clothe_types.id')) 
    master_clothe_type = relationship('MasterClotheType', back_populates='ai_clothe_types')
    image_labels=relationship("ImageLabel",back_populates="ai_clothe_type")
    post_labels=relationship("Label",back_populates="ai_clothe_type")
    items=relationship("Item",back_populates="ai_clothe_type")
    master_sub_clothe_types=relationship("MasterSubClotheType",back_populates="google_clothe_type")

