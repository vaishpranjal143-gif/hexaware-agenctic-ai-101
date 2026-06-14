from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased")

def embedding(word):
    inputs = tokenizer(word, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state[0][1].numpy()

king = embedding("king")
man = embedding("man")
woman = embedding("woman")
queen = embedding("queen")

predicted_queen = king - man + woman

similarity = cosine_similarity([predicted_queen], [queen])[0][0]

print(f"Similarity with queen: {similarity:.4f}")