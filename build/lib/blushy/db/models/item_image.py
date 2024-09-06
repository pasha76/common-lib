from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text
from sqlalchemy.orm import relationship
from datetime import datetime
from blushy.db.models import Base
from sqlalchemy import inspect
from sqlalchemy.ext.hybrid import hybrid_property
from blushy.utils.siglip_manager import SiglipManager
from blushy.utils.labeler import Labeler
from blushy.utils.text_similarity_manager import TextSimilarity
from blushy.utils.gcs import GCSUploader

class ItemImage(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    url = Column(String(1000), nullable=False)
    image_url = Column("image_url",String(1000), nullable=True)
    item_id = Column(Integer, ForeignKey('items.id'))
    item = relationship('Item', back_populates='images')

    master_color_id = Column(Integer, ForeignKey('master_colors.id'))
    master_color = relationship('MasterColor', back_populates='master_colors')

    ai_clothe_type_id = Column(Integer, ForeignKey('ai_clothe_types.id'))
    ai_clothe_type = relationship('AIClotheType', back_populates='ai_clothe_types')

    master_style_id = Column(Integer, ForeignKey('master_styles.id'))
    master_style = relationship('MasterStyle', back_populates='master_styles')

    description = Column(Text, nullable=True)
    image_embedding = Column(Text, nullable=True)   
    text_embedding = Column(Text, nullable=True)   
    created_at = Column(DateTime, default=datetime.utcnow)

    def encode_image(self,siglip_manager:SiglipManager):
        encoded_image=siglip_manager.encode_image(self.image_url)
        self.image_embedding=encoded_image
        
    def generate_description(self,labeler:Labeler):
        item_clothe_type_name=self.item.ai_clothe_type.name
        description=laberer.label_the_clothe_type(self.image_url,item_clothe_type_name)
        self.description=description

    def encode_description(self,text_encoder:TextSimilarity):
        encoded_description=text_encoder.encode_text(self.description)
        self.text_embedding=encoded_description

    def upload_to_gcs(self,gcs_manager:GCSUploader):
        image_url=gcs_manager.upload_image(self.url)
        self.image_url=image_url
        


