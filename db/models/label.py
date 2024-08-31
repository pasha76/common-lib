
from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from common.db.models import Base
from sqlalchemy import inspect


class Label(Base):
    
    __tablename__ = 'labels'
    id = Column(Integer, primary_key=True) 
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False,index=True)
    post=relationship('Post', back_populates='labels')
    similarity_score = Column(Float,  nullable=False)
    image_url = Column(String,  nullable=True)
    enhanced_image_url = Column(String,  nullable=True)
    object_score = Column(Float,  nullable=False)
    master_clothe_type_id = Column(Integer, ForeignKey('master_clothe_types.id'), nullable=False,index=True)
    master_clothe_type=relationship('MasterClotheType', back_populates='labels')

    ai_clothe_type_id = Column(Integer, ForeignKey('ai_clothe_types.id'), nullable=False,index=True)
    ai_clothe_type=relationship('AIClotheType', back_populates='post_labels')

    master_color_id = Column(Integer, ForeignKey('master_colors.id'), nullable=False,index=True)
    master_color=relationship('MasterColor', back_populates='labels')

    master_style_id = Column(Integer, ForeignKey('master_styles.id'), nullable=False,index=True)
    master_style = relationship('MasterStyle', back_populates='post_labels')

    color_score = Column(Float,  nullable=False)
    embedding = Column(Text, nullable=True)  # Store as JSON string in a TEXT field
    text_embedding = Column(Text, nullable=True)  # Store as JSON string in a TEXT field
    description = Column(Text, nullable=True)  # Store as JSON string in a TEXT field


    x1 = Column(Integer)
    y1 = Column(Integer)
    x2 = Column(Integer)
    y2 = Column(Integer)
    
    x3 = Column(Integer)
    y3 = Column(Integer)
    x4 = Column(Integer)
    y4 = Column(Integer)

    

    def bbox(self):
        return f"{self.x1},{self.y1},{self.x2},{self.y2},{self.x3},{self.y3},{self.x4},{self.y4}"

    def to_dict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}