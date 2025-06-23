import streamlit as st
import asyncio
import uuid
import datetime
from frontend.utils import (
    initialize_llm_config_session_state,
    call_generate_stream_api,
    save_chat_message_to_backend,
    get_chat_history_from_backend,
    API_BASE_URL
)

st.set_page_config(page_title="Chat with LLM", layout="wide")

# Initialize LLM configuration (and other session state vars)
initialize_llm_config_session_state()

# Ensure a session ID exists for chat history persistence
if "chat_session_id" not in st.session_state:
    st.session_state.chat_session_id = str(uuid.uuid4())
    st.session_state.messages = [] # Initialize empty messages for a new session
    st.session_state.current_response = "" # For storing partial streaming response

st.title("💬 Chat with Your LLM")
st.markdown(f"**Session ID:** `{st.session_state.chat_session_id}`")
st.info(f"Current LLM: **{st.session_state.llm_provider}** - **{st.session_state.llm_model}** (Configured on [Configuration Page](Configuration))")
if st.session_state.rag_enabled:
    st.warning("RAG Context is Enabled (Future Implementation).")
else:
    st.info("RAG Context is Disabled.")


# Function to display chat messages
def display_chat_messages():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Load chat history from backend on first load or session change
# This ensures consistency with the database and avoids local duplication
if "history_loaded" not in st.session_state or st.session_state.history_loaded is False:
    st.session_state.history_loaded = True
    st.session_state.messages = asyncio.run(get_chat_history_from_backend(st.session_state.chat_session_id))


# Display existing messages
display_chat_messages()

# Chat input
if prompt := st.chat_input("Say something..."):
    # Add user message to display immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare for assistant's response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        st.session_state.current_response = "" # Reset for new response

        async def get_streaming_response():
            try:
                # Call the backend API for streaming LLM response
                stream_generator = call_generate_stream_api(
                    question=prompt,
                    llm_provider=st.session_state.llm_provider,
                    llm_model=st.session_state.llm_model,
                    temperature=st.session_state.temperature,
                    max_tokens=st.session_state.max_tokens,
                    session_id=st.session_state.chat_session_id,
                    rag_enabled=st.session_state.rag_enabled
                )

                # Iterate through the streamed chunks directly
                async for chunk in stream_generator:
                    st.session_state.current_response += chunk
                    message_placeholder.markdown(st.session_state.current_response + "▌") # Blinking cursor

                message_placeholder.markdown(st.session_state.current_response) # Final response

                # ONLY save assistant message to database (after full response is received)
                # The session_state.messages will be reloaded from DB on next rerun,
                # ensuring no local-only or duplicated entries.
                await save_chat_message_to_backend(
                    session_id=st.session_state.chat_session_id,
                    role="assistant",
                    message=st.session_state.current_response,
                    llm_provider=st.session_state.llm_provider,
                    llm_model=st.session_state.llm_model
                )
                # After saving, explicitly reload history to ensure display is up-to-date
                # without waiting for a full Streamlit rerun/refresh
                st.session_state.messages = asyncio.run(get_chat_history_from_backend(st.session_state.chat_session_id))


            except Exception as e:
                st.error(f"Error during LLM interaction: {e}")
                # Optionally remove the last user message if no response was generated
                # or if the save operation failed
                if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                    st.session_state.messages.pop()
                st.session_state.current_response = "" # Clear partial response

        # Run the async function using asyncio.run
        asyncio.run(get_streaming_response())
        st.rerun() # Force a rerun to clean up the cursor and ensure history is refreshed


# Add a button to clear chat history (local and from DB for this session)
if st.button("Clear Chat for this Session"):
    if st.session_state.messages: # Only clear if there are messages
        # Note: This currently only clears the local session state and starts a new session ID.
        # To truly delete from DB, a backend endpoint for deleting by session_id would be needed.
        st.session_state.messages = []
        st.session_state.chat_session_id = str(uuid.uuid4()) # Start a new session
        st.session_state.history_loaded = False # Force reload for new session
        st.rerun() # Rerun to apply changes
