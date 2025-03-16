from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Banner(Base):
    __tablename__ = 'banners'

    id = Column(Integer, primary_key=True)
    asset_url = Column(String, nullable=False)
    description = Column(String)
    expire_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Banner(id={self.id}, description={self.description}, expire_at={self.expire_at})>"