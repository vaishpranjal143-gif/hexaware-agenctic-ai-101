# What is Swarm of Agents?
# Swarm of Agents is a concept where multiple agents work together to solve a problem or complete a task. Each agent has its own capabilities and responsibilities, and they communicate with each other to achieve

# What is Swarm in Autogen?
# A Swarn has no chair.

import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination, HandoffTermination
from autogen_agentchat.messages import HandoffMessage
from autogen_agentchat.teams import Swarm
from autogen_agentchat.ui import Console
from _model import get_client

client = get_client()

front_desk = AssistantAgent(
    name="front_desk",
    model_client=client,
    handoffs=["fraud_desk"],
    system_message=(
        "You are the front desk of Hex Retail. You handle all customer complaints and"
        "decide which desk should handle it. If you decide to handoff to another desk,"
        "send a HandoffMessage with the name of the desk."
    )
)

fraud_desk = AssistantAgent(
    name="fraud_desk",
    model_client=client,
    handoffs=["user"],
    system_message=(
        "You are the fraud desk of Hex Retail. You handle all fraud complaints and"
        "resolve them in two lines, then say CLOSED."
    )
)

team = Swarm(
    [front_desk, fraud_desk],
    termination_condition=TextMentionTermination("CLOSED") | HandoffTermination(target="user")
)

async def main():
    result = await Console(team.run_stream(
        task="There are three charges on my card I never made, on order AR-4471."
    ))
    last = result.messages[-1]

    if isinstance(last, HandoffMessage) and last.target == "user":
        print("\n>>> The Swarm PAUSED and is waiting for a human decision.\n")
        decision = input("Authorize blocking the card? (yes/no): ")

        await Console(team.run_stream(task=HandoffMessage(
            source="user",
            target="last.source",
            content=f"Manager's decision: {decision}"
        )))

    await client.close()

asyncio.run(main())