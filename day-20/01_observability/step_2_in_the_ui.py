from typing import Any, cast
from opentelemetry import trace
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from agent_framework.observability import configure_otel_providers

SPANS = InMemorySpanExporter()
configure_otel_providers(exporters=[SPANS])

import gradio as gr
from _shop import BACKEND, MODEL, history_to_messages, support_agent

AGENT = support_agent()

def since(mark: int) -> list:
    """Only the spans provided by the turn we just ran."""
    cast(Any, trace.get_tracer_provider()).force_flush()
    return list(SPANS.get_finished_spans())[mark:]

async def reply(message: str, history: list[dict]) -> str:
    """Answer, then append a plain English account of what the agent actually did."""
    from agent_framework import Message
    mark = len(SPANS.get_finished_spans())
    answer = (await AGENT.run([*history_to_messages(history), Message("user", [message])])).text
    steps = [f"`{s.name}`" for s in since(mark) if s.name.startswith(("chat", "execute_tool"))]
    return f"{answer}\n\n---\n**under the hood** {' -> '.join(steps) or 'nothing'}"

demo = gr.ChatInterface(fn=reply, title="Hex Retail support",
                        description=f"backend: {BACKEND} · model: {MODEL} · **showing its working**",
                        examples=[{"text": "Can I return HX-90455?"},
                                  {"text": "Is the Hex Buds Mk II in stock?"},
                                  {"text": "My order HX-99999 is broken."}])

if __name__ == "__main__":
    demo.launch()