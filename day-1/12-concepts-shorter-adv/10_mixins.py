# CONCEPT 10 — MIXINS
# Small focused classes that add ONE cross-cutting behaviour via multiple inheritance.
# Mixins are NOT standalone — they are mixed into a host class.
# Rule: list mixins BEFORE the main base class in the class() declaration.

import time, functools
from datetime import datetime

class LoggingMixin:
    def log(self, level, msg):
        print(f"  [{datetime.now().strftime('%H:%M:%S')}][{level}] {getattr(self,'name','?')}: {msg}")

class RetryMixin:
    def with_retry(self, fn, attempts=3, delay=0.05):
        for i in range(1, attempts + 1):
            try:    return fn()
            except Exception as e:
                self.log("WARN", f"Attempt {i} failed: {e}")
                if i < attempts: time.sleep(delay)
        raise RuntimeError(f"Failed after {attempts} attempts")

class CachingMixin:
    def __init__(self):  self._cache = {}
    def cached(self, key, fn):
        if key in self._cache:
            self.log("INFO", f"Cache HIT: {key[:30]}");  return self._cache[key]
        result = fn()
        self._cache[key] = result
        self.log("INFO", f"Cache MISS: {key[:30]}");     return result

class BaseAgent:
    def __init__(self, name, model): self.name, self.model = name, model
    def _call_llm(self, task):       return f"[{self.model}] Result: {task[:40]}"

class ProductionAgent(LoggingMixin, RetryMixin, CachingMixin, BaseAgent):
    def __init__(self, name, model="gpt-4"):
        BaseAgent.__init__(self, name, model)
        CachingMixin.__init__(self)      # explicit — CachingMixin has its own __init__

    def run(self, task):
        self.log("INFO", f"Starting: {task[:40]}")
        return self.cached(task, lambda: self.with_retry(lambda: self._call_llm(task)))

# ── Demo ──────────────────────────────────────────────────────────────
agent = ProductionAgent("Atlas", "claude-3")
print(agent.run("Summarise transformer architectures"))
print(agent.run("Summarise transformer architectures"))  # cache hit

attempts = [0]
def flaky():
    attempts[0] += 1
    if attempts[0] < 3: raise ConnectionError("timeout")
    return "success"

print(agent.with_retry(flaky))
print("MRO:", [c.__name__ for c in ProductionAgent.__mro__])
