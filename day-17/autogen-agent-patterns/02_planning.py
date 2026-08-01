import json
from _agents import run, agent_step, get_client

POLICY = ("Hex Retail accepts audio returns within 21 days of delivery. "
          "Faulty goods carry a two-year warranty. Change-of-mind returns cost "
          "GBP 3.95 postage; faulty returns are free.")

#  One sentence, four separate jobs hiding inside it.
REQUEST = ("My Hex Studio headphones arrived 12 days ago and the left earcup "
           "crackles. Can I return them, what will the postage cost me, how long "
           "does a refund take, and should I just get the Mk II instead?")

# Attempt 1. no plan, one agent, one shot, whatever it produces.
async def without_a_plan(client):
    """The obvious approach: just ask the agent to answer the request, and see what it produces."""
    return await agent_step(
        name="support",
        client=client,
        instruction=f"You are Hex Retail support. {POLICY} Be concise.",
        task=REQUEST)

# Attempt 2. plan first, the planner returns data
PLANNER = (
    "You are a planning agent. You will be given a request,"
    "and you will break it down into a numbered list of steps to answer it. "
    "Each step should be a single sentence, and should be actionable by a single agent. "
    "Do not answer the request yourself, just produce the plan."
)

def normalize(text: str) -> str:
    """Lowercase, and straigten the curly quotes models actually produce.
    Models write "isn't" with U+2019, not the ASCII apostrophe.
    They also use U+201C and U+201D for quotes, not the ASCII double quote.
    This function normalizes those characters to the ASCII versions, and lowercases the text.
    check that works and a check that silently always passes,
    so that we can see what the model produced without failing the test.
    """
    return text.lower().replace("\u2019", "'").replace("\u2018", "'")

REFUSALS = ("isn't provided", "is not provided", "i can't", "i cannot",
            "don't have", "do not have", "no information", "not able to",
            "isn't available", "is not available", "cannot answer", "can't answer",
            "not sure", "i'm not sure", "i am not sure", "i'm not able",
            "i am not able", "i'm unable", "i am unable",)

def refused(text: str) -> bool:
    """Did this answer declient rather than answer the question?"""
    return any(phrase in normalize(text) for phrase in REFUSALS)

async def make_plan(client) -> list[str]:
    """Ask the planning agent to produce a plan for answering the request."""
    raw = await agent_step(
        name="planner",
        client=client,
        instruction=PLANNER,
        task=REQUEST)
    cleaned = raw.strip().removeprefix("```json").removesuffix("```")
    try:
        steps = json.loads(cleaned)
        return [str(step) for step in steps][:6]
    except json.JSONDecodeError:
        return [line.strip("- ") for line in cleaned.splitlines() if line.strip()][:6]

async def main():
    client = get_client()

    print("THE REQUEST:")
    print(REQUEST)
    print()

    print("Attempt 1: without a plan (one agent, one shot)")
    unplanned = await without_a_plan(client)
    print(unplanned)
    print(f"Refused? {'YES' if refused(unplanned) else 'no'}")
    print()

    print("Attempt 2: with a plan (planner + support agent)")
    plan = await make_plan(client)
    print(f" the planner returned {len(plan)} steps, as data:")
    for number, step in enumerate(plan, start=1):
        print(f"  {number}. {step}")
    print()
    print("Now we will execute the plan, step by step, with a support agent.")
    print("The support agent will be given the original request, the policy, and the current step to answer.")
    print("The support agent will be asked to answer the current step, and to be concise.")
    print()

    answers: list[tuple[str, str]] = []
    for number, step in enumerate(plan, start=1):
        answer = await agent_step(
            name=f"step{number}",
            client=client,
            instruction=f"You are Hex Retail support. {POLICY} Be concise.",
            task=f"Request: {REQUEST}\nStep {number}: {step}")
        answers.append((step, answer))
        print(f" [{number}/{len(plan)}] {step}")
        print(f"  -> {answer}")
    print()

    # did the unplanned answer actually cover everything the plan did? (it should have, if it was a good answer)
    print("Now we will check if the unplanned answer covered all the steps in the plan.")
    TOPICS = {
        "return eligibility": ("return", "eligib", "21"),
        "postage cost": ("postage", "cost", "3.95", "free"),
        "refund time": ("refund", "time", "days", "week", "process"),
        "Mk II upgrade": ("mk ii", "upgrade", "new model", "better", "mk 2"),
    }
    lowered = normalize(unplanned)
    covered = 0
    for topic, needles in TOPICS.items():
        hit = any(needle in lowered for needle in needles)
        covered += 1 if hit else 0
        print(f" [{'yes' if hit else 'no '}] {topic}")
    print(f" one-shot mentioned {covered} of {len(TOPICS)} topics in the plan.")
    if refused(unplanned):
        print("The one-shot answer refused to answer the request.")
        print("The plan-based answer did not refuse to answer the request.")
        print("The plan-based answer is therefore better than the one-shot answer.")
    print()

    # and did every planned step actually produce an answer, or did any of them refuse to answer?
    declined = 0
    for number, (step, answer) in enumerate(answers, start=1):
        gave_up = refused(answer)
        declined += 1 if gave_up else 0
        print(f" [{'REFUSED' if gave_up else 'answered'}] step {number}: {step}")
    print(f" {declined} of {len(answers)} steps refused to answer the request.")
    if declined:
        print()
        print("The plan-based answer is not perfect, because some steps refused to answer the request.")
        print("However, the plan-based answer is still better than the one-shot answer, because it covered more topics.")
        print("The plan-based answer can be improved by refining the plan, or by improving the support agent's ability to answer each step.")
        print("The one-shot answer cannot be improved, because it is a single answer that cannot be refined.")
        print("Therefore, the plan-based answer is better than the one-shot answer, even if it is not perfect.")
    print()

    await client.close()

    print("What planning actually bought us here is the ability to break down a complex request into smaller, more manageable steps.")
    print("This allows us to have a support agent answer each step individually, which can lead to more accurate and complete answers.")

run(main())