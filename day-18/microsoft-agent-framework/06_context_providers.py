from typing import Any

from agent_framework import AgentSession, ContextProvider, SessionContext, SupportsAgentRun
from _maf import ORDERS, POLICY, banner, get_client, run

banner("MAF - File 06 - context providers - how to provide context to the agent")

class CustomerRecord(ContextProvider):
    """Injects the caller's order record into every run, without the user asking"""

    def __init__(self, order_id: str) -> None:
        super().__init__(source_id="customer-record")
        self.order_id = order_id

    async def before_run(self, *, agent, session, context, state) -> None:
        """Called before EVERY model invocation - so the facts stay fresh"""
        record = ORDERS.get(self.order_id, {})
        context.extend_instructions(
            self.source_id,
            f"The caller's order is {self.order_id}: delieverd "
            f"{record.get('days')} days ago, faulty={record.get('faulty')}.")

async def main():
    agent = get_client().as_agent(
        name="support",
        instructions=f"You are Hex Retail support. {POLICY} Answer in one sentence.",
        context_providers=[CustomerRecord("HX-90455")])
    result = await agent.run("Can I send these back?")
    print(f" the customer asked: 'Can I send these back?'")
    print(f" the agent said   : {result.text}")

run(main())