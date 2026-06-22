from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('all-MiniLM-L6-v2')

query = "what animal was tired?"

sentences = [
    "The animal didn't cross the road",
    "The road was busy",
    "The weather was sunny",
    "The dog had a fatigue",
    "The cat was tired",
    "what animal was tired?"
]

embeddings = model.encode([query] + sentences)
print(embeddings)

scores = cosine_similarity([embeddings[0]], embeddings[1:])
print(scores)

for sentence, score in zip(sentences, scores[0]):
    print(f"Score: {score:.4f} | Senctence: {sentence}")