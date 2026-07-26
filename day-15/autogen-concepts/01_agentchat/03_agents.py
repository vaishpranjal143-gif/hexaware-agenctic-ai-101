# what is an agent in autogen?
# AssistantAgent wraps 3 things
# 1. a model client (AzureOpenAIChatCompletionClient)
# 2. a system message (a prompt that sets the context for the agent)
# 3. tools

# when you give Autogen a task it runs a loop by itself:
# thinks -> calls a tool -> reads the result -> think again -> answer

import asyncio
from autogen_agentchat.agents import AssistantAgent
from _model import get_client

ORDERS = {
    "AR-4471": "Delivered 12th July signed for by Prashant",
    "AR-5098": "In transit, out for delivery today"
}

async def lookup_order(order_id: str) -> str:
    """Look up the delivery status of a Hex Retail order by its ID."""
    return ORDERS.get(order_id, "Order not found")

agent = AssistantAgent(
    name="support",
    model_client=get_client(),
    tools=[lookup_order],
    reflect_on_tool_use=True,
    system_message=("You are Hex Retail Support. You have access to a tool that can look up the delivery status of an order by its ID. "
    )
)

async def main():
    result = await agent.run(task="where is my order AR – 5098?")
    for message in result.messages:
        print(f"[{message.source}] {message.to_text()}")
    await agent.close()

asyncio.run(main())

