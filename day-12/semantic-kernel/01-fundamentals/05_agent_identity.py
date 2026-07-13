import asyncio
from semantic_kernel.agents import ChatCompletionAgent
from _setup import azure_chat

async def main():
    agent = ChatCompletionAgent(
        service=azure_chat(),
        name="Support",
        instructions="You are a friendly support rep. Respond to the user's question."
    )
    reply = await agent.get_response(message="Where is my order?")
    print(reply.content)

asyncio.run(main())