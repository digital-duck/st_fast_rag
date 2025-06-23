import streamlit as st
import asyncio
import datetime
from frontend.utils import get_chat_history_from_backend, initialize_llm_config_session_state # Corrected import

st.set_page_config(page_title="Chat History", layout="wide")

# Ensure LLM config and session ID are initialized
initialize_llm_config_session_state()
if "chat_session_id" not in st.session_state:
    st.session_state.chat_session_id = None # Should be initialized by Chat_with_LLM.py already

st.title("📚 Chat History")
st.markdown("Review your past conversations with the LLM.")

if st.session_state.chat_session_id:
    st.markdown(f"**Current Session ID:** `{st.session_state.chat_session_id}`")

    # Removed @st.cache_data to ensure fresh history is loaded each time.
    # Caching was preventing new messages from appearing.
    def load_chat_history_sync(session_id_to_load: str):
        """Synchronous wrapper to load chat history from async backend."""
        st.spinner("Loading chat history...") # Manually show spinner if needed
        return asyncio.run(get_chat_history_from_backend(session_id_to_load))

    chat_history = load_chat_history_sync(st.session_state.chat_session_id)

    if not chat_history:
        st.info("No chat history found for this session yet. Start chatting on the 'Chat with LLM' page!")
    else:
        # Display messages in reverse chronological order (most recent at top)
        # Or, if you prefer chronological, remove .reverse()
        chat_history.reverse()

        for message in chat_history:
            role = message["role"]
            content = message["message"]
            # Convert timestamp string to datetime object for formatting
            timestamp_dt = datetime.datetime.fromisoformat(message["timestamp"])
            timestamp_formatted = timestamp_dt.strftime('%Y-%m-%d %H:%M:%S')
            llm_info = f"({message['llm_provider']} - {message['llm_model']})"

            with st.chat_message(role):
                st.markdown(f"**{role.capitalize()}** {llm_info} at *{timestamp_formatted}*:")
                st.markdown(content)
else:
    st.warning("No active chat session found. Please visit the 'Chat with LLM' page to start a new session.")

