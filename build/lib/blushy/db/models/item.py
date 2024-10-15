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
import enum
from blushy.utils.base import url_to_pil_image,serialize_embedding
import json
from sqlalchemy import Table, Column, Integer, ForeignKey
from blushy.db.models.items_colors import item_color_association

class ItemStatus(enum.Enum):
    DOWNLOADED = 1
    UPLOADED_TO_STORAGE = 2
    TITLE_CLASSIFIED=3
    ENCODED_IMAGE = 4
    CREATED_IMAGE_DESCRIPTION = 5
    ENCODED_DESCRIPTION = 6
    UPLOADED_TO_VECTORDB = 7
    READY = 8
    EXPIRED = 9
    EXCEPTION_NOT_LABELED = 10
    EXCEPTION_TITLE_CLASSIFIED=11
    EXCEPTION_ENCODED_DESCRIPTION=12
    EXCEPTION_UPLOADED_TO_STORAGE=13
    EXCEPTION_VECTORDB=14

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    url = Column(String(1000), nullable=False)
    image_url = Column("image_url",String(1000), nullable=False)
    title = Column(String(500),nullable=False)
    price = Column(Float,nullable=False)
    sale_price = Column(Float,nullable=True)
    item_id=Column(String(100),nullable=False,index=True)
    link = Column(String(800),nullable=False)
    image_hash=Column(String(64),nullable=True,unique=True)
    item_hash = Column(String(64), nullable=False, unique=True)
    blushy_clothe_type = Column(String(100), nullable=True, unique=False)

    master_gender_id = Column(Integer, ForeignKey('master_genders.id')) 
    master_gender = relationship('MasterGender', back_populates='items')

    master_color_id = Column(Integer, ForeignKey('master_colors.id'))
    master_color = relationship("MasterColor", back_populates="items")

    colors = relationship("MasterColor", secondary=item_color_association, back_populates="items")


    ai_clothe_type_id = Column(Integer, ForeignKey('ai_clothe_types.id'))
    ai_clothe_type = relationship('AIClotheType', back_populates='items')

    master_style_id = Column(Integer, ForeignKey('master_styles.id'))
    master_style = relationship('MasterStyle', back_populates='items')

    vendor_id = Column(Integer, ForeignKey('vendors.id')) 
    vendor = relationship('Vendor', back_populates='items')
    sold_items = relationship('SoldItem', back_populates='item')
    clicked_items = relationship('ClickedItem', back_populates='item')


    image_description = Column(Text, nullable=True)
    image_embedding = Column(Text, nullable=True)   
    text_embedding = Column(Text, nullable=True)   
    created_at = Column(DateTime, default=datetime.utcnow)

    _master_status_id = Column('master_status_id', Integer, ForeignKey('master_statuses.id'))
    master_status = relationship('MasterStatus', back_populates='items')

    @hybrid_property
    def master_status_id(self):
        return self._master_status_id

    @master_status_id.setter
    def master_status_id(self, value):
        if self._validate_item_data(value):
            if isinstance(value, ItemStatus):
                self._master_status_id = value.value
            elif isinstance(value, int) and value in [status.value for status in ItemStatus]:
                self._master_status_id = value
            else:
                raise ValueError("Invalid status value")
        else:
            raise ValueError("Item data validation failed")


    def _validate_item_data(self,value):
        match value:
            case ItemStatus.DOWNLOADED:
                print(self.title , self.price , self.item_id , self.link , self.master_gender_id , self.vendor_id )
                return self.title and self.price > 0 and self.item_id and self.link and self.master_gender_id is not None and self.vendor_id is not None
            
            case ItemStatus.UPLOADED_TO_STORAGE:
                if self._master_status_id != ItemStatus.DOWNLOADED.value:
                    return False
                if self.url is None:
                    return False
                return True

            case ItemStatus.EXCEPTION_UPLOADED_TO_STORAGE:
                if self._master_status_id != ItemStatus.DOWNLOADED.value:
                    return False
                return True


            case ItemStatus.ENCODED_IMAGE:
                if self.master_status_id != ItemStatus.UPLOADED_TO_STORAGE.value:
                    return False
              
                if self.image_embedding is None:
                    return False
                return self.title and self.price > 0 and self.item_id and self.link

            case ItemStatus.TITLE_CLASSIFIED:
                if self.master_status_id != ItemStatus.CREATED_IMAGE_DESCRIPTION.value:
                    return False
                return self.title and self.price > 0 and self.item_id and self.link and self.ai_clothe_type_id and self.image_description and self.blushy_clothe_type
            
            case ItemStatus.EXCEPTION_TITLE_CLASSIFIED:
                if self.master_status_id != ItemStatus.CREATED_IMAGE_DESCRIPTION.value:
                    return False
                return self.title and self.price > 0 and self.item_id and self.link and self.image_embedding


            case ItemStatus.CREATED_IMAGE_DESCRIPTION:
                if self.master_status_id != ItemStatus.ENCODED_IMAGE.value:
                    return False
                
                if self.blushy_clothe_type is None:
                    return False
                
                return self.title and self.price > 0 and self.item_id and self.link
            
            case ItemStatus.EXCEPTION_NOT_LABELED:
                if self.master_status_id != ItemStatus.ENCODED_IMAGE.value:
                    return False
                
                return self.title and self.price > 0 and self.item_id and self.link
            

            case ItemStatus.ENCODED_DESCRIPTION:
            
                if self.master_status_id != ItemStatus.TITLE_CLASSIFIED.value:
                    return False
                
                if self.text_embedding is None:
                    return False
                return self.title and self.price > 0 and self.item_id and self.link and self.ai_clothe_type_id and self.image_description and self.blushy_clothe_type and self.text_embedding

            case ItemStatus.EXCEPTION_ENCODED_DESCRIPTION:
            
                if self.master_status_id != ItemStatus.TITLE_CLASSIFIED.value:
                    return False
                
                return self.title and self.price > 0 and self.item_id and self.link and self.ai_clothe_type_id and self.image_description and self.blushy_clothe_type


            case ItemStatus.UPLOADED_TO_VECTORDB:
                if self.master_status_id != ItemStatus.ENCODED_DESCRIPTION.value:
                    return False
            
                return (self.title and 
                        self.price > 0 and
                          self.item_id and 
                          self.link and 
                          self.ai_clothe_type_id and 
                          self.image_description and 
                          self.blushy_clothe_type and 
                          self.text_embedding)
            
            case ItemStatus.EXCEPTION_VECTORDB:
                if self.master_status_id != ItemStatus.ENCODED_DESCRIPTION.value:
                    return False
            
                return (self.title and 
                        self.price > 0 and
                          self.item_id and 
                          self.link and 
                          self.ai_clothe_type_id and 
                          self.image_description and 
                          self.blushy_clothe_type and 
                          self.text_embedding)


            case ItemStatus.READY:
                if self.master_status_id != ItemStatus.UPLOADED_TO_VECTORDB.value:
                    return False
                with self as image:
                    if image.description is None:
                        return False
                    if image.text_embedding is None:
                        return False
                    if image.image_embedding is None:
                        return False
                    
                return self.title and self.price > 0 and self.item_id and self.link

            case ItemStatus.EXPIRED:
                if self.master_status_id != ItemStatus.UPLOADED_TO_VECTORDB.value:
                    return False
                return True
    
    def upload_to_vector_db(self,vector_db):
        ids=[]
        metadatas=[]
        vectors=[]
        metadata = {
            "item_hash":self.item_hash,
            "price":self.price,
            "sale_price":self.sale_price,
            "vendor_id":self.vendor_id,
            "vendor_name":self.vendor.name,
            "vendor_link":self.vendor.logo,
            "master_gender_id":self.master_gender_id,
            "country_id":self.vendor.country_id,
            "master_color_id":self.master_color_id,
            "master_style_id":self.master_style_id,
            "image_url":self.image_url,
            "item_url":self.link,
            "master_gender_id":self.master_gender_id,
            "master_clothe_type_id":self.ai_clothe_type.master_clothe_type_id,
            "image_embedding":self.image_embedding,
        }
        ids.append(self.id)
        metadatas.append(metadata)
        vectors.append(json.loads(self.text_embedding))
        vector_db.upsert_vectors(ids,vectors,metadatas)

    def expire(self,vector_db):
        vector_db.delete_by_id(self.id)
        
    
    def to_dict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}



    def encode_image(self,siglip_manager:SiglipManager):
        encoded_image=siglip_manager.encode_image(self.image_url)
        return encoded_image
        
    def generate_description(self,labeler:Labeler):
        descriptions=labeler.label(self.image_url)
        
        return descriptions

    def encode_description(self,text_encoder:TextSimilarity):
        encoded_description=text_encoder.encode_text(self.image_description)
        self.text_embedding=encoded_description
        return encoded_description

    def upload_to_gcs(self,gcs_manager:GCSUploader):
        image=url_to_pil_image(self.url)
        image_url=gcs_manager.upload_image(image)
        self.image_url=image_url
        return image_url
        

    @staticmethod
    def list_all_downloaded_items(session):
        return session.query(Item).filter(Item._master_status_id == ItemStatus.DOWNLOADED.value,
                                          Item.url.isnot(None)).all()
    
    @staticmethod
    def list_all_uploaded_items(session):
        return session.query(Item).filter(Item._master_status_id == ItemStatus.UPLOADED_TO_STORAGE.value,
                                          Item.image_url.isnot(None)).all()
    
    @staticmethod
    def list_all_encoded_items(session):
        return session.query(Item).filter(Item._master_status_id == ItemStatus.ENCODED_IMAGE.value,
                                          Item.image_embedding.isnot(None)).all()
    
    @staticmethod
    def list_all_labeled_items(session):
        return session.query(Item).filter(Item._master_status_id == ItemStatus.CREATED_IMAGE_DESCRIPTION.value,
                                          Item.blushy_clothe_type.isnot(None)).all()


    @staticmethod
    def list_all_classified_title_items(session):
        return session.query(Item).filter(Item._master_status_id == ItemStatus.TITLE_CLASSIFIED.value,
                                          Item.ai_clothe_type_id.isnot(None),
                                          Item.image_description.isnot(None)).all()

        
    @staticmethod
    def list_all_encoded_description_items(session):
        return session.query(Item).filter((Item._master_status_id == ItemStatus.ENCODED_DESCRIPTION.value),
                                          Item.ai_clothe_type_id.isnot(None),
                                          Item.text_embedding.isnot(None),
                                          #Item.vendor_id==3,
                                          Item.blushy_clothe_type.isnot(None),
                                          Item.image_description.isnot(None)).all()
                                          
                                          #Item._master_status_id == ItemStatus.ENCODED_DESCRIPTION.value)