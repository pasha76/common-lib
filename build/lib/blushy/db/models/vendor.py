from sqlalchemy import Column, Integer, String, ForeignKey,DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from blushy.db.models import Base



class Vendor(Base):
    __tablename__ = 'vendors'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    title = Column(String(100))
    address = Column(String(500))
    logo = Column(String(500))
    country_id = Column(Integer, ForeignKey('countries.id'))
    country = relationship('Country', back_populates='vendors')
    items = relationship('Item', back_populates='vendor')
    users = relationship('User', back_populates='vendor')
    genders = relationship('Gender', back_populates='vendor') 
    #colors = relationship('Color', back_populates='vendor') 
    clothe_types = relationship('ClotheType', back_populates='vendor') 
    vendor_statuses = relationship('VendorStatus', back_populates='vendor')  
    conditions = relationship('Condition', back_populates='vendor')  
    brands = relationship('Brand', back_populates='vendor') 
    #feed_logs = relationship('FeedLog', back_populates='vendor')  
    created_at = Column(DateTime, default=datetime.utcnow)

class Brand(Base):
    __tablename__ = 'brands'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)  
    items = relationship('Item', back_populates='brand')
    vendor_id = Column(Integer, ForeignKey('vendors.id'), nullable=False)
    vendor = relationship('Vendor', back_populates='brands')
    
    
class Condition(Base):
    __tablename__ = 'conditions'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)  
    items = relationship('Item', back_populates='condition')
    vendor_id = Column(Integer, ForeignKey('vendors.id'), nullable=False)
    vendor = relationship('Vendor', back_populates='conditions')
    
