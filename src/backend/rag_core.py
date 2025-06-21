from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_core.language_models.chat_models import BaseChatModel
from typing import List, Dict, Any, Optional

# In a real RAG application, this file would contain:
# 1. Document loading and chunking logic
# 2. Embedding model initialization
# 3. Vector store initialization and retrieval logic
# 4. The full RAG chain (retriever + LLM)

# For this initial demo, we'll keep the simple LLM chain.
# We'll add a placeholder for context integration when RAG is enabled.

def get_llm_chain(llm: BaseChatModel, use_rag_context: bool = False, context_data: Optional[str] = None) -> Runnable:
    """
    Creates a LangChain runnable chain for text generation,
    optionally incorporating RAG context.

    Args:
        llm (BaseChatModel): The initialized LangChain ChatModel.
        use_rag_context (bool): If True, the prompt will incorporate context_data.
        context_data (Optional[str]): The context string to be used for RAG.

    Returns:
        Runnable: A LangChain Runnable chain.
    """
    if use_rag_context and context_data:
        # RAG-enabled prompt template
        # In a full RAG implementation, {context} would come from a retriever
        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are a helpful AI assistant. Answer the user's questions clearly and concisely. "
                "Use the following provided context if relevant:\n\n---\nContext:\n{context}\n---\n"
            )),
            ("user", "{question}")
        ])
        # Create a chain that injects context if available
        # For now, we manually pass context_data, in a real RAG, this would be a retriever
        chain = (
            {"context": lambda x: context_data, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
    else:
        # Simple LLM prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant. Answer the user's questions clearly and concisely."),
            ("user", "{question}")
        ])
        # Simple LLM chain: Prompt -> LLM -> Output Parser
        chain = prompt | llm | StrOutputParser()

    return chain

