from docs_utils import load_documents, print_header

def overlapping_chunks(text, chunk_size=300, overlap=60):
    step = chunk_size - overlap
    chunks = []
    for start in range(0, len(text), step):
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

    chunks = overlapping_chunks(doc["text"])
    header = f"Fixed-size chunking with overlap -> {len(chunks)} chunks from {doc['source']}"
    print_header(header)

    end_of_chunk_0 = chunks[0][-60:]  # Get the last 60 characters of the first chunk
    start_of_chunk_1 = chunks[1][:100]
    print("--- end of chunk 0: ---", repr(end_of_chunk_0))
    print("--- start of chunk 1: ---", repr(start_of_chunk_1))
