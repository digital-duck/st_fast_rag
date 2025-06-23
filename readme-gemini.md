## **Project: st_fast_rag (v2.0)**

This updated project expands the Retrieval Augmented Generation (RAG) application to include a multi-page Streamlit frontend, a persistent SQLite database for chat history and notes, and advanced RAG capabilities.

**New Features:**

* **Multi-Page Streamlit App:** Organized into distinct pages for configuration, LLM chat, and note-taking.  
* **SQLite Database Integration:** Uses SQLAlchemy to manage chat_history and notes tables in fast_rag.sqlite3.  
* **Persistent Conversations:** All LLM interactions are saved to the database.  
* **Integrated Note-Taking:** Users can create, view, edit, and delete personal notes.  
* **Advanced RAG (Future):** Designed to seamlessly incorporate chat history and note data as context for future LLM conversations.

### **Project Layout**

st_fast_rag/  
├── .env.example              # Example environment variables for API keys and backend config  
├── README.md                 # Project README (this file)  
├── requirements.txt          # Python dependencies for the entire project  
│  
├── backend/                  # FastAPI backend services  
│   ├── __init__.py           # Makes 'backend' a Python package  
│   ├── main.py               # Main FastAPI application  
│   ├── llm_abstraction.py    # LLM provider abstraction logic (Claude, OpenAI, Gemini)  
│   ├── rag_core.py           # Core RAG/LLM chain definition (will be updated for RAG context)  
│   ├── database.py           # SQLAlchemy database setup and models (new)  
│   └── crud.py               # CRUD operations for database models (new)  
│  
└── frontend/                 # Streamlit frontend application  
    ├── __init__.py           # Makes 'frontend' a Python package  
    ├── Home.py               # Main entry point for the multi-page app (new)  
    ├── utils.py              # Helper functions for FastAPI client interactions (new)  
    ├── pages/                # Streamlit individual pages  
    │   ├── 0_Configuration.py  # Page for LLM provider and model selection (new)  
    │   ├── 1_Chat_with_LLM.py  # Page for LLM interaction and chat history (new)  
    │   └── 2_Notes.py          # Page for note-taking (new)

### **Setup Instructions**

1. **Clone the Repository:**  
```bash
git clone https://github.com/your-username/st_fast_rag.git  
cd st_fast_rag
```

2. **Create a Virtual Environment (Recommended):**  
```bash
# python -m venv venv  
# source venv/bin/activate  # On Windows: venvScriptsactivate

conda create -n rag python=3.12
conda activate rag
```

3. **Install Dependencies:**  
```bash
pip install -r requirements.txt

cd st_fast_rag/src/backend
python database.py  # create tables

sh run_fastapi.sh

# in another terminal
conda activate rag
cd st_fast_rag
sh run_streamlit.sh
```

4. Configure Environment Variables:  
   Create a .env file in the root directory (st_fast_rag/) based on .env.example.  
   # .env  
   ANTHROPIC_API_KEY="your_anthropic_api_key_here"  
   OPENAI_API_KEY="your_openai_api_key_here"  
   GOOGLE_API_KEY="your_google_api_key_here"

   # FastAPI backend host and port (adjust if running on a different machine/port)  
   BACKEND_HOST="127.0.0.1"  
   BACKEND_PORT="8000"

   # Database URL for SQLAlchemy (SQLite)  
   DATABASE_URL="sqlite:///./fast_rag.sqlite3"

   *Replace "your_api_key_here" with your actual API keys. Ensure the DATABASE_URL is set correctly for your SQLite file location.*

### **How to Run**

1. Initialize the Database:  
   Before starting the backend for the first time, you need to create the database tables.  
   Navigate to the st_fast_rag/backend/ directory and run:  
   python database.py

   This will create the fast_rag.sqlite3 file and the necessary tables.  
2. Start the FastAPI Backend:  
   Open a terminal, navigate to the st_fast_rag/ directory, and run:  
   cd backend  
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload

   You should see output indicating the FastAPI server is running. You can also visit http://127.0.0.1:8000/docs in your browser to see the FastAPI Swagger UI.  
3. Start the Streamlit Frontend:  
   Open a separate terminal, navigate to the st_fast_rag/ directory (make sure your virtual environment is activated), and run:  
   streamlit run frontend/Home.py

   This will open the Streamlit application in your web browser.

### **How to Use**

* The Streamlit app will now have a sidebar for navigation between pages.  
* **Configuration Page:** Select your desired LLM provider and model. These settings will persist across pages via Streamlit's session_state.  
* **Chat with LLM Page:** Interact with the selected LLM, and your conversations will be saved and displayed.  
* **Notes Page:** Create, view, edit, and delete personal notes.  
* Experiment with different functionalities!

### **Future Enhancements**

* **Actual RAG Implementation:** Integrate a vector database (e.g., ChromaDB, Pinecone, Qdrant) and a LangChain Retriever to perform true Retrieval Augmented Generation. This would involve:  
  * Ingesting documents and creating embeddings.  
  * Adding an endpoint to the FastAPI backend for document ingestion.  
  * Modifying rag_core.py to use a retriever before calling the LLM, incorporating chat_history and notes as context.  
* **Error Handling & UI Feedback:** More robust error messages in the UI for API key issues, network errors, etc.  
* **Configurable RAG Parameters:** Allow users to adjust top-k retrieval, chunking strategies, etc.  
* **Deployment:** Instructions for deploying both FastAPI and Streamlit to AWS ECS (or other cloud platforms).