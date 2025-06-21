import streamlit as st
from backend.llm_abstraction import LLM_MODELS # Import the LLM models dictionary
from frontend.utils import initialize_llm_config_session_state

# Initialize LLM configuration in session state if not already done
initialize_llm_config_session_state()

st.set_page_config(page_title="Configuration", layout="wide")

st.title("⚙️ LLM Configuration")
st.markdown("Set your preferred LLM provider and model, along with generation parameters.")

# --- LLM Provider and Model selection ---
st.subheader("LLM Selection")

# LLM Provider selection
llm_provider_options = list(LLM_MODELS.keys())
selected_llm_provider = st.selectbox(
    "Select LLM Provider:",
    options=llm_provider_options,
    index=llm_provider_options.index(st.session_state.llm_provider)
)
st.session_state.llm_provider = selected_llm_provider

# Dynamically update model options based on selected provider
model_display_names = list(LLM_MODELS[st.session_state.llm_provider].keys())
# Find current model's display name or default to first if not found
try:
    current_model_value = st.session_state.llm_model
    current_model_display_name = next(
        key for key, value in LLM_MODELS[st.session_state.llm_provider].items()
        if value == current_model_value
    )
    model_default_index = model_display_names.index(current_model_display_name)
except (ValueError, StopIteration):
    model_default_index = 0 # Default to first model if current one isn't found in new provider's list

selected_model_display_name = st.selectbox(
    "Select Model:",
    options=model_display_names,
    index=model_default_index
)
st.session_state.llm_model = LLM_MODELS[st.session_state.llm_provider][selected_model_display_name]

# --- LLM Parameters ---
st.subheader("Generation Parameters")
st.session_state.temperature = st.slider(
    "Temperature (randomness):",
    min_value=0.0,
    max_value=1.0,
    value=st.session_state.temperature,
    step=0.05,
    help="Higher values (e.g., 0.8) make the output more random, while lower values (e.g., 0.2) make it more focused and deterministic."
)

st.session_state.max_tokens = st.slider(
    "Max Tokens (response length):",
    min_value=100,
    max_value=4096, # Set a reasonable max limit, models might have higher
    value=st.session_state.max_tokens,
    step=100,
    help="Maximum number of tokens (words/sub-words) the LLM will generate in its response."
)

st.subheader("Advanced RAG Options (Future)")
st.session_state.rag_enabled = st.checkbox(
    "Enable RAG Context from Notes/Chat History (Future Implementation)",
    value=st.session_state.rag_enabled,
    help="When enabled, future LLM conversations will attempt to use relevant information from your saved notes and chat history as context. (Requires future RAG implementation in backend)."
)

st.success("LLM Configuration Saved!")
st.info(f"Current LLM: **{st.session_state.llm_provider}** - **{st.session_state.llm_model}**")
st.markdown("Navigate to `Chat with LLM` or `Notes` using the sidebar.")
