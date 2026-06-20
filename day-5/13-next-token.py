from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_name = "gpt2"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

text = "The capital of France is"
#[464, 3139, 286m 4881, 318]

inputs = tokenizer(text, return_tensors="pt")
with torch.no_grad():
    outputs = model(**inputs)

next_token_logits = outputs.logits[:, -1, :]

probs = torch.softmax(next_token_logits, dim=-1)

top_probs, top_indices = torch.topk(probs, k=10)

for prob, idx in zip(top_probs[0], top_indices[0]):
    token = tokenizer.decode([idx])
    print(f"{token: <15} {prob.item():.4f}")