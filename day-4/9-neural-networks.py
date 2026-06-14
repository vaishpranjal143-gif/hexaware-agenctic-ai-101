from sklearn.datasets import make_circles
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
import matplotlib.pyplot as plt

X, y = make_circles(
    n_samples=500,
    noise=0.1,
    factor=0.3,
    random_state=42)

linear = LogisticRegression().fit(X, y)
nn = MLPClassifier(
    hidden_layer_sizes=(8, ),
    max_iter=5000,
    random_state=42).fit(X, y)

print(f"Linear Accuracy: {linear.score(X, y):.4f}")
print(f"Neural Accuracy: {nn.score(X, y):.4f}")

plots = [
    ("Actual", y),
    ("Linear", linear.predict(X)),
    ("Neural", nn.predict(X))]

for i, (title, labels) in enumerate(plots, 1):
    plt.subplot(1, 3, i)
    plt.scatter(X[:, 0], X[:, 1], c=labels)
    plt.title(title)

plt.tight_layout()
plt.show()