import asyncio
from _setup import azure_embedding

async def main():
    embedding = azure_embedding()
    vectors = await embedding.generate_embeddings(["a happy dog", "a joyful puppy", "tax law"])
    for text, v in zip(["a happy dog", "a joyful puppy", "tax law"], vectors):
        print(f"Text: {text}\n {len(v)} dimensions\n")

asyncio.run(main())