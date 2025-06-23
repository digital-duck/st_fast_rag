# st_fast_rag
RAG - streamlit frontend + fastapi backend + langchain

```bash
cd st_fast_rag
touch requirements.txt .env.example .env
mkdir backend frontend
cd backend
touch __init__.py main.py llm_abstraction.py rag_core.py database.py crud.py
cd frontend
mkdir pages
touch __init__.py Home.py utils.py pages/0_Configuration.py pages/1_Chat_with_LLM.py touch pages/2_Notes.py

```


# Roadmap

## Features

- add RAG to chat with PDF doc
- add RAG to chat with DB
- 

## Refactoring

- use ag-grid to 
  - display Chat History
  - manage Note