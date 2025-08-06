from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

#-------------------------- 
# NoteBubble Schemas
#--------------------------


class NoteBubbleBase(BaseModel):
    note_bubble_type: str
    content: Optional[str] = None
    audio_path: Optional[str] = None
    timestamp: Optional[datetime] = None
    owner: str = "USER"
    is_edited: bool = False

class NoteBubbleCreate(NoteBubbleBase): pass


class NoteBubbleUpdate(BaseModel):
    content: Optional[str]
    audio_path: Optional[str]
    is_edited: Optional[bool] = True

class NoteBubbleOut(NoteBubbleBase):
    id: int
    class Config:
        from_attributes = True


#-------------------------- 
# Note Schemas
#--------------------------


class NoteBase(BaseModel):
    title: str
    note_type: str
    preview: Optional[str] = None
    actions: Optional[List[str]] = []
    timestamp: Optional[datetime] = None

class NoteCreate(NoteBase):
    bubbles: List[NoteBubbleCreate]=[]


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    preview: Optional[str] = None
    actions: Optional[List[str]] = []


class NoteOut(NoteBase):
    id: int
    timestamp: datetime
    bubbles: List[NoteBubbleOut]=[]

    class Config:
        from_attributes = True
