import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

words = ["king", "man", "woman", "queen",
         "dog", "cat", "car", "bicycle",
         "apple", "banana", "orange", "grape",
         "brother", "sister", "father", "mother",
         "uncle", "aunt", "nephew", "niece"]

vectors = model.encode(words)

coords = PCA(n_components=2).fit_transform(vectors)

for word, (x, y) in zip(words, coords):
    plt.scatter(x, y)
    plt.annotate(word, (x, y))

plt.title("2D Visualization of Word Embeddings")
plt.show()