import asyncio
from dataclasses import dataclass
from typing import Annotated
from semantic_kernel.connectors.in_memory import InMemoryCollection
from semantic_kernel.data.vector import VectorStoreField, vectorstoremodel
from semantic_kernel.functions import kernel_function, KernelArguments
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings
from _setup import build_kernel, azure_embedding

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

class MemoryPlugin:
    def __init__(self, collection, embedding):
        self.collection = collection
        self.embedding = embedding

    @kernel_function(description="Search company policies and return relevant information")
    async def search(self, query: str) -> str:
        vector = (await self.embedding.generate_embeddings([query]))[0]
        results = await self.collection.search(vector=list(map(float, vector)), top=1)
        return "\n".join([r.record.content async for r in results.results])
    
async def main():
    embedding = azure_embedding()
    vectors = await embedding.generate_embeddings(FACTS)
    records = [Fact(fact_id=i, content=t, embedding=list(map(float, v))) for i, (t, v) in enumerate(zip(FACTS, vectors))]

    collection = InMemoryCollection(record_type=Fact)
    await collection.ensure_collection_exists()
    await collection.upsert(records)

    kernel = build_kernel()
    kernel.add_plugin(MemoryPlugin(collection, embedding), "Memory")
    
    settings = AzureChatPromptExecutionSettings()
    settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
    
    answer = await kernel.invoke_prompt(
        "What is the return policy?",
        arguments=KernelArguments(settings=settings),
    )
    
    print(answer)

asyncio.run(main())
