from fastapi import FastAPI
from app.api.routes_user import router as user_router
from app.api.routes_note import router as note_router

from app.db.session import engine
from app.db.base import Base
from app.models import user  
Base.metadata.create_all(bind=engine)
app = FastAPI()
app.include_router(user_router)
app.include_router(note_router, prefix="/api")
