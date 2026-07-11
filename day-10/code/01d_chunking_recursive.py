from docs_utils import load_documents, print_header, recursive_chunks

if __name__ == "__main__":
    documents = load_documents()
    doc = None
    for d in documents:
        if d["source"] == "product_features.md":
            doc = d
            break
    assert doc is not None, "Document 'product_features.md' not found."

    chunks = recursive_chunks(doc["text"], chunk_size=300)
    header = f"Recursive chunking -> {len(chunks)} chunks from {doc['source']}"
    print_header(header)

    preview_chunks = chunks[:3]  # Preview the first 3 chunks
    for i, c in enumerate(preview_chunks):
        chunk_length = len(c)
        print(f"--- Chunk {i} ({chunk_length} characters) ---\n{c}\n")