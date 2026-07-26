import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import MultiModalMessage, StopMessage, TextMessage
from autogen_core import CancellationToken, Image
from PIL import Image as PILImage
from _model import get_client

text = TextMessage(
    content="My order AR-4471 arrived with a cracked case.",
    source="customer"
)

stop = StopMessage(
    content="Ticket resolved",
    source="supervisor"
)

damage_photo = PILImage.new("RGB", (8, 8), "red")
picture = MultiModalMessage(
    content=["Here is a photo of the damage:",
             Image.from_pil(damage_photo)],
    source="customer"
)

for m in (text, stop, picture):
    print(f"{type(m).__name__:20} from={m.source}")

agent = AssistantAgent(
    name="support",
    model_client=get_client(),
    system_message="You are Hex Retail Support. Reply in one sentence."
)

async def main():
    response = await agent.on_messages([text], CancellationToken())
    print("\nREPLIED WITH :", type(response.chat_message).__name__)
    print("CONTENT        :", response.chat_message.to_text())
    await agent.close()

asyncio.run(main())