from agent_framework import Message
from _maf import BACKEND, banner, get_client, run

banner("MAF - File 05 - sessions - who is actually storing the messages?")

async def main():
    agent = get_client().as_agent(name="s", instructions="Answer briefly.")

    # way 1 - an AgentSession object
    session = agent.create_session()
    await agent.run("My order is HX-90455. Remember it.", session=session)
    first = await agent.run("What is my order number?", session=session)
    kept = "HX-90455" in first.text
    print("Way 1 - AgentSession")
    print(f" session fields : {[f for f in dir(session) if not f.startswith('_')]}")
    print(f" remembered.    : {'YES' if kept else 'NO'} -> {first.text}")
    print()

    # way 2 - carry the history in the messages list
    history = [Message("user", ["My order is HX-90455. Remember it."]),
               Message("assistant", ["OK, I will remember that."]),
               Message("user", ["What is my order number?"])]
    second = await agent.run(history)
    print("Way 2 - carry the history in the messages list")
    print(f" remembered.    : {'YES' if 'HX-90455' in second.text else 'NO'} -> {second.text}")
    print()
    print(f" On '{BACKEND}' way 1 {'works' if kept else 'does not work'}, way 2 {'works' if 'HX-90455' in second.text else 'does not work'}")

run(main())