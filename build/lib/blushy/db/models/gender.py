from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from blushy.db.models import Base
from sqlalchemy import inspect

class Gender(Base):
    __tablename__ = 'genders'
    id = Column(Integer, primary_key=True)
    title = Column(String(10), unique=False, nullable=False)
    
    items = relationship('Item', back_populates='gender')
    
    vendor_id = Column(Integer, ForeignKey('vendors.id')) 
    vendor = relationship('Vendor', back_populates='genders')
    
    master_gender_id = Column(Integer, ForeignKey('master_genders.id')) 
    master_genders = relationship('MasterGender', back_populates='genders')
    