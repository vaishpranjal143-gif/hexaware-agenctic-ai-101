
import asyncio
from typing import Sequence
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.messages import BaseChatMessage, BaseAgentEvent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from _model import get_client

client = get_client()

triage = AssistantAgent(
    name="triage",
    model_client=client,
    description="read the new customer, complaint, and states which desk should handle it.",
    system_message=(
        "Name the single correct desk (shipping, refunds or fraud) in one line."
    )
)

shipping = AssistantAgent(
    name="shipping",
    model_client=client,
    description="Handles late, lost or damaged delieveries and courier problems.",
    system_message=("Resolve the delivery problem in two lines, then say HANDLED.")
)  

refunds = AssistantAgent(
    name="refunds",
    model_client=client,
    description="Handles refund requests for damaged or defective products.",
    system_message=("Resolve the refund in two lines, then say HANDLED.")
)

def selector_func(messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> str | None:
    if len(messages) == 1:
        return triage.name
    return None

team = SelectorGroupChat(
    [triage, shipping, refunds],
    model_client=client,
    selector_func=selector_func,
    termination_condition=TextMentionTermination("HANDLED") | MaxMessageTermination(6),
)

async def main():
    await Console(team.run_stream(
        task="My parcel AR-1234 was marked as delivered but I never received it. Please help me."
    ))
    await client.close()

asyncio.run(main())