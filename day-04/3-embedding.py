from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

sentences = [
    "What is the name of your company?",
    "What is the name of your organization?",
    "I love football."
]

embeddings = model.encode(sentences)

similarity = cosine_similarity(embeddings)

print(similarity)