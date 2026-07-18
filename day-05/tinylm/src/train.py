import os
import json
import torch
from transformers import Trainer, TrainingArguments
from tokenizer import HFTokenizer
from model import create_hf_gpt_model

def main():
    print("=" * 60)
    print(" OUR TINY LANGUAGE MODEL")
    print("=" * 60)

    # step 1: Load the dataset
    src_dir = os.path.dirname(os.path.abspath(__file__))
    qa_path = os.path.join(src_dir, "..", "data", "qa_demo.jsonl")
    qa_corpus = []
    with open(qa_path, "r", encoding="utf-8") as f:
        for line in f:
            qa_corpus.append(json.loads(line.strip()))

    # step 2: Initialize the tokenizer
    tokenizer_wrapper = HFTokenizer()
    tokenizer = tokenizer_wrapper.tokenizer
    print(f"[*] Character Vocabulary Size: {tokenizer_wrapper.vocab_size}")

    #   2.1. format texts
    formatted_texts = [
        f"Question: {qa['question']}\nAnswer: {qa['answer']}{tokenizer.eos_token}"
        for qa in qa_corpus
    ]

    #   2.2. tokenize input sequences
    inputs = tokenizer(formatted_texts, padding=True, truncation=True, max_length=128, return_tensors="pt")
    inputs["labels"] = inputs["input_ids"].clone()

    #   2.3. Dataset wrapper
    class QADataset(torch.utils.data.Dataset):
        def __init__(self, encodings):
            self.encodings = encodings
        def __getitem__(self, idx):
            return {key: val[idx] for key, val in self.encodings.items()}
        def __len__(self):
            return len(self.encodings["input_ids"])
    
    dataset = QADataset(inputs)

    # step 3: Create the model
    model = create_hf_gpt_model(vocab_size=tokenizer_wrapper.vocab_size, embed_dim=128, num_head=4, num_layers=2)

    # step 4: Define training arguments 
    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=500,
        per_device_eval_batch_size=8,
        learning_rate=1e-3,
        logging_steps=60,
        save_strategy="no",
        report_to="none",
        use_cpu=True if not torch.cuda.is_available() and not torch.backends.mps.is_available() else False
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset
    )

    print("[*] Training model using HF Trainer...")
    trainer.train()
    print("[+] Training completed")
    print("-" * 60)

    # step 5: Live Interactive Inference
    model.eval()
    device = model.device
    print("[*] Starting live interactive inference...")
    while True:
        try:
            q = input("\nYou: ").strip()
            if not q or q.lower() in ['exit', 'quit']:
                print("Bot: Goodbye!")
                break

            prompt = f"Question: {q}\nAnswer: "
            input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)

            with torch.no_grad():
                output_ids = model.generate(
                    input_ids,
                    max_new_tokens=100,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                    do_sample=False
                )

            response = tokenizer.decode(output_ids[0], skip_special_tokens=True)
            ans = response[len(prompt):].split("\n")[0].strip()
            print(f"Bot: {ans}")

        except KeyboardInterrupt:
            print("\nBot: Goodbye!")
            break
        except Exception as e:
            print(f"Error generating answer: {e}")
    
if __name__ == "__main__":
    main()
