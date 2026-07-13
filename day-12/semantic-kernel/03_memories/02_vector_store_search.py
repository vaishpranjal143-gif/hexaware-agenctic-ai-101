import asyncio
from dataclasses import dataclass
from typing import Annotated
from semantic_kernel.connectors.in_memory import InMemoryCollection
from semantic_kernel.data.vector import VectorStoreField, vectorstoremodel
from _setup import azure_embedding

FACTS = [
    "Our return window is 30 days from the date of purchase.",
    "Support hours are from 9 AM to 5 PM, Monday to Friday.",
    "Shipping is free for orders over $50.",
]

@vectorstoremodel(collection_name="facts")
@dataclass
class Fact:
    fact_id: Annotated[int, VectorStoreField("key")]
    content: Annotated[str, VectorStoreField("data")]
    embedding: Annotated[list[float] | None, VectorStoreField("vector", dimensions=3072)] = None

async def main():
    embedding = azure_embedding()
    vectors = await embedding.generate_embeddings(FACTS)
    records = [Fact(fact_id=i, content=t, embedding=list(map(float, v))) for i, (t, v) in enumerate(zip(FACTS, vectors))]

    collection = InMemoryCollection(record_type=Fact)
    await collection.ensure_collection_exists()
    await collection.upsert(records)

    query_vector = (await embedding.generate_embeddings(["What is the return policy?"]))[0]
    results = await collection.search(vector=list(map(float, query_vector)), top=1)
    async for result in results.results:
        print("Best match: ", result.record.content)

asyncio.run(main())