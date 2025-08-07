#  app/api/routes_note.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from app.models.note import Note
from app.models.note_bubble import NoteBubble
from app.schemas.note import NoteCreate, NoteOut, NoteUpdate, NoteBubbleOut, NoteBubbleCreate, NoteBubbleUpdate
from app.db.session import SessionLocal
from app.auth.jwt_handler import decode_token
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from datetime import datetime


router = APIRouter()
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
#     payload = decode_token(token)
#     return int(payload["sub"])


security = HTTPBearer()

def get_current_user_id(token: HTTPAuthorizationCredentials = Depends(security)) -> int:
    payload = decode_token(token.credentials)  # token.credentials gives just the token string
    return int(payload["sub"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------------
# Note Routes
# -------------------------------

@router.post("/notes", response_model=NoteOut)
def create_note(note_data: NoteCreate, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    note = Note(
        title=note_data.title,
        note_type=note_data.note_type,
        preview=note_data.preview,
        actions=note_data.actions,
        user_id=user_id
    )
    db.add(note)
    db.commit()
    db.refresh(note)

    # Add NoteBubbles
    for bubble in note_data.bubbles:
        note_bubble = NoteBubble(**bubble.model_dump(), note_id=note.id)
        db.add(note_bubble)
    db.commit()
    db.refresh(note)

    return note


@router.get("/notes", response_model=List[NoteOut])
def get_notes(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    return db.query(Note).filter(Note.user_id == user_id).all()


@router.get("/notes/paginated", response_model=Dict[str, Any])
def get_paginated_notes(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    offset = (page - 1) * limit

    total_notes = db.query(func.count(Note.id)).filter(Note.user_id == user_id).scalar()
    notes = (
        db.query(Note)
        .filter(Note.user_id == user_id)
        .order_by(Note.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    has_more = (page * limit) < total_notes

    return {
        "notes": [NoteOut.model_validate(note) for note in notes],
        "page": page,
        "hasMore": has_more,
        "total": total_notes
    }
    


@router.get("/notes/{note_id}", response_model=NoteOut)
def get_note(note_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/notes/{note_id}", response_model=NoteOut)
def update_note(note_id: int, note_data: NoteUpdate, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    for key, value in note_data.dict(exclude_unset=True).items():
        setattr(note, key, value)

    db.commit()
    db.refresh(note)
    return note

@router.delete("/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return {"message": "Note deleted"}



# -------------------------------
# NoteBubble Routes
# -------------------------------

@router.post("/notes/{note_id}/bubbles", response_model=NoteBubbleOut)
def add_note_bubble(note_id: int, bubble: NoteBubbleCreate, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    note_bubble = NoteBubble(**bubble.model_dump(exclude={"timestamp"}), note_id=note.id,timestamp=datetime.utcnow())
    
    db.add(note_bubble)
    db.commit()
    db.refresh(note_bubble)
    return note_bubble

@router.put("/bubbles/{bubble_id}", response_model=NoteBubbleOut)
def update_bubble(bubble_id: int, bubble_data: NoteBubbleUpdate, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    bubble = db.query(NoteBubble).join(Note).filter(NoteBubble.id == bubble_id, Note.user_id == user_id).first()
    if not bubble:
        raise HTTPException(status_code=404, detail="NoteBubble not found")

    for field, value in bubble_data.model_dump(exclude_unset=True).items():
        setattr(bubble, field, value)
    db.commit()
    db.refresh(bubble)
    return bubble

@router.delete("/bubbles/{bubble_id}")
def delete_bubble(bubble_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    bubble = db.query(NoteBubble).join(Note).filter(NoteBubble.id == bubble_id, Note.user_id == user_id).first()
    if not bubble:
        raise HTTPException(status_code=404, detail="NoteBubble not found")
    db.delete(bubble)
    db.commit()
    return {"message": "NoteBubble deleted"}