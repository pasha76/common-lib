from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from blushy.db.models import Base
from sqlalchemy import inspect


class ClotheType(Base):
    __tablename__ = 'clothe_types'
    id = Column(Integer, primary_key=True)
    name = Column(String(100),  nullable=False)

    items = relationship('Item', back_populates='clothe_type')
    
    master_clothe_type_id = Column(Integer, ForeignKey('master_clothe_types.id')) 
    master_clothe_type = relationship('MasterClotheType', back_populates='clothe_types')
    
    vendor_id = Column(Integer, ForeignKey('vendors.id'))  # Add a ForeignKey
    vendor = relationship('Vendor', back_populates='clothe_types') 
