import asyncio
from _setup import build_kernel

async def main():
    kernel = build_kernel()
    answer = await kernel.invoke_prompt("Explain RAG in one line")
    print(answer)

asyncio.run(main())

