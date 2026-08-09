from typing import Any, cast
from opentelemetry import trace
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from agent_framework.observability import configure_otel_providers

SPANS = InMemorySpanExporter()
configure_otel_providers(exporters=[SPANS])

import gradio as gr
from _shop import BACKEND, MODEL, history_to_messages, support_agent, usage

AGENT, SPENT = support_agent(), {"usd": 0.0, "turns": 0, "in": 0, "out": 0}

async def reply(message: str, history: list[dict]) -> str:
    """Answer, then price the turn and the conversation so far"""
    from agent_framework import Message
    mark = len(SPANS.get_finished_spans())
    answer = (await AGENT.run([*history_to_messages(history), Message("user", [message])])).text
    cast(Any, trace.get_tracer_provider()).force_flush()
    t = usage(list(SPANS.get_finished_spans())[mark:])
    SPENT["usd"] += t["usd"]; SPENT["turns"] += 1
    SPENT["in"] += t["in"]; SPENT["out"] += t["out"]
    return (f"{answer}\n\n---\n"
            f"**this turn**. {t['calls']} billed calls. input **{t['in']}**. "
            f"output **{t['out']}**. total {t['in'] + t['out']:,} tokens. USD {t['usd']:.6f}\n\n"
            f"**conversation so far**. input **{SPENT['in']}**. output **{SPENT['out']}**."
            f" USD {SPENT['usd']:.6f}"
            f"{SPENT['usd'] / SPENT['turns'] * 10_000:,.2f} per 10k turns")


demo = gr.ChatInterface(fn=reply, title="Hex Retail support",
                        description=f"backend: {BACKEND} · model: {MODEL} · **costed per turn**",
                        examples=[{"text": "Can I return HX-90455?"},
                                  {"text": "Is the Hex Buds Mk II in stock?"},
                                  {"text": "My order HX-99999 is broken."}])

if __name__ == "__main__":
    demo.launch()