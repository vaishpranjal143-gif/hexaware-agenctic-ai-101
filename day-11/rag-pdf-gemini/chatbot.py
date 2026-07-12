from dotenv import load_dotenv
from os import getenv
import os
import urllib.request
from google import genai
from langchain_community.document_loaders import PyPDFLoader
from system_prompt import SYSTEM_PROMPT

load_dotenv()

client = genai.Client(api_key=getenv("GEMINI_API_KEY"))
MODEL_NAME = "gemma-4-31b-it"

PDF_PATH = os.path.join(os.path.dirname(__file__), "profile-rr.pdf")
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

priming_history = [
    {"role": "user", "parts": [{"text": full_system_prompt}]},
    {"role": "model", "parts": [{"text": "Understood. I will use the provided context to answer your questions."}]}
]
chat = client.chats.create(model=MODEL_NAME, history=priming_history)

def get_streaming_response(user_input):
    full_response = ""
    for chunk in chat.send_message_stream(user_input):
        if chunk.text:
            full_response += chunk.text
            yield ("response", chunk.text)