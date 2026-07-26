import asyncio
import time
from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ModelFamily, ModelInfo
from autogen_ext.models.ollama import OllamaChatCompletionClient

ORDERS = {
    "AR-4471": "Delivered 12th July signed for by Prashant",
    "AR-5098": "In transit, out for delivery today"
}

SYSTEM_MESSAGE = (
    "You are Hex Retail Support. You have access to a tool that can look up the delivery status of an order by its ID. "
    "You will be given a customer's message and you will respond in one sentence. "
    "If the customer asks about an order, you will call the tool to look up the order status and include it in your response. "
    "If the customer asks about something else, you will respond appropriately without calling the tool."
)

async def lookup_order(order_id: str) -> str:
    """Look up the delivery status of a Hex Retail order by its ID."""
    return ORDERS.get(order_id, "Order not found")

def make_client(model: str) -> OllamaChatCompletionClient:
    """Return a ready-to-use OllamaChatCompletionClient instance."""
    return OllamaChatCompletionClient(
        model=model,
        host="http://localhost:11434",
        model_info=ModelInfo(
            vision=True,
            function_calling=True,
            json_output=True,
            family=ModelFamily.UNKNOWN,
            structured_output=True,
            multiple_system_messages=True,
        ),
    )

async def ask(model: str, reflect: bool, show_all: bool = False) -> tuple[float, str]:
    """Run the Hex Retail Support agent with the given model and reflection setting, and return the time taken and the final response."""
    client = make_client(model)
    agent = AssistantAgent(
        name="support",
        model_client=client,
        tools=[lookup_order],
        reflect_on_tool_use=reflect,
        system_message=SYSTEM_MESSAGE
    )
    started = time.perf_counter()
    result = await agent.run(task="where is my order AR–5098?")
    elapsed = time.perf_counter() - started

    if show_all:
        for message in result.messages:
            print(f"[{message.source}] {message.to_text()[:100]}") # Print only the first 100 characters of each message

    await client.close()
    return elapsed, result.messages[-1].to_text()  # Return the time taken and the final response

async def main():
    print("=" * 40)
    print(" THE SAME AGENT AS AZURE OPENAI, BUT USING OLLAMA ")
    print("=" * 40)
    elapsed, _ = await ask(model="gemma4:e2b", reflect=False, show_all=True)
    print(f" ({elapsed:.1f}s) Final response entirely on this computer, no network calls to Azure OpenAI.")

    print("\n" + "=" * 40)
    print(" does model size matter or same agent three runs each?")
    print("=" * 40)
    for model in ("llama3.2", "gemma4:12b"):
        print(f"\nModel: {model}")
        for run in range(1, 4):
            elapsed, answer = await ask(model, reflect=True)
            print(f" Run {run}: ({elapsed:.1f}s) Final response: {answer[:100]}")  # Print only the first 100 characters of the final response

asyncio.run(main())

