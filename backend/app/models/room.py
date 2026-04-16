from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

def generate_room_slug() -> str:
    """Generate a short readable room ID like 'drv-8f2a'."""
    raw = uuid.uuid4().hex
    return f"{raw[:3]}-{raw[3:7]}"

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False, default=generate_room_slug)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    host_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)

    host = relationship("User", back_populates="rooms")


    
    
