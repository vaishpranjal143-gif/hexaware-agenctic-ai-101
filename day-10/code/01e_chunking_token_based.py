from docs_utils import load_documents, print_header

def token_chunks(text, max_tokens=60, overlap_tokens=10):
    words = text.split()
    step = max_tokens - overlap_tokens

    chunks = []
    for start in range(0, len(words), step):
        end = start + max_tokens
        word_group = words[start:end]
        chunk = " ".join(word_group)
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

    chunks = token_chunks(doc["text"])
    header = f"Token-based chunking -> {len(chunks)} chunks from {doc['source']}"
    print_header(header)

    first_chunk = chunks[0]
    first_chunk_words = first_chunk.split()
    word_count = len(first_chunk_words)
    print(f"--- Chunk 0 ({word_count} words) ---\n{first_chunk}\n")