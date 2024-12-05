from sqlalchemy import Column, Integer, String, ForeignKey,DateTime,Float,Text,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from common.db.models import Base
from sqlalchemy import inspect


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    device_id = Column(String(300), unique=True, nullable=False)
    username = Column(String(80), unique=True, nullable=True, index=True)
    instagram_id = Column(String(80), unique=True, nullable=True, index=True)
    access_token=Column(String(300), unique=False, nullable=True)
    email = Column(String(120), unique=False, nullable=True)
    password = Column(String(120), unique=False, nullable=True)
    name = Column(String(80), nullable=True)
    is_verified= Column(Boolean(), nullable=True,default=False)
    profile_photo_url = Column(String(1000), nullable=True)
    master_gender_id = Column(Integer, ForeignKey('master_genders.id')) 
    master_gender = relationship('MasterGender', back_populates='users')
    age = Column(Integer, nullable=True)
    fashion_score = Column(Integer, nullable=True)
    birth_year = Column(Integer, nullable=False,default=1990)
    phone = Column(String(20), nullable=True)
    follower_count = Column(Integer,default=0)
    following_count = Column(Integer,default=0)
    country_id = Column(Integer, ForeignKey('countries.id')) 
    country = relationship('Country', back_populates='users')
    user_type_id = Column(Integer, ForeignKey('user_types.id')) 
    user_type = relationship('UserType', back_populates='users')
    visited_posts = relationship('VisitPost', back_populates='user')
    clicked_items = relationship('ClickedItem', back_populates='user')
    sold_items = relationship('SoldItem', back_populates='user')
    seen_posts=relationship('SeenPost', back_populates='user')
    vendor_id = Column(Integer, ForeignKey('vendors.id'),nullable=True) 
    vendor = relationship('Vendor', back_populates='users')

    user_status_id = Column(Integer, ForeignKey('user_statuses.id')) 
    user_status = relationship('UserStatus', back_populates='users')
    posts=relationship('Post', back_populates='user')
    favorited_posts=relationship('FavoritedPost', back_populates='user')
    saved_posts=relationship('SavedPost', back_populates='user')
    created_at = Column(DateTime, default=datetime.utcnow)

    def is_vendor(self):
        return self.vendor_id is not None

    def to_dict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}