from transformers import GPT2Config, GPT2LMHeadModel

def create_hf_gpt_model(vocab_size, embed_dim, num_head, num_layers=2):
    config = GPT2Config(
        vocab_size=vocab_size,
        n_positions=128,
        n_embd=embed_dim,
        n_layer=num_layers,
        n_head=num_head
    )
    return GPT2LMHeadModel(config)