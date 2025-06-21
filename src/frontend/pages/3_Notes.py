import streamlit as st
import asyncio
import datetime
from frontend.utils import (
    get_notes_from_backend,
    create_note_backend,
    update_note_backend,
    delete_note_backend
)

st.set_page_config(page_title="Notes", layout="wide")

st.title("📝 Your Personal Notes")
st.markdown("Create, view, edit, and delete your notes. All notes are saved to the backend database.")

# --- Session State for Note Editing ---
if "editing_note_id" not in st.session_state:
    st.session_state.editing_note_id = None
if "editing_note_title" not in st.session_state:
    st.session_state.editing_note_title = ""
if "editing_note_content" not in st.session_state:
    st.session_state.editing_note_content = ""

# --- Functions to refresh notes display ---
@st.cache_data(show_spinner="Loading notes...")
def load_notes_sync():
    """Synchronous wrapper to load notes from async backend."""
    return asyncio.run(get_notes_from_backend())

def refresh_notes():
    """Clears cache and reloads notes."""
    st.cache_data.clear()
    st.rerun()

# --- Display Notes ---
st.subheader("Your Existing Notes")

notes = load_notes_sync() # Load notes
if not notes:
    st.info("You don't have any notes yet. Use the form below to create one!")
else:
    for note in notes:
        with st.expander(f"**{note['title']}** (Last Updated: {datetime.datetime.fromisoformat(note['timestamp']).strftime('%Y-%m-%d %H:%M')})"):
            st.markdown(note['content'])

            col_edit, col_delete = st.columns(2)
            with col_edit:
                if st.button("Edit", key=f"edit_note_{note['id']}"):
                    st.session_state.editing_note_id = note['id']
                    st.session_state.editing_note_title = note['title']
                    st.session_state.editing_note_content = note['content']
                    st.rerun() # Rerun to show edit form
            with col_delete:
                if st.button("Delete", key=f"delete_note_{note['id']}", type="secondary"):
                    if asyncio.run(delete_note_backend(note['id'])):
                        refresh_notes() # Refresh after deletion

st.markdown("---")

# --- Create/Edit Note Form ---
st.subheader(
    "Create New Note" if st.session_state.editing_note_id is None else "Edit Note"
)

with st.form("note_form", clear_on_submit=True):
    note_title = st.text_input(
        "Note Title:",
        value=st.session_state.editing_note_title if st.session_state.editing_note_id else "",
        key="note_title_input"
    )
    note_content = st.text_area(
        "Note Content:",
        value=st.session_state.editing_note_content if st.session_state.editing_note_id else "",
        height=200,
        key="note_content_input"
    )

    col_submit, col_cancel = st.columns(2)
    with col_submit:
        if st.form_submit_button(
            "Save Note" if st.session_state.editing_note_id is None else "Update Note"
        ):
            if not note_title.strip() or not note_content.strip():
                st.error("Title and content cannot be empty.")
            else:
                if st.session_state.editing_note_id:
                    # Update existing note
                    if asyncio.run(update_note_backend(
                        st.session_state.editing_note_id, note_title, note_content
                    )):
                        st.session_state.editing_note_id = None # Clear editing state
                        st.session_state.editing_note_title = ""
                        st.session_state.editing_note_content = ""
                        refresh_notes()
                else:
                    # Create new note
                    if asyncio.run(create_note_backend(note_title, note_content)):
                        refresh_notes()
    with col_cancel:
        if st.session_state.editing_note_id and st.form_submit_button("Cancel Edit"):
            st.session_state.editing_note_id = None
            st.session_state.editing_note_title = ""
            st.session_state.editing_note_content = ""
            st.rerun() # Rerun to clear form and exit edit mode

