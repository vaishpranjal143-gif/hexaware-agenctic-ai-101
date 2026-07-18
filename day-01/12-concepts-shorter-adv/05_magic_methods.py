# CONCEPT 5 — MAGIC METHODS (Dunder Methods)
# Python calls __dunders__ automatically for built-in operations.
# Goal: make AgentMemory feel like a native Python container.

from datetime import datetime

class AgentMemory:
    def __init__(self, agent):
        self.agent, self._store = agent, {}

    def __setitem__(self, k, v):          # memory["key"] = value
        self._store[k] = {"val": v, "at": datetime.now().strftime("%H:%M:%S")}

    def __getitem__(self, k):             # value = memory["key"]
        if k not in self._store: raise KeyError(k)
        return self._store[k]["val"]

    def __contains__(self, k): return k in self._store   # "k" in memory
    def __len__(self):         return len(self._store)   # len(memory)
    def __bool__(self):        return len(self._store) > 0  # if memory:
    def __iter__(self):        return iter(self._store)  # for k in memory
    def __repr__(self):        return f"AgentMemory(agent={self.agent!r}, items={len(self)})"
    def __add__(self, other):  # merged = mem_a + mem_b
        m = AgentMemory(f"{self.agent}+{other.agent}")
        for k in self:   m[k] = self[k]
        for k in other:  m[k] = other[k]   # other wins on conflict
        return m

# ── Demo ──────────────────────────────────────────────────────────────
mem = AgentMemory("Aria")
mem["goal"] = "Build a research agent"    # __setitem__
mem["user"] = "Alice"

print(repr(mem))                          # __repr__
print(f"len={len(mem)}")                  # __len__
print(f"'goal' in mem: {'goal' in mem}")  # __contains__
print(f"mem['user']: {mem['user']}")      # __getitem__
for k in mem: print(f"  {k} → {mem[k]}") # __iter__ + __getitem__

mem2 = AgentMemory("Dev")
mem2["lang"] = "Python"
mem2["goal"] = "Dev's goal"               # conflict → mem2 wins
merged = mem + mem2                       # __add__
print(repr(merged))
print(f"merged['goal']: {merged['goal']}") # Dev's version wins ✓
