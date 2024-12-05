from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text
from sqlalchemy.orm import relationship
from datetime import datetime
from blushy.db.models import Base
from sqlalchemy import inspect

class Country(Base):
    __tablename__ = 'countries'
    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)  
    lang=Column(String(5), nullable=True)
    vendors = relationship('Vendor', back_populates='country')
    currencies = relationship('Currency', back_populates='country')
    users = relationship('User', back_populates='country')

    def to_dict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}