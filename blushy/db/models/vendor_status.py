from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from blushy.db.models import Base
from sqlalchemy import inspect

class VendorStatus(Base):
    __tablename__ = 'vendor_statuses'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    vendor_id = Column(Integer, ForeignKey('vendors.id')) 
    vendor = relationship('Vendor', back_populates='vendor_statuses')
    items = relationship('Item', back_populates='vendor_status')

