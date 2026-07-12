from dotenv import load_dotenv
from os import getenv
import os
import urllib.request
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langchain_community.document_loaders import PyPDFLoader
from system_prompt import SYSTEM_PROMPT

load_dotenv()

llm = AzureChatOpenAI(
    azure_deployment=getenv("AZURE_OPENAI_MODEL"),
    api_version=getenv("AZURE_OPENAI_API_VERSION"),
    streaming=True
    )

PDF_PATH = os.path.join(os.path.dirname(__file__), "gemma4-technical-report.pdf")
PDF_URL = "https://raw.githubusercontent.com/hereandnowai/genai-and-prompt-engineering-eduhubspot-s1/main/day-6-of-14/7-chatbot-with-pdf/profile-rr.pdf"

def download_pdf(url, file_path):
    if os.path.exists(file_path):
        return
    with urllib.request.urlopen(url, timeout=10) as response:
        content = response.read()
    with open(file_path, "wb") as f:
        f.write(content)

download_pdf(PDF_URL, PDF_PATH)

def load_pdf_context(pdf_path):
    if not os.path.exists(pdf_path):
        return f"Warning: The PDF document at {pdf_path} does not exist."
    loader = PyPDFLoader(pdf_path)
    pages = loader.load_and_split()
    return "\n\n".join(page.page_content for page in pages)

pdf_context = load_pdf_context(PDF_PATH)
full_system_prompt = f"{SYSTEM_PROMPT}\n\nContext from PDF:\n{pdf_context}"

messages: list[BaseMessage] = [SystemMessage(content=full_system_prompt)]

def get_streaming_response(user_input):
    global messages
    messages.append(HumanMessage(content=user_input))

    full_response = ""
    for chunk in llm.stream(messages):
        content = chunk.content
        if isinstance(content, str) and content:
            full_response += content
            yield ("response", content)
    messages.append(AIMessage(content=full_response))
