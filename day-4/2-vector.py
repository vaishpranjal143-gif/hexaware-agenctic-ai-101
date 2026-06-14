# what is a vector?
# a vector is a list of numbers that represent some kind of information
# in NLP, we often use vectors to represent words, sentences, or even entire documents
# these vectors are called embeddings
# embeddings are dense representations of text that capture semantic meaning
# for example, the word "king" might be represented as a vector of numbers that captures its meaning and relationship to other words like "queen",

from transformers import AutoTokenizer, AutoModel
import torch

MODELS = {
    "BERT": "bert-base-uncased",
    "GEMMA4-E2B": "google/gemma-4-E2B-it"
}

word = "king"

for name, path in MODELS.items():
    tokenizer = AutoTokenizer.from_pretrained(path)
    model = AutoModel.from_pretrained(path)

    inputs = tokenizer(word, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    vector = outputs.last_hidden_state[0].mean(dim=0)
    print(f"\nModel: {name} | Word: {word} | Shape: {vector.shape}")
    print(f"First 10 values:\n{vector[:10]}")