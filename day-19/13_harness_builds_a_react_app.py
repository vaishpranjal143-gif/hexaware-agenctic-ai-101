import os
import shutil
import subprocess
import webbrowser
from pathlib import Path

from agent_framework import (FileSystemAgentFileStore,
                             FunctionInvocationContext,
                             create_harness_agent, tool)

from _maf import POLICY, banner, get_client, run

banner("THE HARNESS BUILDS A REACT APP")

QUEUE = {
    "HX-90455": {"days": 12, "faulty": True,  "item": "Hex Studio headphones", "paid": 129.99},
    "HX-90456": {"days": 34, "faulty": False, "item": "Hex Buds Mk II",        "paid": 59.00},
    "HX-90457": {"days": 6,  "faulty": False, "item": "Hex Studio headphones", "paid": 129.99},
    "HX-90458": {"days": 27, "faulty": True,  "item": "Hex Desk Mic",          "paid": 84.50},
}

CALLS: list[str] = []
WORKSPACE = Path(__file__).parent / "_react_workspace"
PAGE = WORKSPACE / "dashboard.html"


async def watch(context: FunctionInvocationContext, next):
    """Record the name of every tool that runs — including ones we did not write."""
    CALLS.append(context.function.name)
    await next()


@tool
def open_returns() -> str:
    """Every return request currently waiting, with item, price, age and fault status."""
    return "\n".join(f"{oid}: {r['item']}, GBP {r['paid']}, delivered {r['days']} "
                     f"days ago, faulty={r['faulty']}" for oid, r in QUEUE.items())


BRIEF = f"""Build a returns dashboard for Hex Retail as a single HTML file.

STEP 1. Call open_returns to get the real data. Do not invent orders.
STEP 2. Decide ACCEPT or REJECT for each one under this policy: {POLICY}
STEP 3. Write the whole thing to dashboard.html as ONE self-contained file.

The file must:
- load React 18, ReactDOM 18 and Babel standalone from unpkg CDN script tags
- put the JSX in <script type="text/babel"> and render into <div id="root">
- define a React component that renders one CARD per return, showing the order
  id, item, price, age in days, an ACCEPT or REJECT badge, and a one-line reason
- show a header with the total GBP being refunded across accepted returns
- let the user filter to All / Accepted / Rejected with React useState
- look genuinely good: dark background, readable web-safe font stack, rounded
  cards, subtle borders, green badges for ACCEPT and red for REJECT, a
  responsive CSS grid, and hover states. All CSS inline in a <style> tag.

Write the file once, complete and valid. Then read it back to confirm it saved."""

CHECKS = {
    "React from CDN": "unpkg.com/react@18",
    "ReactDOM from CDN": "unpkg.com/react-dom@18",
    "Babel standalone": "babel",
    "a JSX script block": 'type="text/babel"',
    "a root element": 'id="root"',
    "React renders into it": "createRoot",
    "useState for filtering": "useState",
    "inline styling": "<style",
}

TOTAL = "344.48"

CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]
ON_PATH = ["google-chrome", "chromium", "chromium-browser", "msedge", "chrome"]


def find_browser() -> str:
    """Return a runnable browser path, or an empty string if there is none."""
    for candidate in CANDIDATES:
        if candidate and Path(candidate).exists():
            return candidate
    for name in ON_PATH:
        found = shutil.which(name)
        if found:
            return found
    return ""


def rendered_dom() -> str:
    """Open the page headlessly and return the DOM *after* JavaScript ran."""
    browser = find_browser()
    if not browser:
        return ""
    done = subprocess.run([browser, "--headless", "--disable-gpu", "--no-sandbox",
                           "--dump-dom", "--virtual-time-budget=6000", PAGE.as_uri()],
                          capture_output=True, text=True, timeout=90)
    return done.stdout


async def main():
    shutil.rmtree(WORKSPACE, ignore_errors=True)
    WORKSPACE.mkdir(parents=True)

    agent = create_harness_agent(
        client=get_client(), name="frontend", tools=[open_returns], middleware=[watch],
        agent_instructions="You are a senior frontend engineer. You write clean, "
                           "self-contained React and you finish the job in one file.",
        file_access_store=FileSystemAgentFileStore(root_directory=str(WORKSPACE)),
        file_access_disable_write_tool_approval=True,
        disable_web_search=True, disable_file_memory=True,
        disable_mode=True,
        loop_max_iterations=20)

    session = agent.create_session()
    await agent.run(BRIEF, session=session)

    if not PAGE.exists():
        print("   (no file on the first attempt — asking once more)\n")
        await agent.run(BRIEF, session=agent.create_session())

    todo = session.state.get("todo", {}).get("items", [])
    print("   its plan:")
    for item in todo:
        print(f"     [{'x' if item['is_complete'] else ' '}] {item['title']}")

    mine = {"open_returns"}
    borrowed = sorted({c for c in CALLS if c not in mine})
    print(f"\n   our tools     : {sorted(mine)}")
    print(f"   its own tools : {borrowed}")
    print(f"   files created : {[p.name for p in WORKSPACE.iterdir()]}")

    if not PAGE.exists():
        print("\n   no dashboard.html was produced"); return
    html = PAGE.read_text()
    print(f"\n   dashboard.html — {len(html):,} characters, {len(html.splitlines())} lines\n")

    print("   STRUCTURAL CHECKS — is the right machinery in the file?")
    for label, needle in CHECKS.items():
        print(f"     {'PASS' if needle.lower() in html.lower() else 'MISS'}  {label}")
    present = [oid for oid in QUEUE if oid in html]
    print(f"     {len(present)}/{len(QUEUE)} real order ids present : {present}")

    print("\n   RENDER CHECK — does it actually run in a browser?")
    dom = rendered_dom()
    if not dom:
        print("     SKIPPED — no Chromium-based browser found, so this was NOT verified")
        return
    in_source = TOTAL in html
    in_dom = TOTAL in dom
    print(f"     total '{TOTAL}' in the SOURCE file  : {in_source}")
    print(f"     total '{TOTAL}' in the RENDERED DOM : {in_dom}")
    print(f"     -> React really executed            : {(not in_source) and in_dom}")
    print(f"     DOM grew {len(html):,} -> {len(dom):,} characters as components mounted")

    print(f"\n   open it with:  open {PAGE}")
    try:
        answer = input("   open it now? [y/N]: ").strip().lower()
    except EOFError:
        answer = "n"
    if answer == "y":
        webbrowser.open(PAGE.as_uri())


run(main())
