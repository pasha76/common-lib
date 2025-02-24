
from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from blushy.db.models import Base
from sqlalchemy import inspect
import json


class Label(Base):
    
    
    __tablename__ = 'labels'
    id = Column(Integer, primary_key=True) 
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False,index=True)
    post=relationship('Post', back_populates='labels')
  
    ai_clothe_type_id = Column(Integer, ForeignKey('ai_clothe_types.id'), nullable=False,index=True)
    ai_clothe_type=relationship('AIClotheType', back_populates='post_labels')

    master_color_id = Column(Integer, ForeignKey('master_colors.id'), nullable=False,index=True)
    master_color=relationship('MasterColor', back_populates='labels')

    master_style_id = Column(Integer, ForeignKey('master_styles.id'), nullable=False,index=True)
    master_style = relationship('MasterStyle', back_populates='post_labels')

    text_embedding = Column(Text, nullable=True)  # Store as JSON string in a TEXT field
    label_info = Column(Text, nullable=True)  # Store as JSON string in a TEXT field
    image_embedding= Column(Text, nullable=True)  # Store as JSON string in a TEXT field
    description = Column(Text, nullable=True)  # Store as JSON string in a TEXT field
    description_tr=Column(Text, nullable=True)


    def upload_to_vector_db(self,vector_db):
        ids=[]
        metadatas=[]
        vectors=[]
        metadata = {
            "post_id":self.post_id,
            "country_id":self.post.user.country_id,
            "master_gender_id":self.post.user.master_gender_id,
            "master_clothe_type_id":self.ai_clothe_type.master_clothe_type_id
        }
        ids.append(self.id)
        metadatas.append(metadata)
        vectors.append(json.loads(self.text_embedding))
        vector_db.upsert_vectors(ids,vectors,metadatas)

 

    def to_dict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}