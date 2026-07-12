from dotenv import load_dotenv
from os import getenv
import os
import urllib.request
import io
from pypdf import PdfReader
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

load_dotenv()

DOCUMENT_PATH = os.path.join(os.path.dirname(__file__), "gemma4-technical-report.md")
DOCUMENT_URL = "https://arxiv.org/pdf/2607.02770"

def download_document(url, file_path):
    if os.path.exists(file_path):
        return
    with urllib.request.urlopen(url, timeout=10) as response:
        raw = response.read()
    reader = PdfReader(io.BytesIO(raw))
    content = "\n\n".join(page.extract_text() or "" for page in reader.pages)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

def load_and_chunk(file_path, chunk_size=400, chunk_overlap=60):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
        )
    chunks = splitter.split_text(text)
    documents = []
    for i, chunk in enumerate(chunks):
        documents.append(Document(page_content=chunk, metadata={"chunk_id": i, "source": os.path.basename(file_path)}))
    return documents

download_document(DOCUMENT_URL, DOCUMENT_PATH)
CHUNKS = load_and_chunk(DOCUMENT_PATH)

embeddings = AzureOpenAIEmbeddings(
    azure_deployment=getenv("AZURE_OPENAI_EMBEDDING_MODEL"),
    api_version=getenv("AZURE_OPENAI_API_VERSION")
    )

vectorstore = FAISS.from_documents(CHUNKS, embeddings)

def retrieve(query, k=4):
    return vectorstore.similarity_search(query, k=k)