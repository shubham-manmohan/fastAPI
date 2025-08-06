# app/models/note_bubble.py

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class NoteBubble(Base):
    __tablename__ = "note_bubble"
    
    id = Column(Integer, primary_key=True, index=True)
    note_bubble_type = Column(String, nullable=False)  # transcript | audio | text
    content = Column(String, nullable=True)
    audio_path = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    owner = Column(String, default="USER")  # "SYSTEM" or "USER"
    is_edited = Column(Boolean, default=False)

    note_id = Column(Integer, ForeignKey("note.id"))

    note = relationship("Note", back_populates="bubbles")
