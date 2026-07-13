from transformers.models.gpt2.modeling_gpt2 import GPT2Block
from transformers import GPT2Config

def get_transformer_block(embed_dim=128, num_head=4):
    config = GPT2Config(
        n_embd=embed_dim,
        n_head=num_head,
        n_positions=128
    )
    return GPT2Block(config)