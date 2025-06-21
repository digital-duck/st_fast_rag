import os
from typing import Literal, Dict

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import BaseChatModel

def get_llm(
    provider: Literal["claude", "openai", "gemini"],
    model_name: str,
    temperature: float = 0.3,
    max_tokens: int = 1024,
    streaming: bool = True
) -> BaseChatModel:
    """
    Abstracted function to get an LLM instance based on the provider.

    Args:
        provider (Literal["claude", "openai", "gemini"]): The LLM provider.
        model_name (str): The specific model name (e.g., "claude-3-sonnet-20240229", "gpt-4o", "gemini-pro").
        temperature (float, optional): Controls randomness. Defaults to 0.7.
        max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 1024.
        streaming (bool, optional): Whether to enable streaming. Defaults to True.

    Returns:
        BaseChatModel: An initialized LangChain ChatModel instance.

    Raises:
        ValueError: If an unsupported provider is given or API key is missing.
    """
    if provider == "claude":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set.")
        return ChatAnthropic(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=streaming,
            anthropic_api_key=api_key
        )
    elif provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=streaming,
            openai_api_key=api_key
        )
    elif provider == "gemini":
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            max_output_tokens=max_tokens, # Gemini uses max_output_tokens
            streaming=streaming,
            google_api_key=api_key
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

# Define common model names for convenience
LLM_MODELS: Dict[str, Dict[str, str]] = {
    "claude": {
        "Sonnet 3.5": "claude-3-5-sonnet-20240620", # Latest Sonnet
        "Opus 3": "claude-3-opus-20240229",
        "Haiku 3": "claude-3-haiku-20240307",
    },
    "openai": {
        "GPT-4o": "gpt-4o",
        "GPT-4o-mini": "gpt-4o-mini",
        "GPT-3.5 Turbo": "gpt-3.5-turbo",
    },
    "gemini": {
        "Gemini 1.5 Flash": "gemini-1.5-flash",
        "Gemini 1.5 Pro": "gemini-1.5-pro",
    }
}
