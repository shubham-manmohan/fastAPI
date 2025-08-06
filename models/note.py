# app/models/note.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Note(Base):
    __tablename__ = "note"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    note_type = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    preview = Column(String, nullable=True)
    actions = Column(JSON, default=[])  # e.g. ["Pin", "Archived"]
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="notes")
    bubbles = relationship("NoteBubble", back_populates="note", cascade="all, delete")
