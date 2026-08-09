from typing import Annotated
from agent_framework import Message, ToolApprovalMiddleware, tool
from _maf import ORDERS, POLICY, banner, get_client, run

banner("File - 11 - Human in the loop")

EXECUTED: list[str] = []

@tool(approval_mode="never_require")
def lookup_order(order_id: Annotated[str, "an order reference"]) ->str:
    """Read an order. Changes nothing"""
    EXECUTED.append(f"lookup_order({order_id})")
    record = ORDERS.get(order_id, {})
    return f"{order_id}: delivered {record.get('days')} days ago, faulty={record.get('faulty')}"

@tool(approval_mode="always_require")
def issue_refund(order_id: Annotated[str, "an order reference"],
                 amount: Annotated[float, "amount in USD"]) -> str:
    """Refund a customer. Irreversible."""
    EXECUTED.append(f"issue_refund({order_id}, {amount})")
    return f"Refunded USD {amount} for {order_id}"

def ask_a_human(tool_name: str, arguments: str) -> bool:
    """Stop the whole program and wait for someone at a keyboard to decide."""
    print(f"\nApproval Needed")
    print(f"tool: {tool_name}")
    print(f"arguments: {arguments}")
    try:
        answer = input("Approve? [Y/N]: ").strip().lower()
    except EOFError:
        print(" (no one is here to answer - refusing by default)")
    return answer in ("y", "yes")

async def main():
    agent = get_client().as_agent(
        name="support",
        tools=[lookup_order, issue_refund],
        middleware=[ToolApprovalMiddleware()],
        instructions=f"You are Hex Retail Support. {POLICY} Refund faulty orders.")

    session = agent.create_session()

    # Turn 1 - the agent tries the refund and the gate stops it.
    result = await agent.run("Order HX-90455 is faulty. Refund USD 120.99.", session=session)
    print(f" after turn 1, executed: {EXECUTED}")
    pending = [c for m in result.messages for c in m.contents
               if c.type == "function_approval_request"]

    if not pending:
        print(" nothing needed approval"); return

    # The human step is below
    request = pending[0]
    call = request.function_call
    assert call is not None
    decision = ask_a_human(str(call.name), str(call.arguments))

    # turn 2 - resume the same session, carrying the human's decision
    approval = request.to_function_approval_response(approved=decision)
    result2 = await agent.run([Message(role="user", contents=[approval])], session=session)

    print(f" after turn 2, executed: {EXECUTED}")
    print(f" agent said            : {result2.text}")

run(main())

