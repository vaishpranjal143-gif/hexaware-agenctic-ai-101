import asyncio
import json
from pathlib import Path
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination
from _model import get_client

client = get_client()
SAVE_FILE = Path(__file__).parent / "ticket_state.json"

def build_team():
    agent = AssistantAgent(
        name="desk",
        model_client=client,
        system_message="you are a Hex Retail support answer in one short line."
    )
    return RoundRobinGroupChat([agent], termination_condition=MaxMessageTermination(3))

async def main():
    team_one = build_team()
    await team_one.run(task="Log this: order AR-4471 is cracked and needs a replacement.")

    state = await team_one.save_state()
    SAVE_FILE.write_text(json.dumps(state))
    print("SAVED : ", SAVE_FILE.name, f"({SAVE_FILE.stat().st_size} bytes)")

    del team_one

    team_two = build_team()
    blank = await team_two.run(task="Which order number did I mention?")
    print("BEFORE :", blank.messages[-1].to_text())

    team_three = build_team()
    await team_three.load_state(json.loads(SAVE_FILE.read_text()))
    recalled = await team_three.run(task="Which order number did I mention?")
    print("AFTER  :", recalled.messages[-1].to_text())

    await client.close()

asyncio.run(main())

