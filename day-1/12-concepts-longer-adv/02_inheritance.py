"""
╔══════════════════════════════════════════════════════════════════════╗
║  CONCEPT 2 — INHERITANCE                                            ║
║  File    : 02_inheritance.py                                        ║
║  Run     : python 02_inheritance.py                                 ║
╠══════════════════════════════════════════════════════════════════════╣
║  WHAT IS IT?                                                        ║
║  A child class automatically gets all the attributes and methods    ║
║  of its parent class. It can add new things or override existing    ║
║  ones, without duplicating the parent's code.                       ║
║                                                                     ║
║  KEY RULES:                                                         ║
║    Always call super().__init__() first in child __init__           ║
║    Override a method to change its behaviour in the child           ║
║    Use super().method() to call the parent version                  ║
║                                                                     ║
║  AGENTIC AI USE CASE: Agent Hierarchy                               ║
║  All agents share: name, model, memory, turn counter, logging.      ║
║  Specialists (Research, Coder, Manager) add their own behaviour.    ║
╚══════════════════════════════════════════════════════════════════════╝
"""

from datetime import datetime


# ─────────────────────────────────────────────────────────────────────
#  PART 1 — THE PROBLEM: Code duplication without inheritance
# ─────────────────────────────────────────────────────────────────────

print("=" * 60)
print("PART 1 — THE PROBLEM (Duplicated code, no parent class)")
print("=" * 60)

class BadResearchAgent:
    """Every agent copies the same __init__ and memory logic. Terrible."""

    def __init__(self, name, model, sources):
        self.name    = name        # ← copied in every agent class
        self.model   = model       # ← copied in every agent class
        self.memory  = []          # ← copied in every agent class
        self.turn    = 0           # ← copied in every agent class
        self.sources = sources

    def run(self, task):
        return f"Researching: {task}"


class BadCoderAgent:
    """Exact same __init__ fields duplicated — any change must be made in BOTH."""

    def __init__(self, name, model, language):
        self.name     = name       # ← same duplication
        self.model    = model      # ← same duplication
        self.memory   = []         # ← same duplication
        self.turn     = 0          # ← same duplication
        self.language = language

    def run(self, task):
        return f"Coding in {self.language}: {task}"


print("Problem: Both agents copy the same 4 lines of __init__ code.")
print("If we add 'self.session_id = uuid4()' we must change BOTH classes.")
print("With 10 agent types, this becomes unmanageable.\n")


# ─────────────────────────────────────────────────────────────────────
#  PART 2 — THE SOLUTION: Inheritance with a base class
# ─────────────────────────────────────────────────────────────────────

print("=" * 60)
print("PART 2 — THE SOLUTION (Inheritance)")
print("=" * 60)


class BaseAgent:
    """
    The foundation for every agent in the system.

    DEFINED ONCE HERE, available to all subclasses:
        name, model, memory, turn  — shared state
        remember()                 — stores any string to memory
        recall()                   — returns all stored memories
        introduce()                — works for any subclass dynamically
        step()                     — template: increment → run() → remember
        run()                      — hook: subclasses MUST override this
    """

    def __init__(self, name: str, model: str):
        self.name   = name
        self.model  = model
        self.memory = []            # every agent gets their own memory list
        self.turn   = 0             # counts how many tasks completed

    # ── Shared methods — defined once, inherited by all ───────────────

    def remember(self, content: str):
        """Save something to this agent's memory. Works for any agent type."""
        self.memory.append({
            "turn"    : self.turn,
            "content" : content,
            "at"      : datetime.now().strftime("%H:%M:%S"),
        })

    def recall(self) -> list:
        """Return all stored memory items (content only)."""
        return [item["content"] for item in self.memory]

    def introduce(self) -> str:
        """
        Uses self.__class__.__name__ so it adapts to the real subclass type.
        ResearchAgent prints 'ResearchAgent', CoderAgent prints 'CoderAgent'.
        We write this once — it works correctly for all children.
        """
        return (
            f"I am {self.name}, "
            f"a {self.__class__.__name__} "          # dynamic — reflects actual type
            f"powered by {self.model}."
        )

    def step(self, task: str) -> str:
        """
        Template Method pattern — the exact same flow for ALL agents:
          1. Increment turn counter
          2. Call self.run(task) — polymorphic: each subclass provides its own
          3. Remember the result
          4. Return the result

        By defining the flow here, every subclass gets it for free.
        Subclasses only need to implement run().
        """
        self.turn += 1
        result = self.run(task)    # ← calls the subclass version automatically
        self.remember(result)
        return result

    def run(self, task: str) -> str:
        """
        HOOK — subclasses MUST override this.
        Leaving it as NotImplementedError catches any forgotten override early.
        """
        raise NotImplementedError(
            f"'{self.__class__.__name__}' must implement run(task). "
            f"BaseAgent.run() should never be called directly."
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(name='{self.name}', "
            f"turns={self.turn}, "
            f"memory_items={len(self.memory)})"
        )


# ─────────────────────────────────────────────────────────────────────
#  CHILD CLASSES — each specialises BaseAgent
# ─────────────────────────────────────────────────────────────────────

class ResearchAgent(BaseAgent):
    """
    Specialises in searching sources and synthesising findings.

    INHERITS from BaseAgent:
        name, model, memory, turn
        remember(), recall(), introduce(), step(), __repr__

    ADDS:
        sources         — list of data sources to search
        search_history  — track all queries made
        searches_done() — count of searches performed

    OVERRIDES:
        run()           — research-specific behaviour
    """

    def __init__(self, name: str, model: str, sources: list):
        super().__init__(name, model)    # ← ALWAYS call super() first
        #                                    This sets up name, model, memory, turn
        self.sources        = sources
        self.search_history = []

    def run(self, task: str) -> str:
        """
        Override: research-specific behaviour.
        Called automatically by self.step(task) from BaseAgent.
        """
        self.search_history.append(task)
        source_list = ", ".join(self.sources)

        return (
            f"[Research | Turn {self.turn}]\n"
            f"  Query   : {task}\n"
            f"  Sources : {source_list}\n"
            f"  Finding : Retrieved findings on '{task}' "
            f"from {len(self.sources)} source(s)."
        )

    def searches_done(self) -> int:
        """Extra method specific to ResearchAgent — not in BaseAgent."""
        return len(self.search_history)


class CoderAgent(BaseAgent):
    """
    Specialises in writing and explaining code.

    INHERITS from BaseAgent:
        Everything — name, model, memory, turn, all shared methods

    ADDS:
        language        — preferred programming language
        snippets_made   — list of generated code snippets

    OVERRIDES:
        run()           — code-generation behaviour
    """

    def __init__(self, name: str, model: str, language: str = "python"):
        super().__init__(name, model)    # ← super() sets name, model, memory, turn
        self.language      = language
        self.snippets_made = []

    def run(self, task: str) -> str:
        """Override: coding-specific behaviour."""
        snippet = (
            f"def solution():\n"
            f"    \"\"\"{task}\"\"\"\n"
            f"    pass  # TODO: implement"
        )
        self.snippets_made.append(snippet)

        indented = "\n".join(f"    {line}" for line in snippet.split("\n"))
        return (
            f"[Code | {self.language} | Turn {self.turn}]\n"
            f"  Task    : {task}\n"
            f"  Output  :\n{indented}"
        )

    def last_snippet(self) -> str:
        """Extra method specific to CoderAgent."""
        return self.snippets_made[-1] if self.snippets_made else ""


class ManagerAgent(BaseAgent):
    """
    Orchestrates a team of other agents.
    Delegates tasks to the right specialist. Does NO work itself.

    INHERITS from BaseAgent:
        Everything

    ADDS:
        team            — list of child agents
        delegation_log  — record of who handled what

    OVERRIDES:
        run()           — routing/delegation logic
    """

    def __init__(self, name: str, model: str, team: list):
        super().__init__(name, model)
        self.team           = team
        self.delegation_log = []

    def run(self, task: str) -> str:
        """Override: route the task to the right specialist."""
        task_lower = task.lower()

        # Simple keyword routing
        if any(kw in task_lower for kw in ["code", "write", "function", "implement", "script"]):
            chosen = next((a for a in self.team if isinstance(a, CoderAgent)), None)
        else:
            chosen = next((a for a in self.team if isinstance(a, ResearchAgent)), None)

        chosen = chosen or self.team[0]    # fallback to first agent
        self.delegation_log.append({"task": task, "delegated_to": chosen.name})

        # step() handles memory for the child agent automatically
        child_result = chosen.step(task)
        indented = "\n".join(f"      {line}" for line in child_result.split("\n"))

        return (
            f"[Manager | Turn {self.turn}]\n"
            f"  Delegated to: {chosen.name} ({chosen.__class__.__name__})\n"
            f"  Result:\n{indented}"
        )

    def delegation_summary(self) -> list:
        """Show who handled what."""
        return [(d["delegated_to"], d["task"][:40]) for d in self.delegation_log]


# ─────────────────────────────────────────────────────────────────────
#  DEMO
# ─────────────────────────────────────────────────────────────────────

print("\n── Creating agents ─────────────────────────────────────────")

researcher = ResearchAgent(
    name="Aria",
    model="gpt-4",
    sources=["arxiv.org", "Wikipedia", "Semantic Scholar"]
)

coder = CoderAgent(
    name="Dev",
    model="claude-3-sonnet",
    language="python"
)

manager = ManagerAgent(
    name="Boss",
    model="gpt-4o",
    team=[researcher, coder]
)

print("\n── introduce() — adapts to the real class dynamically ──────")
print(researcher.introduce())
print(coder.introduce())
print(manager.introduce())

print("\n── ResearchAgent doing research ────────────────────────────")
result1 = researcher.step("Transformer attention mechanisms")
print(result1)
print(f"\n  researcher.searches_done() = {researcher.searches_done()}")

print("\n── CoderAgent writing code ─────────────────────────────────")
result2 = coder.step("Write a function to chunk a list into batches")
print(result2)

print("\n── ManagerAgent routing tasks ──────────────────────────────")
print(manager.run("Research multi-agent orchestration patterns"))
print()
print(manager.run("Code a retry decorator for LLM API calls"))
print()
print(manager.run("Research the history of neural networks"))

print("\n── Memory — inherited from BaseAgent, works for all ────────")
print(f"  researcher memory : {len(researcher.recall())} item(s)")
print(f"  coder memory      : {len(coder.recall())} item(s)")
print(f"  manager memory    : {len(manager.recall())} item(s)")

print("\n── __repr__ — also inherited from BaseAgent ─────────────────")
print(f"  {researcher}")
print(f"  {coder}")
print(f"  {manager}")

print("\n── Manager delegation log ──────────────────────────────────")
for agent_name, task in manager.delegation_summary():
    print(f"  {agent_name} handled: '{task}'")

print("\n── run() raises NotImplementedError if not overridden ───────")
class ForgottenAgent(BaseAgent):
    def __init__(self):
        super().__init__("Ghost", "gpt-4")
    # Forgot to implement run()!

ghost = ForgottenAgent()
try:
    ghost.step("Do something")
except NotImplementedError as e:
    print(f"  Caught: {e}")

print("\n── Key takeaways ───────────────────────────────────────────")
print("""
  1. super().__init__()  → must be called FIRST in every child __init__
  2. Shared methods      → defined once in BaseAgent, inherited by all
  3. Override run()      → each subclass provides its own specific logic
  4. Template method     → step() defines the flow; run() is the variable part
  5. __class__.__name__  → introduce() knows the real type dynamically
  6. NotImplementedError → enforces that subclasses implement run()
""")
