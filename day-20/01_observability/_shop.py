"""Hex Retail — the shop itself. NO observability anywhere in this file.

Every step_*.py imports this unchanged. That is the point of the project: the
business logic never learns it is being observed.
"""

import asyncio, os, warnings
from typing import Annotated, Any

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv()); warnings.filterwarnings("ignore")

POLICY = ("Hex Retail accepts audio returns within 21 days of delivery. "
          "Faulty goods carry a two-year warranty. Faulty returns are free.")

ORDERS = {"HX-90455": ("Hex Studio headphones", 129.99, 12, True),   # item, paid, days ago, faulty
          "HX-90456": ("Hex Buds Mk II", 59.00, 34, False),
          "HX-90457": ("Hex Desk Mic", 84.50, 6, False)}

STOCK = {"Hex Studio headphones": 4, "Hex Buds Mk II": 0, "Hex Desk Mic": 17}

ESCALATED: list[str] = []                                 # tickets raised for a human


def _azure_alive() -> bool:
    """One cheap real call — is the training subscription up right now?"""
    import json, urllib.request
    end = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
    key, model = os.environ.get("AZURE_OPENAI_API_KEY"), os.environ.get("AZURE_OPENAI_MODEL")
    if not (end and key and model):
        return False
    req = urllib.request.Request(f"{end}/openai/v1/responses",
                                 data=json.dumps({"model": model, "input": "ok"}).encode(),
                                 headers={"api-key": key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status == 200
    except Exception:
        return False


BACKEND = "azure" if _azure_alive() else "ollama"
MODEL = (os.environ["AZURE_OPENAI_MODEL"] if BACKEND == "azure"
         else os.environ.get("OLLAMA_MODEL", "gemma4:12b"))


def look_up_order(order_id: Annotated[str, "an order id like HX-90455"]) -> str:
    """Look up a customer order: item, price paid, days since delivery, fault status."""
    item, paid, days, faulty = ORDERS.get(order_id, ("unknown", 0.0, 0, False))
    if item == "unknown":
        raise ValueError(f"{order_id} is not a Hex Retail order")   # step 5 needs a real failure
    return f"{order_id}: {item}, USD {paid}, delivered {days} days ago, faulty={faulty}"


def check_stock(item: Annotated[str, "a product name"]) -> str:
    """Check how many units of a product are in stock."""
    return f"{item}: {STOCK.get(item, 0)} in stock"


def escalate(reason: Annotated[str, "why a human is needed"]) -> str:
    """Raise a ticket for a human agent. Use only when you genuinely cannot help."""
    ESCALATED.append(reason)
    return f"Ticket raised: {reason}"


TOOLS = [look_up_order, check_stock, escalate]
INSTRUCTIONS = (f"You are Hex Retail's customer support assistant. {POLICY} "
                "Never answer about a specific ORDER without calling look_up_order first. "
                "For product availability use check_stock. Be warm and brief — "
                "two sentences at most. If you cannot help, escalate.")


def client(**kw: Any):
    """One chat client, pointed at whichever backend is alive. Imported late on purpose."""
    from agent_framework_openai import OpenAIChatClient
    if BACKEND == "azure":
        s: dict[str, Any] = dict(model=MODEL, api_key=os.environ["AZURE_OPENAI_API_KEY"],
                                 base_url=os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/") + "/openai/v1/")
    else:
        s = dict(model=MODEL, api_key="ollama",
                 base_url=os.environ.get("OLLAMA_HOST", "http://localhost:11434") + "/v1")
    s.update(kw)
    return OpenAIChatClient(**s)


def support_agent():
    """The Hex Retail support agent. Knows nothing about telemetry."""
    return client().as_agent(name="hex-support", tools=TOOLS, instructions=INSTRUCTIONS)


def history_to_messages(history: list[dict]):
    """Turn Gradio's chat history into Agent Framework messages."""
    from agent_framework import Message
    return [Message(h["role"], [h["content"]]) for h in history
            if isinstance(h.get("content"), str) and h.get("role") in ("user", "assistant")]


#  REAL Azure list prices, fetched from Microsoft's public Retail Prices API.
#  See _pricing.py for what this is (list price) and is not (your contract).
from _pricing import rates as _rates                      # noqa: E402

RATES, RATES_SOURCE = _rates(MODEL)                       # USD per MILLION tokens


def usage(spans) -> dict[str, float]:
    """Input, cached and output tokens plus USD cost across the BILLED `chat` spans."""
    got = lambda s, k: int(str((s.attributes or {}).get(f"gen_ai.usage.{k}", 0) or 0))
    billed = [s for s in spans if s.name.startswith("chat")]
    t: dict[str, float] = {"calls": len(billed), "in": 0, "cached": 0, "out": 0}
    for span in billed:
        t["in"] += got(span, "input_tokens")
        t["cached"] += got(span, "cache_read.input_tokens")
        t["out"] += got(span, "output_tokens")
    t["usd"] = ((t["in"] - t["cached"]) * RATES["in"] + t["cached"] * RATES["cached"]
                + t["out"] * RATES["out"]) / 1_000_000
    return t


def run(coro):
    return asyncio.run(coro)
