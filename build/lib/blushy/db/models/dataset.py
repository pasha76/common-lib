
from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from blushy.db.models import Base
from sqlalchemy import inspect


class Dataset(Base):
    
    __tablename__ = 'dataset'
    id = Column(Integer, primary_key=True) 
    image_url =Column(String(500),nullable=False)
    image_hash=Column(String(255),nullable=True,unique=True)
    description = Column(Text, nullable=False) 
    full_body_human = Column(Boolean)
    partial_body_human = Column(Boolean)
    no_human = Column(Boolean)
    clothe_wearables = Column(Boolean)
    more_than_one_person = Column(Boolean)
    aesthetic_score = Column(Integer)






    def to_dict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}