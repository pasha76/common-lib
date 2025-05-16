from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from blushy.db.models import Base
from sqlalchemy import inspect
    
class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False,index=True)
    user=relationship('User', back_populates='posts')
    instagram_post_url = Column(String(500), unique=False, nullable=True)
    instagram_post_id = Column(String(50), unique=True, nullable=True, index=True)
    public_image_url = Column('public_image_url', String(500), nullable=True) 
    description = Column(String(5000), nullable=True)
    image_embedding = Column(Text, nullable=True)  
    master_gender_id = Column(Integer, ForeignKey('master_genders.id'))  # Correct ForeignKey
    master_gender = relationship('MasterGender', back_populates='posts')
    like_count = Column(Integer,  nullable=True,default=0)
    visit_count = Column(Integer,  nullable=True,default=0)
    sales_count = Column(Integer,  nullable=True,default=0)
    click_count = Column(Integer,  nullable=True,default=0)
    been_trendy=Column(Boolean(), nullable=True,default=False)
    labels=relationship('Label', back_populates='post')
    post_status_id = Column(Integer,ForeignKey('post_statuses.id'), nullable=False,index=True)
    post_status=relationship('PostStatus', back_populates='posts')
    saved_posts=relationship('SavedPost', back_populates='post')
    sold_items=relationship('SoldItem', back_populates='post')
    seen_posts=relationship('SeenPost', back_populates='post')
    favorited_posts=relationship('FavoritedPost', back_populates='post')
    trendy_week_start=Column(DateTime)
    trendy_week_end =Column(DateTime)
    clicked_items = relationship('ClickedItem', back_populates='post')
    visited_posts = relationship('VisitPost', back_populates='post')  
    comments=relationship('Comment', back_populates='post')  
    caches=relationship('Cache', back_populates='post')
    created_at = Column(DateTime, default=datetime.utcnow)
    complaints=relationship('Complaint', back_populates='post')
   

    def to_dict(self,ignore_keys=[]):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs if c.key not in ignore_keys}