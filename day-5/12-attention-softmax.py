import torch

tokens = [
    "RCB",
    "GT",
    "SRH",
    "RR"
]

scores = torch.tensor([8.5, 7.0, 6.5, 5.0])

probs = torch.softmax(scores, dim=0)

for token, prob in zip(tokens, probs):
    print(f"Token: {token} | Probability: {prob:.4f}")