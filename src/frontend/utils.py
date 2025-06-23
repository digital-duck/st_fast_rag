import streamlit as st
import httpx # For making async HTTP requests
import asyncio
import os
import uuid
from datetime import datetime
from typing import AsyncGenerator, List, Dict, Any, Optional

# --- Configuration ---
# Load environment variables (important for backend URL)
from dotenv import load_dotenv
load_dotenv()

BACKEND_HOST = os.getenv("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = os.getenv("BACKEND_PORT", "8000")
API_BASE_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"

# --- Session State Management for LLM Configuration ---
def initialize_llm_config_session_state():
    """Initializes LLM configuration in Streamlit session state."""
    if "llm_provider" not in st.session_state:
        st.session_state.llm_provider = "gemini"
    if "llm_model" not in st.session_state:
        st.session_state.llm_model = "gemini-2.5-flash"
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.3
    if "max_tokens" not in st.session_state:
        st.session_state.max_tokens = 1024
    if "rag_enabled" not in st.session_state:
        st.session_state.rag_enabled = False # Default RAG to disabled

# --- FastAPI Client Utility Functions ---

async def call_generate_stream_api(
    question: str,
    llm_provider: str,
    llm_model: str,
    temperature: float,
    max_tokens: int,
    session_id: str,
    rag_enabled: bool
) -> AsyncGenerator[str, None]:
    """
    Calls the FastAPI backend's /generate_stream endpoint and yields streamed chunks.
    CORRECTED: Using httpx.AsyncClient().stream() method for explicit streaming requests.
    """
    json_payload = {
        "question": question,
        "llm_provider": llm_provider,
        "llm_model": llm_model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "session_id": session_id,
        "rag_enabled": rag_enabled,
    }
    async with httpx.AsyncClient() as client:
        try:
            # Use client.stream() to initiate a streaming request.
            # The first argument is the HTTP method ("POST"), followed by the URL,
            # and then other request parameters like `json` payload.
            async with client.stream(
                "POST", # HTTP method
                f"{API_BASE_URL}/generate_stream", # URL
                json=json_payload, # Request body
                timeout=None # Allow long timeouts for LLM calls
            ) as response:
                response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

                # Stream the response content by iterating over aiter_bytes()
                async for chunk in response.aiter_bytes():
                    yield chunk.decode("utf-8")

        except httpx.HTTPStatusError as e:
            error_text = f"Status code: {e.response.status_code}. Response: "
            try:
                # Ensure the response body is read before accessing .text
                # and to prevent "Attempted to access streaming response content..."
                await e.response.aread()
                error_text += e.response.text
            except Exception as read_exc:
                error_text += f"(Failed to read error response body: {read_exc})"

            st.error(f"Backend HTTP error: {error_text}")
            # Ensure the response is closed/drained on error to prevent resource leaks
            if e.response and not e.response.is_closed:
                await e.response.aclose()
            raise # Re-raise the exception to propagate it to the calling function
        except httpx.RequestError as e:
            st.error(f"Network error communicating with backend: {e}")
            st.info(f"Please ensure the FastAPI backend is running at {API_BASE_URL}")
            raise # Re-raise the exception
        except Exception as e:
            st.error(f"An unexpected error occurred during API call: {e}")
            raise

async def save_chat_message_to_backend(
    session_id: str,
    role: str,
    message: str,
    llm_provider: str,
    llm_model: str
):
    """Saves a chat message to the backend database."""
    json_payload = {
        "session_id": session_id,
        "role": role,
        "message": message,
        "llm_provider": llm_provider,
        "llm_model": llm_model
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{API_BASE_URL}/chat_history/", json=json_payload)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            st.error(f"Failed to save chat message (HTTP Error): {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            st.error(f"Network error saving chat message: {e}")
            raise
        except Exception as e:
            st.error(f"An unexpected error occurred while saving chat message: {e}")
            raise

async def get_chat_history_from_backend(session_id: str) -> List[Dict[str, Any]]:
    """Retrieves chat history for a given session ID from the backend."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/chat_history/{session_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            st.error(f"Failed to retrieve chat history (HTTP Error): {e.response.status_code} - {e.response.text}")
            return []
        except httpx.RequestError as e:
            st.error(f"Network error retrieving chat history: {e}")
            return []
        except Exception as e:
            st.error(f"An unexpected error occurred while retrieving chat history: {e}")
            return []

async def get_notes_from_backend() -> List[Dict[str, Any]]:
    """Retrieves all notes from the backend."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/notes/")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            st.error(f"Failed to retrieve notes (HTTP Error): {e.response.status_code} - {e.response.text}")
            return []
        except httpx.RequestError as e:
            st.error(f"Network error retrieving notes: {e}")
            return []
        except Exception as e:
            st.error(f"An unexpected error occurred while retrieving notes: {e}")
            return []

async def create_note_backend(title: str, content: str) -> Optional[Dict[str, Any]]:
    """Creates a new note via the backend."""
    json_payload = {"title": title, "content": content}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{API_BASE_URL}/notes/", json=json_payload)
            response.raise_for_status()
            st.success("Note created successfully!")
            return response.json()
        except httpx.HTTPStatusError as e:
            st.error(f"Failed to create note (HTTP Error): {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            st.error(f"Network error creating note: {e}")
            return None
        except Exception as e:
            st.error(f"An unexpected error occurred while creating note: {e}")
            return None

async def update_note_backend(note_id: int, title: str, content: str) -> Optional[Dict[str, Any]]:
    """Updates an existing note via the backend."""
    json_payload = {"title": title, "content": content}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(f"{API_BASE_URL}/notes/{note_id}", json=json_payload)
            response.raise_for_status()
            st.success("Note updated successfully!")
            return response.json()
        except httpx.HTTPStatusError as e:
            st.error(f"Failed to update note (HTTP Error): {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            st.error(f"Network error updating note: {e}")
            return None
        except Exception as e:
            st.error(f"An unexpected error occurred while updating note: {e}")
            return None

async def delete_note_backend(note_id: int) -> bool:
    """Deletes a note via the backend."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(f"{API_BASE_URL}/notes/{note_id}")
            response.raise_for_status()
            st.success("Note deleted successfully!")
            return True
        except httpx.HTTPStatusError as e:
            st.error(f"Failed to delete note (HTTP Error): {e.response.status_code} - {e.response.text}")
            return False
        except httpx.RequestError as e:
            st.error(f"Network error deleting note: {e}")
            return False
        except Exception as e:
            st.error(f"An unexpected error occurred while deleting note: {e}")
            return False
