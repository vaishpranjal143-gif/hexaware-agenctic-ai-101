import json
from typing import Any, cast
from opentelemetry import trace
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from agent_framework.observability import configure_otel_providers

SPANS = InMemorySpanExporter(); configure_otel_providers(exporters=[SPANS])

import gradio as gr                                       # noqa: E402
from _shop import (INSTRUCTIONS, RATES, check_stock, client,  # noqa: E402
                   escalate, look_up_order, usage)

CATALOGUE = {"look_up_order": look_up_order, "check_stock": check_stock, "escalate": escalate}
grab = lambda s, k: int(str((s.attributes or {}).get(f"gen_ai.usage.{k}", 0) or 0))


def flush_since(mark: int) -> list:
    """Every span produced since `mark`, once the batch is flushed."""
    cast(Any, trace.get_tracer_provider()).force_flush()
    return list(SPANS.get_finished_spans())[mark:]


async def one_call(question: str, instructions: str, tools: list) -> tuple[int, list]:
    """Input tokens on the FIRST model call for a configuration, plus the spans."""
    mark = len(SPANS.get_finished_spans())
    await client().as_agent(name="probe", tools=tools, instructions=instructions).run(question)
    fresh = flush_since(mark)
    chats = [s for s in fresh if s.name.startswith("chat")]
    return (grab(chats[0], "input_tokens") if chats else 0), fresh


async def measure(question: str, chosen: list[str], with_instructions: bool):
    """Build the ladder, then run the real thing and make the two tally."""
    question = question.strip() or "Can I return HX-90455?"
    prompt = INSTRUCTIONS if with_instructions else ""

    rungs = [("nothing at all — just the question", "", [])]                 # rung 0
    if with_instructions:
        rungs.append(("+ system instructions", prompt, []))
    for name in chosen:                                                      # one rung per tool
        so_far = [CATALOGUE[n] for n in chosen[:chosen.index(name) + 1]]
        rungs.append((f"+ tool: {name}", prompt, so_far))

    ladder, previous = [], 0
    for label, instructions, tools in rungs:
        tokens, _ = await one_call(question, instructions, tools)
        ladder.append((label, tokens, tokens - previous if previous else 0))
        previous = tokens

    mark = len(SPANS.get_finished_spans())                                   # now the REAL turn
    await client().as_agent(name="real", tools=[CATALOGUE[n] for n in chosen],
                            instructions=prompt).run(question)
    fresh = flush_since(mark)
    chats = [s for s in fresh if s.name.startswith("chat")]
    tally = usage(fresh)

    rows = "\n".join(f"| {label} | {tokens} | +{added} |" for label, tokens, added in ladder)
    calls = "\n".join(
        f"| call {i} | {grab(s, 'input_tokens')} | {grab(s, 'output_tokens')} | "
        f"{'asked for a tool' if i < len(chats) else 'read the result and answered'} |"
        for i, s in enumerate(chats, start=1))
    schema = json.dumps(json.loads(str((next(
        (s for s in fresh if "gen_ai.tool.definitions" in (s.attributes or {})), chats[0])
        .attributes or {}).get("gen_ai.tool.definitions", "[]")) or "[]")[:1], indent=2) \
        if chosen else "(no tools selected)"

    return (f"## Where the input tokens go\n\n"
            f"Question: `{question}`\n\n"
            f"### 1 · What is attached to **every** call\n\n"
            f"| what is attached | input tokens | added |\n|---|---:|---:|\n{rows}\n\n"
            f"The last row is what **one** model call costs before anyone says anything.\n\n"
            f"### 2 · The actual turn — this is where {tally['in']} comes from\n\n"
            f"| | input | output | why |\n|---|---:|---:|---|\n{calls}\n"
            f"| **total** | **{tally['in']}** | **{tally['out']}** | "
            f"**USD {tally['usd']:.6f}** |\n\n"
            f"A tool-using turn is **{tally['calls']} billed calls**, and call 2 re-sends "
            f"everything call 1 sent, plus the tool result.\n\n"
            f"### 3 · Why one tool costs 40-70 tokens\n\n"
            f"One parameter becomes this much JSON Schema:\n\n```json\n{schema}\n```\n\n"
            f"Rates used: input USD {RATES['in']}/M · cached {RATES['cached']}/M · "
            f"output {RATES['out']}/M.")


with gr.Blocks(title="Where the tokens go") as demo:
    gr.Markdown("# Where do the input tokens go?\nTick tools on and off and watch the bill move.")
    with gr.Row():
        with gr.Column(scale=2):
            q = gr.Textbox("Can I return HX-90455?", label="Customer question")
            picks = gr.CheckboxGroup(list(CATALOGUE), value=list(CATALOGUE), label="Tools attached")
            instr = gr.Checkbox(True, label="Attach the system instructions")
            go = gr.Button("Measure", variant="primary")
        with gr.Column(scale=3):
            out = gr.Markdown("_press Measure — it makes several real model calls_")
    go.click(measure, [q, picks, instr], out)

if __name__ == "__main__":
    demo.launch()