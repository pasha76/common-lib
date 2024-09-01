from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from blushy.db.models import Base
from sqlalchemy import inspect


class FavoritedPost(Base):
    __tablename__ = 'favorited_posts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False,index=True)
    user=relationship('User', back_populates='favorited_posts')
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False,index=True)
    post=relationship('Post', back_populates='favorited_posts')
    created_at = Column(DateTime, default=datetime.utcnow)

class SavedPost(Base):
    __tablename__ = 'saved_posts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False,index=True)
    user=relationship('User', back_populates='saved_posts')
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False,index=True)
    post=relationship('Post', back_populates='saved_posts')
    created_at = Column(DateTime, default=datetime.utcnow) 
    

class PostStatus(Base):
    __tablename__ = 'post_statuses'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), unique=True, nullable=False)
    posts = relationship('Post', back_populates='post_status')
    
class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False,index=True)
    user=relationship('User', back_populates='posts')
    instagram_post_url = Column(String(500), unique=False, nullable=True)
    enhanced_image_url = Column(String(500), unique=False, nullable=True)
    instagram_post_id = Column(String(50), unique=True, nullable=True, index=True)
    _public_image_url = Column('public_image_url', String(500), nullable=True) 
    no_bg_public_image_url = Column(String(500), nullable=True) 
    description = Column(String(5000), nullable=True)
    quality_score = Column(Float,  nullable=False)
    similarity_score = Column(Float,  nullable=False)
    image_embedding = Column(Text, nullable=True)  
    master_gender_id = Column(Integer, ForeignKey('master_genders.id'))  # Correct ForeignKey
    master_gender = relationship('MasterGender', back_populates='posts')
    post_scope=Column(Integer, nullable=True)
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
    created_at = Column(DateTime, default=datetime.utcnow)
