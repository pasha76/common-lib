from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from common.db.models import Base
from sqlalchemy import inspect



class GoogleClotheType(Base):
    __tablename__ = 'google_clothe_types'
    id = Column(Integer, primary_key=True)

    code = Column(Integer, unique=True, nullable=False)
    fullname = Column(String(500), unique=True, nullable=False)
    name = Column(String(150), unique=True, nullable=False)
    master_clothe_type_id = Column(Integer, ForeignKey('master_clothe_types.id'), nullable=False)
    master_clothe_type = relationship('MasterClotheType', back_populates='google_clothe_types')

