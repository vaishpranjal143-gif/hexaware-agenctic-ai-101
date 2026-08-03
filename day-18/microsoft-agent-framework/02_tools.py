from typing import Annotated
from _maf import ORDERS, POLICY, banner, get_client, run

banner("MAF - File 02 - tools - functions the agent may call")

CALLS: list[str] = []

def lookup_order(order_id: Annotated[str, "an order reference like HX-90455"]) -> str:
    """Look up a Hex Retail order and return its delivery status."""
    CALLS.append(order_id)
    record = ORDERS.get(order_id)
    if record is None:
        return f"No order {order_id} exists."
    return f"{order_id}: delivered {record['days']} days ago, faulty={record['faulty']}"

async def main():
    agent = get_client().as_agent(
        name="support",
        tools=[lookup_order],
        instructions=f"You are Hex Retail support. {POLICY} Always call lookup_order first")
    result = await agent.run("Is order HX-90455 returnable?")

    print(f" tool was called with : {CALLS}")
    print(f"THE AGENT SAID        : {result.text}")

run(main())