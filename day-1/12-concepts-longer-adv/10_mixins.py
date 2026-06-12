"""
╔══════════════════════════════════════════════════════════════════════╗
║  CONCEPT 10 — MIXINS                                                ║
║  File    : 10_mixins.py                                             ║
║  Run     : python 10_mixins.py                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║  WHAT IS IT?                                                        ║
║  A mixin is a small, focused class that adds ONE specific           ║
║  cross-cutting behaviour via multiple inheritance.                  ║
║  Mixins are not meant to be instantiated alone.                     ║
║                                                                     ║
║  MIXIN RULES:                                                       ║
║    1. Adds ONE behaviour only (logging, retry, caching...)          ║
║    2. Does NOT define __init__ (or calls super() if it does)        ║
║    3. Listed BEFORE the main class in the inheritance list          ║
║    4. Uses self.name etc. from the host class (duck typing)         ║
║    5. Named with 'Mixin' suffix by convention                       ║
║                                                                     ║
║  VERSUS INHERITANCE:                                                ║
║    Inheritance: "ResearchAgent IS A BaseAgent"                      ║
║    Mixin:       "ProductionAgent HAS logging capability"            ║
║                                                                     ║
║  AGENTIC AI USE CASE: Agent Capability Packs                        ║
║  Logging, retry, caching — added to any agent without touching      ║
║  the agent's core logic. Each mixin is independently useful.        ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import time
import functools
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────
#  PART 1 — THE PROBLEM: Duplicated cross-cutting code
# ─────────────────────────────────────────────────────────────────────

print("=" * 60)
print("PART 1 — THE PROBLEM (duplicated logging and retry)")
print("=" * 60)

class BadResearchAgent:
    """Logging and retry are duplicated directly in the agent."""

    def __init__(self, name):
        self.name    = name
        self._cache  = {}

    def run(self, task: str) -> str:
        # Logging baked into run() — can't reuse elsewhere
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"  [{ts}][INFO] {self.name}: Starting '{task}'")

        # Retry baked into run() — can't reuse elsewhere
        for attempt in range(3):
            try:
                result = self._do_research(task)
                print(f"  [{ts}][INFO] {self.name}: Done")
                return result
            except Exception as e:
                print(f"  [{ts}][WARN] Attempt {attempt+1} failed: {e}")
                time.sleep(0.01)
        raise RuntimeError("All retries failed")

    def _do_research(self, task):
        return f"Research results for: {task}"


class BadCoderAgent:
    """Same logging and retry code duplicated here too — maintenance nightmare."""

    def __init__(self, name):
        self.name   = name
        self._cache = {}

    def run(self, task: str) -> str:
        # SAME logging code — duplicated!
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"  [{ts}][INFO] {self.name}: Starting '{task}'")
        return f"Code for: {task}"


print("BadResearchAgent and BadCoderAgent both duplicate logging/retry.")
print("With 10 agent types, this becomes unmanageable.\n")
r = BadResearchAgent("Aria")
r.run("AI safety research")


# ─────────────────────────────────────────────────────────────────────
#  PART 2 — THE SOLUTION: Three reusable mixins
# ─────────────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("PART 2 — THE SOLUTION (Mixins)")
print("=" * 60)


class LoggingMixin:
    """
    MIXIN 1: Structured logging for any class.

    Accesses self.name from the host class via duck typing.
    If the host has no 'name', falls back to the class name.

    Usage:
        class MyAgent(LoggingMixin, BaseAgent): ...
        agent.log("INFO", "Starting task")
    """

    LOG_COLOURS = {"DEBUG": "·", "INFO": "✓", "WARN": "!", "ERROR": "✗"}

    def log(self, level: str, message: str):
        """
        Print a structured log line.
        Automatically uses self.name from whatever class this mixin is mixed into.
        """
        agent_id = getattr(self, "name", self.__class__.__name__)
        level    = level.upper()
        ts       = datetime.now().strftime("%H:%M:%S")
        icon     = self.LOG_COLOURS.get(level, "?")
        print(f"  [{ts}][{icon}][{level:5s}] {agent_id}: {message}")

    def logged(self, fn):
        """
        Method decorator: wraps fn with entry and exit logging.

        Usage:
            def run(self, task):
                run = self.logged(run)  # or use as @self.logged
        """
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            self.log("DEBUG", f"→ Entering {fn.__name__}()")
            try:
                result = fn(*args, **kwargs)
                self.log("DEBUG", f"← {fn.__name__}() returned OK")
                return result
            except Exception as exc:
                self.log("ERROR", f"✗ {fn.__name__}() raised {type(exc).__name__}: {exc}")
                raise
        return wrapper


class RetryMixin:
    """
    MIXIN 2: Automatic retry with exponential back-off.

    Any method call that might fail transiently can be wrapped
    with self.with_retry(fn, ...).

    Usage:
        result = self.with_retry(lambda: self.call_api(task), max_attempts=3)
    """

    def with_retry(
        self,
        fn,
        max_attempts: int   = 3,
        initial_delay: float = 0.05,
        backoff: float       = 2.0,
    ):
        """
        Call fn(). On exception, wait and retry up to max_attempts times.
        Delay doubles each attempt (exponential back-off).

        Parameters:
            fn             : callable with NO arguments (use lambda)
            max_attempts   : total attempts before giving up
            initial_delay  : seconds to wait before first retry
            backoff        : multiply delay by this each retry
        """
        delay     = initial_delay
        last_exc  = None

        for attempt in range(1, max_attempts + 1):
            try:
                return fn()                   # try calling the function
            except Exception as exc:
                last_exc = exc
                if attempt < max_attempts:
                    if hasattr(self, "log"):  # use LoggingMixin if available
                        self.log(
                            "WARN",
                            f"Attempt {attempt}/{max_attempts} failed: {exc}. "
                            f"Retrying in {delay:.2f}s..."
                        )
                    time.sleep(delay)
                    delay *= backoff          # exponential back-off

        # All attempts exhausted
        if hasattr(self, "log"):
            self.log("ERROR", f"All {max_attempts} attempt(s) failed.")
        raise last_exc


class CachingMixin:
    """
    MIXIN 3: Memoisation — avoid repeating identical computations.

    Stores results keyed by a string. If the same key is seen again,
    returns the cached result without calling fn() again.

    IMPORTANT: Because this mixin has __init__, the host class
    must call CachingMixin.__init__(self) explicitly.

    Usage:
        result = self.cached("task_key", lambda: self.run_task())
    """

    def __init__(self):
        self._cache      : dict = {}
        self._cache_hits : int  = 0

    def cached(self, key: str, fn):
        """
        If key is in cache → return cached result immediately.
        If not → call fn(), store result, return it.
        """
        if key in self._cache:
            self._cache_hits += 1
            if hasattr(self, "log"):
                self.log("DEBUG", f"Cache HIT → '{key[:40]}'")
            return self._cache[key]

        # Cache miss: compute and store
        result = fn()
        self._cache[key] = result
        if hasattr(self, "log"):
            self.log("DEBUG", f"Cache MISS, stored → '{key[:40]}'")
        return result

    def cache_stats(self) -> dict:
        return {
            "cached_keys": len(self._cache),
            "cache_hits" : self._cache_hits,
        }

    def cache_clear(self):
        self._cache.clear()
        self._cache_hits = 0
        if hasattr(self, "log"):
            self.log("INFO", "Cache cleared.")


# ─────────────────────────────────────────────────────────────────────
#  COMPOSE MIXINS INTO A PRODUCTION AGENT
# ─────────────────────────────────────────────────────────────────────

class BaseAgent:
    """Simple base agent without any cross-cutting concerns."""

    def __init__(self, name: str, model: str):
        self.name  = name
        self.model = model

    def _call_llm(self, task: str) -> str:
        """Simulated LLM call. Real code calls an API here."""
        return f"[{self.model}] Result: '{task[:55]}'"


class ProductionAgent(LoggingMixin, RetryMixin, CachingMixin, BaseAgent):
    """
    A production-ready agent composing all three mixins.

    MRO:
      ProductionAgent → LoggingMixin → RetryMixin → CachingMixin → BaseAgent → object

    COMPOSITION RULES:
      1. Mixins listed BEFORE BaseAgent in the inheritance list
      2. CachingMixin.__init__(self) called explicitly because it has __init__
      3. BaseAgent.__init__() called next for name and model
      4. LoggingMixin and RetryMixin have no __init__ — nothing to call

    The run() method below contains ONLY agent logic.
    All logging, retry, and caching come from the mixins.
    """

    def __init__(self, name: str, model: str = "gpt-4"):
        BaseAgent.__init__(self, name, model)     # sets self.name, self.model
        CachingMixin.__init__(self)               # sets self._cache, self._cache_hits
        # LoggingMixin and RetryMixin: no __init__ needed

    def run(self, task: str) -> str:
        """
        Core agent logic — clean and focused.
        Cross-cutting concerns come from mixins, not from this method.
        """
        self.log("INFO", f"Starting task: '{task[:50]}'")

        # Use caching to avoid repeating identical tasks
        result = self.cached(
            key=task,
            fn=lambda: self._execute_with_retry(task)
        )

        self.log("INFO", f"Task complete.")
        return result

    def _execute_with_retry(self, task: str) -> str:
        """Calls _call_llm with retry protection."""
        return self.with_retry(
            fn=lambda: self._call_llm(task),
            max_attempts=3,
            initial_delay=0.02,
        )


# ─────────────────────────────────────────────────────────────────────
#  DEMO
# ─────────────────────────────────────────────────────────────────────

print("\n── Creating a ProductionAgent (all three mixins) ────────────")
agent = ProductionAgent("Atlas", model="claude-3-sonnet")

print("\n── First run: cache miss → executes task ────────────────────")
result1 = agent.run("Summarise the impact of transformers on NLP")
print(f"  Result: {result1}")

print("\n── Second run: same task → cache hit ────────────────────────")
result2 = agent.run("Summarise the impact of transformers on NLP")
print(f"  Result: {result2}")
print(f"  Cache stats: {agent.cache_stats()}")

print("\n── Third run: different task → new cache miss ───────────────")
result3 = agent.run("Explain the ReAct agent framework")
print(f"  Result: {result3}")
print(f"  Cache stats: {agent.cache_stats()}")

print("\n── Retry demo: flaky function ───────────────────────────────")
attempt_counter = [0]

def flaky_api_call():
    """Simulates a flaky API that fails twice then succeeds."""
    attempt_counter[0] += 1
    if attempt_counter[0] < 3:
        raise ConnectionError(f"API timeout (attempt {attempt_counter[0]})")
    return f"Success on attempt {attempt_counter[0]}"

try:
    result = agent.with_retry(flaky_api_call, max_attempts=4, initial_delay=0.01)
    agent.log("INFO", f"Retry result: {result}")
except Exception as e:
    agent.log("ERROR", f"All retries failed: {e}")

print("\n── LoggingMixin works on ANY class ──────────────────────────")

class SimpleService(LoggingMixin):
    """Not an agent — just a service that wants structured logging."""
    def __init__(self, name):
        self.name = name    # LoggingMixin reads self.name

    def start(self):
        self.log("INFO", "Service starting.")
        self.log("WARN", "Low memory warning.")
        self.log("ERROR", "Could not connect to database.")

svc = SimpleService("DatabaseService")
svc.start()

print("\n── Cache clear ──────────────────────────────────────────────")
agent.cache_clear()
print(f"  After clear: {agent.cache_stats()}")

print("\n── MRO of ProductionAgent ───────────────────────────────────")
for i, cls in enumerate(ProductionAgent.__mro__):
    print(f"  {i}: {cls.__name__}")

print("\n── Key takeaways ────────────────────────────────────────────")
print("""
  Mixin          Purpose                  Named with
  ─────────────  ───────────────────────  ─────────────────
  LoggingMixin   Structured log output    log(), logged()
  RetryMixin     Retry on failure         with_retry()
  CachingMixin   Memoise results          cached(), cache_stats()

  Rules:
    1. List mixins BEFORE the main base class in class()
    2. If a mixin has __init__, call it explicitly in the host's __init__
    3. Mixins use getattr(self, 'name', ...) to safely access host attributes
    4. Each mixin does ONE thing — do not add unrelated methods
    5. "Mixin" suffix is a naming convention — not enforced by Python
    6. Composition: host class IS-A BaseAgent but HAS logging via Mixin
""")
