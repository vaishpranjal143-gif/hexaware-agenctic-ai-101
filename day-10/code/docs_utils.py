import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "documents")

def load_documents():
    documents = []
    filenames = os.listdir(DATA_DIR)
    sorted_filenames = sorted(filenames)  # Sort the filenames alphabetically
    for filename in sorted_filenames:
        if not filename.endswith(".md"):
            continue
        path = os.path.join(DATA_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        document = {"source": filename, "text": text}
        documents.append(document)
    return documents

def recursive_chunks(text, chunk_size=300, separators=("\n\n", "\n", ". ", " ")):
    def _split(text, seps):
        text = text.strip()
        if len(text) <= chunk_size or not seps:
            if text:
                return [text]
            return []
        
        sep = seps[0]
        rest_seps = seps[1:]
        raw_parts = text.split(sep)
        parts = []
        for p in raw_parts:
            if p.strip():  # Only add non-empty parts
                parts.append(p)
        if len(parts) == 1:
            return _split(text, rest_seps)
        
        chunks = []
        buffer = ""
        for part in parts:
            if buffer:
                candidate = buffer + sep + part
            else:
                candidate = part
            if len(candidate) <= chunk_size:
                buffer = candidate
            else:
                if buffer:
                    chunks.extend(_split(buffer, rest_seps))
                buffer = part
        if buffer:
            chunks.extend(_split(buffer, rest_seps))
        return chunks
    separator_list = list(separators)
    return _split(text, separator_list)

def chunk_documents(documents, chunk_size=300):
    chunks = []
    for doc in documents:
        doc_chunks = recursive_chunks(doc["text"], chunk_size=chunk_size)
        for chunk_text in doc_chunks:
            chunk = {"text": chunk_text, "source": doc["source"]}
            chunks.append(chunk)
    return chunks

def print_header(title):
    print("\n" + "=" * len(title))
    print(title)
    print("=" * len(title))