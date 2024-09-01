from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text
from sqlalchemy.orm import relationship
from datetime import datetime
from blushy.db.models import Base
from sqlalchemy import inspect
from sqlalchemy.ext.hybrid import hybrid_property

class ItemImage(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    url = Column(String(1000), nullable=False)
    _image_url = Column("image_url",String(1000), nullable=True)

    reference_image_id=Column(Integer,nullable=True,default=0)
    
    item_id = Column(Integer, ForeignKey('items.id'))
    item = relationship('Item', back_populates='images')

    labels=relationship('ImageLabel', back_populates='image')
    
    image_class=Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    embedding = Column(Text, nullable=True)  # Store as JSON string in a TEXT field    



    @hybrid_property
    def image_url(self):
        return self._image_url

    @image_url.setter
    def image_url(self, value):
        if not value.startswith("http"):
            print(value)
            raise ValueError("Invalid URL: URL must start with http")
        self._image_url = value
        #self._generate_image_fashion_embeddings(value)

    """
    def _generate_image_fashion_embeddings(self, url):
        
        classes = {"full body human": 0,
                                "partial body human": 1,
                                "object": 2}
        image_class = embedding_extractor.classify(url, classes)
        self.image_class=image_class
    """

    
    
    
    
    @property
    def uri(self):
        uri="gs://"+self.image_url.replace("https://storage.googleapis.com/","")
        return uri
    