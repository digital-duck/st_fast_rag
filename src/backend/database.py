import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# Load environment variables from .env file (if not already loaded)
load_dotenv()

# Get the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fast_rag.sqlite3")

# Create a SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}) # check_same_thread=False for SQLite with FastAPI

# Declare a base class for declarative models
Base = declarative_base()

# Define the ChatHistory model
class ChatHistory(Base):
    """
    SQLAlchemy model for storing chat conversation history.
    """
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False) # To group conversations
    timestamp = Column(DateTime, default=func.now())
    role = Column(String, nullable=False) # "user" or "assistant"
    message = Column(Text, nullable=False)
    llm_provider = Column(String, nullable=False)
    llm_model = Column(String, nullable=False)

    def __repr__(self):
        return f"<ChatHistory(id={self.id}, session_id='{self.session_id}', role='{self.role}', message='{self.message[:50]}...')>"

# Define the Note model
class Note(Base):
    """
    SQLAlchemy model for storing user notes.
    """
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=func.now())
    title = Column(String, index=True, nullable=False)
    url = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    comments = Column(Text, nullable=False)
    tags = Column(Text, nullable=False)

    def __repr__(self):
        return f"""
        <Note(id={self.id}, title='{self.title}', url='{self.url}', content='{self.content[:50]}...', comments='{self.comments[:50]}...', tags='{self.tags}')>
        """

# Create a SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get a database session for FastAPI
def get_db():
    """
    Dependency function to provide a database session to FastAPI routes.
    Ensures the session is closed after the request is processed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create all tables in the database
def create_db_tables():
    """
    Creates all defined database tables.
    This function should be called once when setting up the application.
    """
    print(f"Attempting to create database tables at {DATABASE_URL}...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created (if they didn't exist).")

if __name__ == "__main__":
    # This block will run when you execute `python backend/database.py`
    create_db_tables()
