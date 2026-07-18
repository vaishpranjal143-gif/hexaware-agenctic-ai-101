"""
╔══════════════════════════════════════════════════════════════════════╗
║  CONCEPT 5 — MAGIC METHODS (Dunder Methods)                         ║
║  File    : 05_magic_methods.py                                      ║
║  Run     : python 05_magic_methods.py                               ║
╠══════════════════════════════════════════════════════════════════════╣
║  WHAT IS IT?                                                        ║
║  Methods surrounded by double underscores (__method__) that Python  ║
║  calls automatically when you use built-in operations on an object. ║
║  They let your class integrate seamlessly with Python syntax.       ║
║                                                                     ║
║  METHODS COVERED IN THIS FILE:                                      ║
║    __init__      → object construction (you already know this one)  ║
║    __repr__      → repr(obj) and REPL display                       ║
║    __str__       → str(obj) and print(obj)                          ║
║    __len__       → len(obj)                                         ║
║    __bool__      → if obj:                                          ║
║    __contains__  → "key" in obj                                     ║
║    __getitem__   → obj["key"]                                       ║
║    __setitem__   → obj["key"] = value                               ║
║    __delitem__   → del obj["key"]                                   ║
║    __iter__      → for item in obj                                  ║
║    __add__       → obj_a + obj_b                                    ║
║                                                                     ║
║  AGENTIC AI USE CASE: Agent Memory Store                            ║
║  Agent memory should feel native — indexable, iterable, mergeable.  ║
╚══════════════════════════════════════════════════════════════════════╝
"""

from datetime import datetime


# ─────────────────────────────────────────────────────────────────────
#  PART 1 — THE PROBLEM: Memory that doesn't behave like Python
# ─────────────────────────────────────────────────────────────────────

print("=" * 60)
print("PART 1 — THE PROBLEM (clunky API, not Pythonic)")
print("=" * 60)

class BadMemory:
    """Memory store without dunder methods — awkward to use."""

    def __init__(self):
        self._data = {}

    def set(self, key, value):
        self._data[key] = value

    def get(self, key):
        return self._data.get(key)

    def has(self, key):
        return key in self._data

    def size(self):
        return len(self._data)

    def get_all_keys(self):
        return list(self._data.keys())


bad_mem = BadMemory()
bad_mem.set("goal", "Build a research agent")
bad_mem.set("user", "Alice")

# Usage is verbose and non-Pythonic:
print(f"bad_mem.get('goal')   = {bad_mem.get('goal')}")
print(f"bad_mem.has('goal')   = {bad_mem.has('goal')}")
print(f"bad_mem.size()        = {bad_mem.size()}")
print(f"bad_mem.get_all_keys()= {bad_mem.get_all_keys()}")
print("\nProblem: You have to learn a new API. Python's built-in syntax doesn't work.")
print("         Can't do: len(mem), 'goal' in mem, mem['goal'], for k in mem\n")


# ─────────────────────────────────────────────────────────────────────
#  PART 2 — THE SOLUTION: Magic methods make it feel native
# ─────────────────────────────────────────────────────────────────────

print("=" * 60)
print("PART 2 — THE SOLUTION (Magic Methods)")
print("=" * 60)


class MemoryStore:
    """
    Key-value store for agent working memory.
    Implements dunder methods so it works like a native Python container.

    Python calls these automatically — you never call them directly:
        memory["key"] = value     →  __setitem__ is called
        value = memory["key"]     →  __getitem__ is called
        del memory["key"]         →  __delitem__ is called
        "key" in memory           →  __contains__ is called
        len(memory)               →  __len__ is called
        if memory:                →  __bool__ is called
        for key in memory:        →  __iter__ is called
        repr(memory)              →  __repr__ is called
        print(memory)             →  __str__ is called
        mem_a + mem_b             →  __add__ is called
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self._store: dict = {}         # internal storage — callers use [] not ._store

    # ── CONSTRUCTION ──────────────────────────────────────────────────

    # __init__ is the one dunder method you already know.
    # It runs when you write: mem = MemoryStore("Aria")

    # ── STORAGE OPERATIONS ────────────────────────────────────────────

    def __setitem__(self, key: str, value):
        """
        Called by: memory["key"] = value

        We store the value + metadata (timestamp, version counter).
        The caller just writes memory["goal"] = "Build an agent" — simple.
        """
        existing_version = self._store[key]["version"] if key in self._store else 0
        self._store[key] = {
            "value"  : value,
            "at"     : datetime.now().strftime("%H:%M:%S"),
            "version": existing_version + 1,
        }

    def __getitem__(self, key: str):
        """
        Called by: value = memory["key"]

        Returns the value. Raises KeyError if not found,
        exactly like a real Python dict.
        """
        if key not in self._store:
            raise KeyError(
                f"'{key}' not found in {self.agent_name}'s memory.\n"
                f"  Available keys: {list(self._store.keys())}"
            )
        return self._store[key]["value"]

    def __delitem__(self, key: str):
        """
        Called by: del memory["key"]

        Removes the entry. Raises KeyError if key doesn't exist.
        """
        if key not in self._store:
            raise KeyError(f"Cannot delete '{key}' — not in memory.")
        del self._store[key]

    # ── LOOKUP OPERATIONS ─────────────────────────────────────────────

    def __contains__(self, key: str) -> bool:
        """
        Called by: "key" in memory

        Returns True if the key exists. Python calls this when you write
        'key' in memory — you never call __contains__ yourself.
        """
        return key in self._store

    def __len__(self) -> int:
        """
        Called by: len(memory)

        Returns the number of stored items.
        """
        return len(self._store)

    def __bool__(self) -> bool:
        """
        Called by: if memory:  or  bool(memory)

        Returns True if memory has at least one item.
        Without this, Python would fall back to checking if the object
        is None (which it never is), so 'if memory' would always be True.
        """
        return len(self._store) > 0

    # ── ITERATION ─────────────────────────────────────────────────────

    def __iter__(self):
        """
        Called by: for key in memory

        Returns an iterator over the keys (same as iterating over a dict).
        """
        return iter(self._store)

    # ── DISPLAY ───────────────────────────────────────────────────────

    def __repr__(self) -> str:
        """
        Called by: repr(memory)   — used in the Python REPL and debuggers.

        Convention: __repr__ should return a string from which the object
        could theoretically be reconstructed. Keep it concise.
        """
        return (
            f"MemoryStore("
            f"agent='{self.agent_name}', "
            f"items={len(self._store)})"
        )

    def __str__(self) -> str:
        """
        Called by: str(memory)  or  print(memory)

        Convention: __str__ is for human-readable display.
        If __str__ is not defined, Python falls back to __repr__.
        """
        if not self._store:
            return f"MemoryStore('{self.agent_name}') — empty"

        lines = [f"MemoryStore('{self.agent_name}'):"]
        for key, meta in self._store.items():
            lines.append(
                f"  [v{meta['version']}] {key!r} = {str(meta['value'])[:50]!r}"
                f"  (stored @ {meta['at']})"
            )
        return "\n".join(lines)

    # ── COMBINATION ───────────────────────────────────────────────────

    def __add__(self, other: "MemoryStore") -> "MemoryStore":
        """
        Called by: merged = memory_a + memory_b

        Rules:
          - Returns a NEW MemoryStore (never mutates the originals)
          - On key conflict, the RIGHT-HAND side (other) wins
          - Combined agent name reflects both sources
        """
        merged = MemoryStore(f"{self.agent_name}+{other.agent_name}")
        # Copy self first
        for key in self._store:
            merged[key] = self[key]
        # Copy other second — overwrites conflicts
        for key in other:
            merged[key] = other[key]
        return merged

    # ── DICT-LIKE HELPERS ─────────────────────────────────────────────

    def when(self, key: str) -> str:
        """When was this key last written?"""
        if key not in self._store:
            raise KeyError(key)
        return self._store[key]["at"]

    def version(self, key: str) -> int:
        """How many times has this key been updated?"""
        if key not in self._store:
            raise KeyError(key)
        return self._store[key]["version"]

    def keys(self):
        return self._store.keys()

    def values(self):
        return (self._store[k]["value"] for k in self._store)

    def items(self):
        return ((k, self._store[k]["value"]) for k in self._store)


# ─────────────────────────────────────────────────────────────────────
#  DEMO — each magic method demonstrated individually
# ─────────────────────────────────────────────────────────────────────

print("\n── __setitem__ : memory['key'] = value ─────────────────────")
mem = MemoryStore("Aria")
mem["user_goal"]   = "Build a research assistant agent"
mem["task_plan"]   = "Search → Summarise → Output"
mem["context"]     = "AI safety research project"
mem["user_name"]   = "Alice"
print("Stored 4 items via mem['key'] = value")

print("\n── __repr__ : repr(memory) ─────────────────────────────────")
print(repr(mem))    # short summary

print("\n── __str__ : print(memory) ─────────────────────────────────")
print(str(mem))     # verbose display

print("\n── __len__ : len(memory) ───────────────────────────────────")
print(f"len(mem) = {len(mem)}")

print("\n── __contains__ : 'key' in memory ──────────────────────────")
print(f"'user_goal' in mem = {'user_goal' in mem}")
print(f"'budget'    in mem = {'budget' in mem}")

print("\n── __getitem__ : value = memory['key'] ──────────────────────")
print(f"mem['user_name'] = {mem['user_name']}")
print(f"Stored at: {mem.when('user_name')}")

print("\n── __setitem__ again: updating a key increments version ─────")
mem["user_goal"] = "Build a multi-agent research pipeline"
print(f"user_goal version = {mem.version('user_goal')}  (was 1, now 2)")

print("\n── __iter__ : for key in memory ─────────────────────────────")
print("Iterating over all keys:")
for key in mem:              # __iter__ is called here
    print(f"  {key:12s} → {mem[key]}")

print("\n── __bool__ : if memory ─────────────────────────────────────")
if mem:                      # __bool__ is called here
    print("Memory has content — agent has context to work with.")

empty_mem = MemoryStore("EmptyBot")
if not empty_mem:
    print("Empty memory — agent starts with a blank slate.")

print("\n── __delitem__ : del memory['key'] ──────────────────────────")
del mem["context"]
print(f"After del 'context': len = {len(mem)}")

print("\n── __add__ : merged = mem_a + mem_b ─────────────────────────")
mem2 = MemoryStore("Dev")
mem2["context"]  = "Coding project (Dev's version)"  # conflict → mem2 wins
mem2["language"] = "Python"

merged = mem + mem2     # __add__ is called here
print(f"Merged: {repr(merged)}")
print(f"merged['context']  = {merged['context']}")   # Dev's value wins
print(f"merged['user_name']= {merged['user_name']}")  # Aria's value (no conflict)

print("\n── KeyError when accessing a missing key ────────────────────")
try:
    _ = mem["nonexistent_key"]
except KeyError as e:
    print(f"  KeyError raised: {e}")

print("\n── Using items() like a dict ────────────────────────────────")
print("All key-value pairs:")
for key, value in mem.items():
    print(f"  {key}: {value}")

print("\n── Key takeaways ────────────────────────────────────────────")
print("""
  Magic Method       Python Syntax that triggers it
  ─────────────────  ──────────────────────────────
  __init__           mem = MemoryStore("Aria")
  __repr__           repr(mem)  — also used in REPL/debugger
  __str__            print(mem) or str(mem)
  __len__            len(mem)
  __bool__           if mem:  / not mem
  __contains__       "key" in mem
  __getitem__        mem["key"]
  __setitem__        mem["key"] = value
  __delitem__        del mem["key"]
  __iter__           for key in mem:
  __add__            merged = mem_a + mem_b

  Rule: You define __method__, Python calls it automatically.
        Never call dunder methods directly (e.g. mem.__len__()).
        Always use the built-in syntax that triggers them.
""")
