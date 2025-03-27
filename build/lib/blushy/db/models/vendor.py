from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Text
from sqlalchemy.orm import relationship
from datetime import datetime
from blushy.db.models import Base



class Vendor(Base):
    __tablename__ = 'vendors'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    name = Column(String(100))
    address = Column(String(500))
    logo = Column(String(500))
    country_id = Column(Integer, ForeignKey('countries.id'))
    country = relationship('Country', back_populates='vendors')
    items = relationship('Item', back_populates='vendor')
    users = relationship('User', back_populates='vendor')
    product_feed_url = Column(String(1000))
    product_feed_last_updated = Column(DateTime)
    product_mapping=Column(Text)
    vendor_statuses = relationship('VendorStatus', back_populates='vendor')  


    created_at = Column(DateTime, default=datetime.utcnow)


