import asyncio
import json
import os
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Annotated

from agent_framework import Agent, Message
from agent_framework.observability import enable_instrumentation
from agent_framework.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from langfuse import Langfuse, propagate_attributes
from pydantic import Field

load_dotenv()
MODEL = os.environ["OLLAMA_MODEL"]
BASE_URL = os.environ["OLLAMA_BASE_URL"]
API_KEY = os.environ["OLLAMA_API_KEY"]

langfuse = Langfuse()
enable_instrumentation(enable_sensitive_data=True)

with urllib.request.urlopen(f"{BASE_URL}/models") as response:
    AVAILABLE = [m["id"] for m in json.load(response)["data"]]

if MODEL not in AVAILABLE:
    raise SystemExit(
        f"[ollama] '{MODEL}' is not on Ollama Cloud. Available:\n "
        + "\n ".join(sorted(AVAILABLE))
    )

def check_key() -> None:
    """Send the cheapest possible chat request just to see if the key is accepted."""
    request = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=json.dumps({"model": MODEL, "max_tokens": 1,
                         "messages": [{"role": "user", "content": "hello"}]}).encode(),
        headers={"Authorization": f"Bearer {API_KEY}",
                 "Content-Type": "application/json"}
    )
    try:
        urllib.request.urlopen(request, timeout=60).read()
    except urllib.error.HTTPError as error:
        if error.code not in (401, 403):
            raise
        detail = error.read().decode(errors="replace")
        env_file = ".env"

        if error.code == 401:
            raise SystemExit(
                f"\n[ollama] Ollama Cloud does not recognise OLLAMA_API_KEY"
                f"(HTTP 401).\n"
                f" The key ends '{API_KEY}'"
                f" and put it in {env_file}\n"
            ) from None

        raise SystemExit(
            f"\n[ollama] Your key is valid, but '{MODEL}' is not included in your plan."
            f" (HTTP 401)\n"
            f" Ollama said {detail.strip()}"
        ) from None

check_key()
print(f"[ollama] {MODEL} via {BASE_URL} - key accepted, {len(AVAILABLE)} models offered")

ACCOUNTS = {"SB-9001": 84_215.50, "SB-9002": 12_430.00, "SB-9003": 3_46_890.25}

def check_balance(account_id: Annotated[str, Field(description="Account id, e.g. SB-9001")]) -> str:
    """Look up the balance of a Meridian Bank Account."""
    balance = ACCOUNTS.get(account_id.upper())
    return f"{account_id}: Rs{balance:,.2f}" if balance else f"No account {account_id}"

agent = Agent(
    OpenAIChatCompletionClient(model=MODEL, api_key=API_KEY, base_url=BASE_URL),
    "You are Meridian Bank's Acssistant capable of checking the Account Balance of a customer. "
    "You will be given an account id, and you will respond with the balance of that account." \
    "If the account id is not found, you will respond with 'No account {account_id}'."
    "Branches open Monday to Friday, 9am to 5pm. Saturday 9am to 1pm. Closed on Sunday and public holidays."
    "Savings pays 3% interest per year, and Fixed Deposits pay 6% interest per year. "
    "You will not provide any other information, and you will not make up any information." \
    "Be brief and concise in your responses.",
    name="Meridian Bank Assistant",
    tools=[check_balance]
)

# turns whatever gradio hands us as a message into a plain string
def plain_text(content: object) -> str:
    """Flatten one Gradio history"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(plain_text(part) for part in content)
    if isinstance(content, dict):
        return str(content.get("text") or content.get("content") or "")
    return str(content)

def new_session() -> dict:
    """Fresh, empty running totals for one conversation"""
    return {"id": f"chat-{uuid.uuid4().hex[:12]}", "turns": 0,
            "tokens_in": 0, "tokens_out": 0, "seconds":0.0}

def session_url(trace_id: str, session_id: str) -> str:
    """Link to the session view in langfuse."""
    trace_url = langfuse.get_trace_url(trace_id=trace_id) or ""
    return f"{trace_url.rsplit('/traces/', 1)[0]}/sessions/{session_id}"


def ask(message: str, history: list, session: dict | None = None) -> tuple[str, str]:
    session = new_session() if session is None else session
    past = [Message(m["role"], [plain_text(m["content"])]) for m in history]
    started = time.perf_counter()

    with propagate_attributes(session_id=session["id"]), \
            langfuse.start_as_current_observation(name="chat turn", as_type="agent") as span:
        trace_id = span.trace_id
        try:
            result = asyncio.run(agent.run([*past, Message("user", [message])]))
        except Exception as error:
            span.update(level="ERROR", status_message=str(error))
            langfuse.flush()
            return (f"That turn failed: {type(error).__name__}",
                    f"Error {error}\n\n"
                    f"({langfuse.get_trace_url(trace_id=trace_id)})")

    elapsed = time.perf_counter() - started
    langfuse.flush()

    used = result.usage_details or {}
    token_in = used.get("input_token_count") or 0
    tokens_out = used.get("output_token_count") or 0

    session["turns"] += 1
    session["tokens_in"] += token_in
    session["tokens_out"] += tokens_out
    session["seconds"] += elapsed

    report = (f"**This turn** - **{token_in}** tokens in - **{tokens_out:,}** out"
              f"**{elapsed:.2f}s**\n\n"
              f"**All {session['turns']} turn(s)** - **{session['tokens_in']:,}** in"
              f"**{session['tokens_out']:,}** out"
              f"**{session['tokens_in'] + session['tokens_out']:,}** total"
              f"**{session['seconds']:.2f}s**\n\n"
              f"[This turn's trace]({langfuse.get_trace_url(trace_id=trace_id)})"
              f"[The whole conversation]({session_url(trace_id, session['id'])})")
    return result.text, report

if __name__ == "__main__":
    session, history = new_session(), []
    for question in ["What's the balance on SB-9001?", "And SB-9003"]:
        answer, summary = ask(question, history, session)
        history += [{"role": "user", "content": question,
                    "role": "assistant", "content": answer}]
        print(f"\n {question}\n{answer}\n\n{summary}")




    