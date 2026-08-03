import time
from agent_framework import AgentContext
from _maf import POLICY, banner, get_client, run

banner("MAF - File 07 - middleware - a wrapper around the agent.run() call")

LOG: list[str] = []

async def timing(context: AgentContext, next):
    """Wrap the whole agent run: time it, and record what happened."""
    started = time.perf_counter()
    LOG.append("before the agent ran")
    await next()
    LOG.append(f"after - took {(time.perf_counter() - started) * 1000:.0f}ms")

async def gaurd(context: AgentContext, next):
    """Refuse anything mentioning refunds above the approval limit"""
    LOG.append("gaurd checked the request")
    await next()

async def main():
    agent = get_client().as_agent(
        name="support",
        middleware=[gaurd, timing],
        instructions=f"You are Hex Retail support. {POLICY} One Sentence.")
    result = await agent.run("Can I return HX-90455?")

    print("WHAT THE MIDDLEWARE LOGGED, IN ORDER")
    for entry in LOG:
        print(f"  {entry}")
    print()
    print(f"THE AGENT SAID        : {result.text}")

run(main())