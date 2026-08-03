from _maf import POLICY, banner, get_client, run

banner("MAF - File 01 - client + instructions")

async def main():
    client = get_client()
    agent = client.as_agent(
        name="support",
        instructions=f"You are Hex Retail support. {POLICY} Answer in one sentence.")
    result = await agent.run("My headphones arrived 12 days ago and crackle. Can I return them?")

    print(f"THE AGENT SAID")
    print(f"  {result.text}")
    print()
    print("WHAT CAME BACK")
    print(f" type : {type(result).__name__}")
    print(f" messages : {len(result.messages)}")

run(main())