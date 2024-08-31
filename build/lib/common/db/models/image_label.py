from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text
from sqlalchemy.orm import relationship
from datetime import datetime
from common.db.models import Base
from sqlalchemy import inspect

class ImageLabel(Base):
    __tablename__ = 'image_labels'
    id = Column(Integer, primary_key=True) 
    image_id = Column(Integer, ForeignKey('images.id'), nullable=False,index=True)
    image=relationship('ItemImage', back_populates='labels')
    object_score = Column(Float,  nullable=False)
    ai_clothe_type_id= Column(Integer, ForeignKey('ai_clothe_types.id'), nullable=True,index=True)
    ai_clothe_type=relationship('AIClotheType', back_populates='image_labels')
    master_clothe_type_id = Column(Integer, ForeignKey('master_clothe_types.id'), nullable=True,index=True)
    master_clothe_type=relationship('MasterClotheType', back_populates='image_labels')
    description = Column(String(1500), nullable=True)  # Store as JSON string in a TEXT field

    master_color_id = Column(Integer, ForeignKey('master_colors.id'), nullable=False,index=True)
    master_color=relationship('MasterColor', back_populates='image_labels')

    master_style_id = Column(Integer, ForeignKey('master_styles.id'), nullable=False,index=True)
    master_style = relationship('MasterStyle', back_populates='image_labels')
    text_embedding = Column(Text, nullable=True)  # Store as JSON string in a TEXT field    


    caption=Column(String(100), nullable=False)

    x1 = Column(Float)
    y1 = Column(Float)
    x2 = Column(Float)
    y2 = Column(Float)
    
    x3 = Column(Float)
    y3 = Column(Float)
    x4 = Column(Float)
    y4 = Column(Float)


    def bbox(self):
        return f"{max(self.x1,0)},{max(self.y1,0)},{self.x2},{self.y2},{self.x3},{self.y3},{self.x4},{self.y4}"
    
    def to_dict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}