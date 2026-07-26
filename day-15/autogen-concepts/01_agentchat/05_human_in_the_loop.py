import asyncio
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from _model import get_client

client = get_client()

refunds = AssistantAgent(
    name="refunds",
    model_client=client,
    system_message=(
        "You handle Hex Retail Refunds propose one specific refund amount and"
        "reason in two lines, then stop and wait for the manager's decision."
        "If manager approves confirm it and end your message with DONE."
        "If the manager pushes back propose a revised amount instead."
    )
)

manager = UserProxyAgent(
    name="manager",
    input_func=input,
)

team = RoundRobinGroupChat(
    [refunds, manager],
    termination_condition=TextMentionTermination("DONE"),
)

async def main():
    print("\n" + "=" * 80 + "\n")
    print("You are the MANAGER when you see enter your response type either approved to accept the refund the agent proposed or your own words example to high offer 50% instead to push back")
    print("\n" + "=" * 80 + "\n")
    await Console(team.run_stream(
        task="customers ₹10,000 headphones arrived cracked. Decide the refund."
    ))
    await client.close()

asyncio.run(main())