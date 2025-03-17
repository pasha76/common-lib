from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from blushy.db.models import Base

class Complaint(Base):
    __tablename__ = 'complaints'

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(String(50), nullable=False, default='pending')  # pending, resolved, rejected
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships (optional, add if needed)
    post = relationship("Post", back_populates="complaints")
    user = relationship("User", back_populates="complaints")

    def __repr__(self):
        return f"<Complaint(id={self.id}, post_id={self.post_id}, user_id={self.user_id}, status={self.status})>"