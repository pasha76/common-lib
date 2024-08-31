from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from common.db.models import Base
from sqlalchemy import inspect


class Currency(Base):
    __tablename__ = 'currencies'
    id = Column(Integer, primary_key=True)
    code = Column(String(3), unique=True, nullable=False)  # ISO Currency Code
    name = Column(String(20), nullable=False)
    
    country_id = Column(Integer, ForeignKey('countries.id'))
    country = relationship('Country', back_populates='currencies')