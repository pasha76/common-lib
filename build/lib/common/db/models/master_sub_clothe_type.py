
from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from common.db.models import Base
from sqlalchemy import inspect


class MasterSubClotheType(Base):
    __tablename__ = 'master_sub_clothe_types'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    google_clothe_type_id = Column(Integer, ForeignKey('ai_clothe_types.id'), nullable=False)
    master_clothe_type_id = Column(Integer, ForeignKey('master_clothe_types.id'), nullable=False)

    # Establishing the relationship to MasterClotheType
    master_clothe_type = relationship('MasterClotheType', back_populates='sub_clothe_types')
    google_clothe_type = relationship('AIClotheType', back_populates='master_sub_clothe_types')

