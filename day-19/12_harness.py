import inspect
import shutil
from pathlib import Path
from typing import Annotated

from agent_framework import (FileSystemAgentFileStore,
                             FunctionInvocationContext,
                             create_harness_agent, tool)

from _maf import POLICY, banner, get_client, run

banner("THE HARNESS — equipment, not a gate")

#  Read the real signature rather than trust a slide.
OPTIONS = list(inspect.signature(create_harness_agent).parameters)
print(f"   create_harness_agent() takes {len(OPTIONS)} arguments")

GROUPS = {
    "plans its own work": ["disable_todo", "todo_provider"],
    "survives a long run": ["max_context_window_tokens", "disable_compaction"],
    "reads and writes files": ["file_access_store", "disable_file_access"],
    "remembers across runs": ["disable_file_memory", "file_memory_store"],
    "reaches outward": ["disable_web_search", "shell_executor", "background_agents"],
    "the file 10 gate, pre-wired": ["disable_tool_auto_approval", "auto_approval_rules"],
}
for group, names in GROUPS.items():
    print(f"   {group:28} {', '.join(n for n in names if n in OPTIONS)[:60]}")
print()

QUEUE = {
    "HX-90455": {"days": 12, "faulty": True,  "item": "Hex Studio headphones", "paid": 129.99},
    "HX-90456": {"days": 34, "faulty": False, "item": "Hex Buds Mk II",        "paid": 59.00},
    "HX-90457": {"days": 6,  "faulty": False, "item": "Hex Studio headphones", "paid": 129.99},
    "HX-90458": {"days": 27, "faulty": True,  "item": "Hex Desk Mic",          "paid": 84.50},
}

CALLS: list[str] = []
WORKSPACE = Path(__file__).parent / "_harness_workspace"


async def watch(context: FunctionInvocationContext, next):
    """Record the name of every tool that runs — including ones we did not write."""
    CALLS.append(context.function.name)
    await next()


@tool
def list_open_returns() -> str:
    """Every return request currently waiting for triage."""
    return ", ".join(QUEUE)


@tool
def lookup_return(order_id: Annotated[str, "an order reference"]) -> str:
    """Read one return request."""
    record = QUEUE.get(order_id)
    if not record:
        return f"{order_id}: no such order"
    return (f"{order_id}: {record['item']}, GBP {record['paid']}, delivered "
            f"{record['days']} days ago, faulty={record['faulty']}")


TASK = ("Triage every open return. For each one decide ACCEPT or REJECT under "
        "our policy and give a one-line reason. Then write the whole thing to "
        "triage_report.md as a markdown table, and finish with a total of the "
        "GBP we are refunding.")

TOOLS = [list_open_returns, lookup_return]


async def main():
    shutil.rmtree(WORKSPACE, ignore_errors=True)
    WORKSPACE.mkdir(parents=True)

    # ---- PART A — a plain agent from file 02, with no equipment ----------
    plain = get_client().as_agent(
        name="triage", tools=TOOLS, middleware=[watch],
        instructions=f"You are Hex Retail's returns desk. {POLICY}")
    answer_a = await plain.run(TASK)
    calls_a, CALLS[:] = list(CALLS), []
    files_a = list(WORKSPACE.iterdir())

    # ---- PART B — the harness, same job, same tools, same model ----------
    harness = create_harness_agent(
        client=get_client(), name="triage", tools=TOOLS, middleware=[watch],
        agent_instructions=f"You are Hex Retail's returns desk. {POLICY}",
        file_access_store=FileSystemAgentFileStore(root_directory=str(WORKSPACE)),
        file_access_disable_write_tool_approval=True,
        disable_web_search=True, disable_file_memory=True,
        disable_mode=True,
        loop_max_iterations=12)

    session = harness.create_session()
    await harness.run(TASK, session=session)
    calls_b, files_b = list(CALLS), list(WORKSPACE.iterdir())

    # ---- THE DIFFERENCE --------------------------------------------------
    mine = {t.name for t in TOOLS}
    borrowed = [c for c in calls_b if c not in mine]
    todo = session.state.get("todo", {}).get("items", [])

    print(f"{'':29}{'plain agent':<22}harness")
    print(f"   {'tools we gave it':26}{len(mine):<22}{len(mine)}")
    print(f"   {'tools it brought itself':26}{0:<22}{len(set(borrowed))}")
    print(f"   {'tool calls made':26}{len(calls_a):<22}{len(calls_b)}")
    print(f"   {'planned its own work':26}{'no':<22}{len(todo)} todos, "
          f"{sum(i['is_complete'] for i in todo)} done")
    print(f"   {'left an artifact':26}{str([p.name for p in files_a]):<22}"
          f"{[p.name for p in files_b]}")
    print(f"\n   the harness called, unprompted : {sorted(set(borrowed))}")
    print(f"   its plan:")
    for item in todo:
        print(f"     [{'x' if item['is_complete'] else ' '}] {item['title']}")

    print(f"\n   PLAIN AGENT, in its own words : {answer_a.text.splitlines()[0][:]}")
    report = WORKSPACE / "triage_report.md"
    if report.exists():
        print(f"\n   {report.name} — {report.stat().st_size} bytes, written by nobody at this keyboard:")
        for line in report.read_text().splitlines():
            print(f"     {line[:76]}")


run(main())
