import asyncio
import os
from typing import Any
from dotenv import load_dotenv
from agent_framework_openai import OpenAIChatClient

load_dotenv()

def _azure_alive() -> bool:
    """One cheap real call - is the training subscription up right now?"""
    import json
    import urllib.request
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
    key, model = os.environ.get("AZURE_OPENAI_API_KEY"), os.environ.get("AZURE_OPENAI_MODEL")
    if not (endpoint and key and model):
        return False
    request = urllib.request.Request(
        f"{endpoint}/openai/v1/responses",
        data=json.dumps({"model": model, "input": "ok"}).encode(),
        headers={"api-key": key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status == 200
    except Exception:
        return False

BACKEND = "azure" if _azure_alive() else "ollama"
MODEL = (os.environ["AZURE_OPENAI_MODEL"] if BACKEND == "azure"
         else os.environ.get("OLLAMA_MODEL", "gemma4:e2b"))

def get_client(**overrides: Any) -> OpenAIChatClient:
    """One chat client, pointed at whichever backend is alive."""
    if BACKEND == "azure":
        settings: dict[str, Any] = dict(model=MODEL, api_key=os.environ["AZURE_OPENAI_API_KEY"],
                            base_url=os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/") + "/openai/v1/")
    else:
        settings: dict[str, Any] = dict(model=MODEL, api_key="ollama",
                            base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434") + "/v1")
    settings.update(overrides)
    return OpenAIChatClient(**settings)

def banner(title: str) -> None:
    """Print a banner to the console."""
    print("=" * 80)
    print(f" {title}")
    print("=" * 80)
    print(f"Backend: {BACKEND}, Model: {MODEL}")
    print("=" * 80)

def run(coro):
    """Run a coroutine in an asyncio event loop."""
    return asyncio.run(coro)


POLICY = {"Hex retail accepts audio returns within 21 days of delivery."
          "Faulty goods carry a two year warranty. Faulty returns are free."}

ORDERS = {"HX-90455": {"days": 12, "faulty": True, "item": "Hex Studio headphones"},
          "HX-90456": {"days": 34, "faulty": False, "item": "Hex Buds Mk II"}}
