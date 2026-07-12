from dotenv import load_dotenv
from os import getenv
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from system_prompt import SYSTEM_PROMPT
from rag_pipeline import retrieve

load_dotenv()

llm = AzureChatOpenAI(
    azure_deployment=getenv("AZURE_OPENAI_MODEL"),
    api_version=getenv("AZURE_OPENAI_API_VERSION"),
    streaming=True
    )

messages: list[BaseMessage] = [SystemMessage(content=SYSTEM_PROMPT)]

def build_context(retrieved_chunks):
    parts = []
    for i, chunk in enumerate(retrieved_chunks):
        parts.append(f"[{i + 1}] {chunk.page_content}")
    return "\n\n".join(parts)

def get_streaming_response(user_input, top_k=4):
    global messages
    retrieved_chunks = retrieve(user_input, k=top_k)
    context = build_context(retrieved_chunks)
    prompt = f"Context passages:\n{context}\n\nQuestion: {user_input}"
    messages.append(HumanMessage(content=prompt))

    full_response = ""
    for chunk in llm.stream(messages):
        content = chunk.content
        if isinstance(content, str) and content:
            full_response += content
            yield ("response", content)
    messages.append(AIMessage(content=full_response))