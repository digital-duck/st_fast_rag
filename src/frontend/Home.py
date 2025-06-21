import streamlit as st

# Set Streamlit page configuration for multi-page app
st.set_page_config(
    page_title="Fast RAG",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("💡 Welcome to RAG!")
st.subheader("Streamlit Frontend, FastAPI Backend, LangChain LLMs, and Persistent Data")

st.markdown(
    """
    This application is a comprehensive demo showcasing a modern Generative AI architecture:

    -   **Streamlit:** Provides an intuitive and interactive user interface.
    -   **FastAPI:** Powers a high-performance, asynchronous backend for handling LLM requests and data operations.
    -   **LangChain:** Offers a powerful framework for building LLM applications, with an abstraction layer allowing you to seamlessly switch between different LLM providers (Claude, GPT-4o, Gemini).
    -   **SQLite Database:** Persists your LLM conversations and personal notes, ensuring your data is saved.

    ### How to Use:
    1.  **Configure LLM:** Go to the `Configuration` page in the sidebar to select your preferred LLM provider and model. Remember to set up your API keys in the `.env` file!
    2.  **Chat with LLM:** Navigate to the `Chat with LLM` page to start conversations with your chosen AI. Your chat history will be automatically saved.
    3.  **Manage Notes:** Visit the `Notes` page to create, view, edit, and delete your personal notes.
    4.  **Advanced RAG (Coming Soon!):** The foundation is laid to incorporate your chat history and notes as context for future LLM conversations, enabling Retrieval Augmented Generation (RAG).

    ### Get Started:
    Use the navigation in the sidebar to explore the application's features.
    """
)

# Optional: Add an image or video showcasing the app
# st.image("path/to/your/app_screenshot.png", caption="st_fast_rag in action")

st.info("Remember to run both the FastAPI backend and the Streamlit frontend!")

