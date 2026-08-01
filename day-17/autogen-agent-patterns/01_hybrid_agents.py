# hybrid agent in autogen-agent-patterns
# Python rules + AssistantAgent = a hybrid agent that can reason and code

import time
from _agents import agent_step, get_client, run

POLICY = "Hex Retail Accepts audio returns within 21 days of delivery."

ORDERS = {
    "AR-90455": {"days": 12, "faulty": True, "item": "Hex Studio Headphones"},
    "AR-90456": {"days": 34, "faulty": False, "item": "Hex Studio Buds Mk II"},
    "AR-90457": {"days": 5, "faulty": False, "item": "Hex Studio Headphones"},
    "AR-90458": {"days": 40, "faulty": True, "item": "Hex Studio Buds Mk II"},
}

TICKETS = [
    ("AR-90455", "Left earbud stopped working. Want to send it back"),
    ("AR-90456", "Changed my mind, want to return the headphones"),
    ("AR-90457", "Wrong color, please refund my order"),
    ("AR-90458", "These are faulty and I am well outside 21 days - where do I stand?"),
    ("AR-99999", "Please refund my order"),
    ("AR-90455", "My daughter dropped the headphones in water, can I have them repaired?")
]

def decide_by_rules(order_id: str, message: str) -> tuple[str, str] | None:
    """Return (decision, reason) when the rules are CERTAIN, else None.
    Returning None is the important part: it is the light comes on the dark side of the rules,
    and the agent will be called to adjudicate.
    """
    record = ORDERS.get(order_id)
    if record is None:
        return ("REJECT", "no such order in our system")
    if record["faulty"] and record["days"] <= 21:
        return ("APPROVE", f"faulty, {record['days']} days - inside the 21-day window")
    if not record["faulty"] and record["days"] <= 21:
        return ("APPROVE", f"{record['days']} days - inside the 21-day window")
    if not record["faulty"] and record["days"] > 21:
        return ("REJECT", f"{record['days']} days - outside the 21-day window")
    return None  # the rules give up, and the agent will be called to adjudicate


# an autogen agent will be called only when the rules give up.
JUDGEMENT = (
    "You are Hex Retail's senior returns adjudicator."
    f"{POLICY} Faulty good are additionally covered by a two-year warranty. "
    "You handle only the cases the rules could not settle. "
    "Reply in at most two sentences: the decision, then the reason."
)

async def main():
    client = get_client()
    by_rule = 0
    by_model = 0
    rule_seconds = 0.0
    model_seconds = 0.0

    print("SIX TICKETS THROUGH A HYBRID AGENT (RULES + AUTOGEN AGENT)")
    print()
    for order_id, message in TICKETS:
        started = time.perf_counter()
        verdict = decide_by_rules(order_id, message)
        elapsed = time.perf_counter() - started
        rule_seconds += elapsed

        if verdict is not None:
            by_rule += 1
            decision, reason = verdict
            print(f" [RULE] {order_id}: {decision} ({reason})")
            print(f"         {elapsed * 1000:.3f}ms, 0 tokens")
        else:
            by_model += 1
            started = time.perf_counter()
            answer = await agent_step(
                name="adjudicator", instruction=JUDGEMENT,
                task=f"Order {order_id}: {ORDERS[order_id]}\nCustomer wrote: {message}",
                client=client)
            elapsed = time.perf_counter() - started
            model_seconds += elapsed
            print(f" [MODEL] {order_id} escalated - the rules had no answer")
            print(f"         {answer}")
            print(f"         {elapsed:.2f}s, one model call")
        print()

    await client.close()

    total = by_rule + by_model
    print("THE SPLIT BETWEEN RULES AND MODEL:")
    print(f" settled by rules: {by_rule} of {total} ({by_rule / total * 100:.0f}%)")
    print(f" escalated to LLM: {by_model} of {total} ({by_model / total * 100:.0f}%)")
    print(f" time in rules: {rule_seconds * 1000:.3f}ms total")
    print(f" time in model: {model_seconds * 1000:.3f}s total")
    if by_model:
        print(f" the model tool ~ {model_seconds / max(rule_seconds, 1e-6):.0f}x slower than the rules")
    print()

    order_id, message = TICKETS[-1]
    verdict = decide_by_rules(order_id, message)
    print("THE TICKET THAT SHOULD WORRY YOU")
    print(f" customer wrote: {message}")
    print(f" they asked for: a REPAIR. They said explicitly they do not want a refund.")
    print(f" the rules said: {verdict[0] if verdict else 'escalated'} - "
          f"{verdict[1] if verdict else ''}")
    print()

run(main())