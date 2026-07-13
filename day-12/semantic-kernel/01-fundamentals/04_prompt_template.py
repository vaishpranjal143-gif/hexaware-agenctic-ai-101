import asyncio
from semantic_kernel.functions import KernelArguments
from _setup import build_kernel

async def main():
    kernel = build_kernel()
    answer = await kernel.invoke_prompt(
        "write a one-line {{$tone}} welcome message for a {{$product}} user",
        arguments=KernelArguments(tone="cheerful", product="banking app")
    )
    print(answer)

asyncio.run(main())
