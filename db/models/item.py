from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text
from sqlalchemy.orm import relationship
from datetime import datetime
from common.db.models import Base
from sqlalchemy import inspect

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    title = Column(String(500),nullable=False)
    description = Column(Text(2000))
    price = Column(Float,nullable=False)
    sale_price = Column(Float,nullable=False)
    item_id=Column(Text(50),nullable=False,index=True)
    link = Column(String(500),nullable=False)

    ai_clothe_type_id= Column(Integer, ForeignKey('ai_clothe_types.id'), nullable=True,index=True)
    ai_clothe_type=relationship('AIClotheType', back_populates='items')
    
    clicked_items = relationship('ClickedItem', back_populates='item')
    
    currency_code = Column(String(3), ForeignKey('currencies.code')) 
    
    condition_id = Column(Integer, ForeignKey('conditions.id')) 
    condition = relationship('Condition', back_populates='items')
    
    brand_id = Column(Integer, ForeignKey('brands.id')) 
    brand = relationship('Brand', back_populates='items')
    
    gender_id = Column(Integer, ForeignKey('genders.id')) 
    gender = relationship('Gender', back_populates='items')
    
    #color_id = Column(Integer, ForeignKey('colors.id')) 
    #color = relationship('Color', back_populates='items')
    

    vendor_id = Column(Integer, ForeignKey('vendors.id')) 
    vendor = relationship('Vendor', back_populates='items')


    clothe_type_id = Column(Integer, ForeignKey('clothe_types.id'))
    clothe_type = relationship('ClotheType', back_populates='items')

    images = relationship('ItemImage', back_populates='item')  # Assuming an 'Image' model
    master_status_id = Column(Integer, ForeignKey('master_statuses.id'))
    master_status = relationship('MasterStatus', back_populates='items')

    vendor_status_id = Column(Integer, ForeignKey('vendor_statuses.id'))
    vendor_status = relationship('VendorStatus', back_populates='items')
    sold_items = relationship('SoldItem', back_populates='item')
    created_at = Column(DateTime, default=datetime.utcnow)

    
    
    def to_dict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}
