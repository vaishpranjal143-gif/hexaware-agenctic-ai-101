import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from _model import get_client

client = get_client()
optimist = AssistantAgent("optimist", client, system_message="you're always argue FOR a full refund, never say SETTLED.")
skeptic = AssistantAgent("skeptic", client, system_message="you always argue AGAINST refund, never say SETTLED.")
team = RoundRobinGroupChat([optimist, skeptic], termination_condition=MaxMessageTermination(6))

async def main():
    result = await team.run(task="Should we refund order AR-4471?")

    for message in result.messages:
        usage = message.models_usage
        cost = f"{usage.prompt_tokens} + {usage.completion_tokens}" if usage else "-"
        print(f"[{message.source:<9}] {message.to_text()[:80]:<80}  ({cost})")

    print(f"\nStopped because: {result.stop_reason}")
    await client.close()

asyncio.run(main())
