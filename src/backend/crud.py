from sqlalchemy.orm import Session
from typing import List, Optional

from database import ChatHistory, Note # Import models
from pydantic import BaseModel
import datetime

# --- Pydantic Models for Request/Response (API Schemas) ---

# Chat History Schemas
class ChatMessageBase(BaseModel):
    session_id: str
    role: str # "user" or "assistant"
    message: str
    llm_provider: str
    llm_model: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageResponse(ChatMessageBase):
    id: int
    timestamp: datetime.datetime

    class Config:
        from_attributes = True # or orm_mode = True for Pydantic v1

# Note Schemas
class NoteBase(BaseModel):
    title: str
    content: str

class NoteCreate(NoteBase):
    pass

class NoteUpdate(NoteBase):
    pass # For update, we might allow partial updates later, but for now full update

class NoteResponse(NoteBase):
    id: int
    timestamp: datetime.datetime

    class Config:
        from_attributes = True # or orm_mode = True for Pydantic v1

# --- CRUD Operations for Chat History ---

def create_chat_message(db: Session, message: ChatMessageCreate) -> ChatHistory:
    """Creates a new chat message record in the database."""
    db_message = ChatHistory(**message.dict())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_chat_history(db: Session, session_id: str, skip: int = 0, limit: int = 100) -> List[ChatHistory]:
    """Retrieves chat history for a specific session ID, ordered by timestamp."""
    return db.query(ChatHistory).filter(ChatHistory.session_id == session_id).order_by(ChatHistory.timestamp).offset(skip).limit(limit).all()

# --- CRUD Operations for Notes ---

def create_note(db: Session, note: NoteCreate) -> Note:
    """Creates a new note record in the database."""
    db_note = Note(**note.dict())
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def get_note(db: Session, note_id: int) -> Optional[Note]:
    """Retrieves a single note by its ID."""
    return db.query(Note).filter(Note.id == note_id).first()

def get_notes(db: Session, skip: int = 0, limit: int = 100) -> List[Note]:
    """Retrieves all notes, ordered by timestamp."""
    return db.query(Note).order_by(Note.timestamp.desc()).offset(skip).limit(limit).all()

def update_note(db: Session, note_id: int, note: NoteUpdate) -> Optional[Note]:
    """Updates an existing note."""
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if db_note:
        for var, value in note.dict().items():
            setattr(db_note, var, value)
        db.commit()
        db.refresh(db_note)
    return db_note

def delete_note(db: Session, note_id: int) -> Optional[Note]:
    """Deletes a note by its ID."""
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if db_note:
        db.delete(db_note)
        db.commit()
    return db_note
