"""STEP 1 — switch on observability, but don't change the app at all. You should see traces in the console."""

import os
os.environ["ENABLE_CONSOLE_EXPORTERS"] = "true"
os.environ["OTEL_SERVICE_NAME"] = "hex-retail-support"

from agent_framework.observability import configure_otel_providers
configure_otel_providers()

import gradio as gr
from _shop import BACKEND, MODEL, history_to_messages, support_agent

AGENT = support_agent()                                   # built once, reused for every message


async def reply(message: str, history: list[dict]) -> str:
    """One customer message in, one answer out. This is the whole application."""
    past = history_to_messages(history)                   # Gradio owns the transcript
    from agent_framework import Message
    result = await AGENT.run([*past, Message("user", [message])])
    return result.text


demo = gr.ChatInterface(fn=reply, title="Hex Retail support",
                        description=f"backend: {BACKEND} · model: {MODEL} · **traces in the terminal**",
                        examples=[{"text": "Can I return HX-90455?"},
                                  {"text": "Is the Hex Buds Mk II in stock?"},
                                  {"text": "My order HX-99999 is broken."}])

if __name__ == "__main__":
    demo.launch()
