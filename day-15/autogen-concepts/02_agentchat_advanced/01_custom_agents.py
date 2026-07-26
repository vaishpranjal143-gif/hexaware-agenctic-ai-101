# custom agent in autogen!

import asyncio
from typing import Sequence
from autogen_agentchat.agents import AssistantAgent, BaseChatAgent
from autogen_agentchat.messages import BaseChatMessage, TextMessage
from autogen_agentchat.base import Response
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from _model import get_client

class PolicyAgent(BaseChatAgent):
    def __init__(self, name: str) -> None:
        super().__init__(name, "Applies the refund rulebook.")

    @property
    def produced_message_types(self) -> Sequence[type[BaseChatMessage]]:
        return (TextMessage,)

    async def on_messages(self, messages: Sequence[BaseChatMessage],
                         calcenllation_token: CancellationToken) -> Response:
        text = " ".join(m.to_text() for m in messages).lower()
        amount = 0
        for word in text.replace(",", "").split():
            if word.isdigit():
                amount = max(amount, int(word))
        if amount > 5000:
            verdict = f"POLICY: {amount} exceeds the 5000 INR limit -> manager must approve."
        else:
            verdict = f"POLICY: {amount} is within the 5000 INR limit -> auto-approve."
        return Response(chat_message=TextMessage(content=verdict, source=self.name))

    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        pass


client = get_client()

writer = AssistantAgent(
    name="writer",
    model_client=client,
    system_message=(
        "turn the policy line into one warm sentence for the customer."
    )
)

team = RoundRobinGroupChat(
    [PolicyAgent("policy"), writer],
    termination_condition=MaxMessageTermination(4),
)

async def main():
    await Console(team.run_stream(
        task="customer wants a refund of ₹10,000 for AR-4471 because the headphones arrived cracked. Decide the refund."))
    await client.close()

asyncio.run(main())