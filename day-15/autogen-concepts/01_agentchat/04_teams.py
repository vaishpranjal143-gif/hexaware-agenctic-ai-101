import asyncio
import os
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from _model import get_client

DEFAULT = os.environ["AZURE_OPENAI_MODEL"]
WRITER_DEPLOYMENT = os.environ.get("WRITER_DEPLOYMENT", DEFAULT)
REVIEWER_DEPLOYMENT = os.environ.get("REVIEWER_DEPLOYMENT", DEFAULT)

writer_client = get_client(WRITER_DEPLOYMENT)
reviewer_client = get_client(REVIEWER_DEPLOYMENT)

print(f"[writer -> {WRITER_DEPLOYMENT}]")
print(f"[reviewer -> {REVIEWER_DEPLOYMENT}]")
if WRITER_DEPLOYMENT == REVIEWER_DEPLOYMENT:
    print("Warning: writer and reviewer are using the same model deployment.")
    print("[REVIEWER_DEPLOYMENT] should be different from [WRITER_DEPLOYMENT] to avoid model confusion.")
print()

writer = AssistantAgent(
    name="writer",
    model_client=writer_client,
    system_message=(
        "You write replies to Hex Retail Customers. Keep them under 40 words."
        "If the reviewer asks for changes, rewrite the whole reply and show it."
    )
)

reviewer = AssistantAgent(
    name="reviewer",
    model_client=reviewer_client,
    system_message=(
        "You are a compliance reviewer of Hex Retail Customers. A reply is only acceptable if it apologises,"
        " names a concrete next step, and gives a timeframe. If anything is missing,"
        "say exactly what is missing and ask the writer to rewrite the reply. When all three are present,"
        "say 'Approved'."
    )
)

team = RoundRobinGroupChat(
    [writer, reviewer],
    termination_condition=TextMentionTermination("Approved"),
)

async def main():
    await Console(team.run_stream(
        task="Customer says their headphones arrived cracked. Write a reply."
    ))
    await writer_client.close()
    await reviewer_client.close()

asyncio.run(main())