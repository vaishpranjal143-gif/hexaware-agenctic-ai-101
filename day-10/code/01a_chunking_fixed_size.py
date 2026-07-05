from docs_utils import load_documents, print_header

def fixed_size_chunking(text, chunk_size=300):
    chunks = []
    for start in range(0, len(text), chunk_size):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
    return chunks

if __name__ == "__main__":
    documents = load_documents()
    doc = None
    for d in documents:
        if d["source"] == "product_features.md":
            doc = d
            break
    assert doc is not None, "Document 'product_features.md' not found."

    chunks = fixed_size_chunking(doc["text"])
    header = f"Fixed-size chunking -> {len(chunks)} chunks from {doc['source']}"
    print_header(header)
    
    preview_chunks = chunks[:3]  # Preview the first 3 chunks
    for i, c in enumerate(preview_chunks):
        chunk_length = len(c)
        print(f"--- Chunk {i} ({chunk_length} characters) ---\n{c}\n")