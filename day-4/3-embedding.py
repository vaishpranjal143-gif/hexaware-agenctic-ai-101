from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

sentences = [
    "I love dogs",
    "Dogs are wonderful companions",
    "The stock market crashed yesterday"
]

embeddings = model.encode(sentences)

similarity = cosine_similarity(embeddings)

print(similarity)