import re
from docs_utils import load_documents, print_header

def sentence_chunks(text, sentences_per_chunk=4):
    text = text.replace("\n", " ")  # Replace newlines with spaces
    text = text.strip()  # Remove leading and trailing whitespace
    sentences = re.split(r'(?<=[.!?])\s+', text) # Split by sentence-ending punctuation followed by whitespace

    chunks = []
    for start in range(0, len(sentences), sentences_per_chunk):
        end = start + sentences_per_chunk
        sentence_group = sentences[start:end]
        chunk = " ".join(sentence_group)
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

    chunks = sentence_chunks(doc["text"])
    header = f"Sentence-based chunking -> {len(chunks)} chunks from {doc['source']}"
    print_header(header)
    print(chunks[0])  # Print the first chunk for preview

    
