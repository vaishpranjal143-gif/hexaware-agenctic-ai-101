from transformers import GPT2Tokenizer

class HFTokenizer:
    def __init__(self):
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.pad_token_id = self.tokenizer.pad_token_id
        self.eos_token_id = self.tokenizer.eos_token_id
        self.vocab_size = len(self.tokenizer)

    def encode(self, text: str):
        return self.tokenizer.encode(text)
    
    def decode(self, ids: list[int]):
        return self.tokenizer.decode(ids)