from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from blushy.db.models import Base
from sqlalchemy import inspect



class MasterClotheType(Base):
    __tablename__ = 'master_clothe_types'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    name_tr = Column(String(100), unique=True, nullable=False)
    name_for_ai = Column(String(100), unique=True, nullable=False)

    item_order=Column(Integer, nullable=False,default=0)

    google_clothe_types = relationship('GoogleClotheType', back_populates='master_clothe_type')
    clothe_types = relationship('ClotheType', back_populates='master_clothe_type')
    ai_clothe_types = relationship('AIClotheType', back_populates='master_clothe_type')

    sub_clothe_types = relationship('MasterSubClotheType', back_populates='master_clothe_type')
    labels= relationship('Label', back_populates='master_clothe_type')       
    image_labels= relationship('ImageLabel', back_populates='master_clothe_type')

