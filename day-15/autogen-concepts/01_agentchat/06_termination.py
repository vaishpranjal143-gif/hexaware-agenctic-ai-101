import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from _model import get_client

client = get_client()

optimist = AssistantAgent(
    name="optimist",
    model_client=client,
    system_message=(
        "you're always argue FOR a full refund one short line never say SETTLED."
    )
)

skeptic = AssistantAgent(
    name="skeptic",
    model_client=client,
    system_message=(
        "you always argue AGAINST refund one shot line never say SETTLED."
    )
)

async def run_with(rule, label):
    team = RoundRobinGroupChat([optimist, skeptic], termination_condition=rule)
    result = await team.run(task="Should we refund order AR-4471?")
    print(f"{label:24} -> {len(result.messages)} messages, stopped because: {result.stop_reason}")

async def main():
    word_only = TextMentionTermination("SETTLED")
    word_or_cap = TextMentionTermination("SETTLED") | MaxMessageTermination(6)

    await run_with(word_or_cap, "word or 6-message cap")
    await run_with(word_only | MaxMessageTermination(20), "word or 20-message cap")
    await client.close()

asyncio.run(main())