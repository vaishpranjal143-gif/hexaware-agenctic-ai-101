from transformers import pipeline

generator = pipeline('text-generation', model='./models/qwen-0.5b')

messages = [
    {
        "role": "user",
        "content": "Complete this sentence: Sachin Tendulkar is God of"
    }
]

result = generator(messages, max_new_tokens=11)
print(result[0]['generated_text'][-1]["content"])

