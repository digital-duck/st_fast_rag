import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import AsyncGenerator, Literal, List, Optional
from sqlalchemy.orm import Session
from concurrent.futures import ThreadPoolExecutor
import asyncio # Import asyncio

# Local imports from our backend modules
from llm_abstraction import get_llm, LLM_MODELS
from rag_core import get_llm_chain # This will be our simple LLM chain for now
from database import get_db, SessionLocal
from crud import (
    ChatMessageCreate, ChatMessageResponse,
    NoteCreate, NoteResponse, NoteUpdate,
    create_chat_message, get_chat_history,
    create_note, get_note, get_notes, update_note, delete_note
)

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="st_fast_rag Backend API",
    description="FastAPI backend for RAG application with LLM abstraction, streaming, and database persistence.",
    version="0.1.0",
)

# Configuration from environment variables
BACKEND_HOST = os.getenv("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", 8000))

# Thread pool for synchronous database operations in async context
executor = ThreadPoolExecutor(max_workers=1) # Adjust max_workers as needed
# set max_workers to 1 because SQLite has limited concurrency support
# For more robust DBs like PostgreSQL, you can increase this.


# Define request body model for the API endpoint
class GenerateRequest(BaseModel):
    question: str
    llm_provider: Literal["claude", "openai", "gemini"]
    llm_model: str
    temperature: float = 0.3
    max_tokens: int = 1024
    session_id: str # To associate with chat history
    rag_enabled: bool = False # Placeholder for future RAG context
    # Potentially add other RAG specific params here

@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "message": "Backend is running!"}

@app.post("/generate_stream")
async def generate_stream(request: GenerateRequest, db: Session = Depends(get_db)):
    """
    API endpoint to generate an LLM response with streaming.
    It uses the LLM abstraction layer to get the appropriate model.
    Also persists user query and LLM response to chat history.
    """
    try:
        # Save user message to database
        user_message_data = ChatMessageCreate(
            session_id=request.session_id,
            role="user",
            message=request.question,
            llm_provider=request.llm_provider,
            llm_model=request.llm_model
        )
        # Use executor for synchronous DB operation in async endpoint
        await asyncio.get_running_loop().run_in_executor(executor, create_chat_message, db, user_message_data)

        # Get the LLM instance via our abstraction layer
        llm = get_llm(
            provider=request.llm_provider,
            model_name=request.llm_model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            streaming=True # Ensure streaming is enabled for this endpoint
        )

        # Get the LangChain chain (currently just LLM direct call, but extensible to RAG)
        chain = get_llm_chain(llm)

        # TODO: In future, if rag_enabled, fetch context from notes/chat_history
        # and modify the chain to include context.

        assistant_response_full = "" # To store the complete response for saving

        async def generate_response_chunks() -> AsyncGenerator[str, None]:
            """Async generator to yield LLM response chunks."""
            nonlocal assistant_response_full
            # `astream` returns an async generator that yields chunks
            async for chunk in chain.astream({"question": request.question}):
                assistant_response_full += chunk
                yield chunk

            # After streaming is complete, save the assistant's full response
            assistant_message_data = ChatMessageCreate(
                session_id=request.session_id,
                role="assistant",
                message=assistant_response_full,
                llm_provider=request.llm_provider,
                llm_model=request.llm_model
            )
            await asyncio.get_running_loop().run_in_executor(executor, create_chat_message, db, assistant_message_data)


        # Return a StreamingResponse
        return StreamingResponse(generate_response_chunks(), media_type="text/plain")

    except ValueError as ve:
        # Catch errors from get_llm (e.g., missing API key, unsupported provider)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# --- chat_history Endpoints ---

@app.get("/chat_history/{session_id}", response_model=List[ChatMessageResponse])
async def get_session_chat_history(session_id: str, db: Session = Depends(get_db)):
    """Retrieves chat history for a given session ID."""
    history = await asyncio.get_running_loop().run_in_executor(executor, get_chat_history, db, session_id)
    return history

@app.post("/chat_history/", response_model=ChatMessageResponse)
async def create_new_chat_message(message: ChatMessageCreate, db: Session = Depends(get_db)):
    """Creates a new chat message record."""
    db_message = await asyncio.get_running_loop().run_in_executor(executor, create_chat_message, db, message)
    return db_message

# --- Notes Endpoints ---

@app.get("/notes/", response_model=List[NoteResponse])
async def read_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieves all notes."""
    notes = await asyncio.get_running_loop().run_in_executor(executor, get_notes, db, skip, limit)
    return notes

@app.get("/notes/{note_id}", response_model=NoteResponse)
async def read_note(note_id: int, db: Session = Depends(get_db)):
    """Retrieves a single note by ID."""
    db_note = await asyncio.get_running_loop().run_in_executor(executor, get_note, db, note_id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return db_note

@app.post("/notes/", response_model=NoteResponse)
async def create_new_note(note: NoteCreate, db: Session = Depends(get_db)):
    """Creates a new note."""
    db_note = await asyncio.get_running_loop().run_in_executor(executor, create_note, db, note)
    return db_note

@app.put("/notes/{note_id}", response_model=NoteResponse)
async def update_existing_note(note_id: int, note: NoteUpdate, db: Session = Depends(get_db)):
    """Updates an existing note."""
    db_note = await asyncio.get_running_loop().run_in_executor(executor, update_note, db, note_id, note)
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return db_note

@app.delete("/notes/{note_id}", response_model=NoteResponse)
async def delete_existing_note(note_id: int, db: Session = Depends(get_db)):
    """Deletes a note by ID."""
    db_note = await asyncio.get_running_loop().run_in_executor(executor, delete_note, db, note_id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return db_note

