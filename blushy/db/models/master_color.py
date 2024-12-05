from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from blushy.db.models import Base
from sqlalchemy import inspect
from blushy.db.models.items_colors import item_color_association

class MasterColor(Base):
    __tablename__ = 'master_colors'
    id = Column(Integer, primary_key=True)
    name = Column(String(10), unique=True, nullable=False)

    labels = relationship('Label', back_populates='master_color')
    #items = relationship('Item', back_populates='master_color')
    items = relationship("Item", back_populates="colors")
