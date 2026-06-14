# what is a token?
# a token is a unit of meaning in natural language processing (NLP).
# It can be a word, a subword, or even a character.
# Tokens are the building blocks of language models
# and are used to represent text in a way that machines can understand.

# water --> litre
# fruits --> kilogrammes

# word --> token

# sentence --> tokenizer --> token --> numbers --> neural network

from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

sentences = [
    "ai is amazing",
    "a change that is unbelieveable",
    "transformers are powerful"
]

for text in sentences:
    tokens = tokenizer.tokenize(text)

    print(f"\nText: {text}")
    print(f"Tokens: {tokens}")
    print(f"Count: {len(tokens)}")