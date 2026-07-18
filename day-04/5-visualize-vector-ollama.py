import ollama
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

words = ["king", "man", "woman", "queen",
         "dog", "cat", "car", "bicycle",
         "apple", "banana", "orange", "grape",
         "brother", "sister", "father", "mother",
         "uncle", "aunt", "nephew", "niece"]

vectors = [
    ollama.embeddings(
        model="embeddinggemma:latest",
        prompt=word
    )["embedding"]
    for word in words
]

coords = PCA(n_components=2).fit_transform(vectors)

for word, (x, y) in zip(words, coords):
    plt.scatter(x, y)
    plt.annotate(word, (x, y))

plt.title("2D Visualization of Word Embeddings")
plt.show()