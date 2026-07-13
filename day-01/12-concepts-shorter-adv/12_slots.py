# CONCEPT 12 — __slots__
# By default every instance carries a __dict__ (a full Python dict) → ~150 bytes.
# __slots__ replaces __dict__ with a fixed C-level struct → ~50 bytes.
# Trade-off: 60–70% less memory, but no dynamic attributes allowed.

import sys, time

class RegularMessage:                             # normal class — uses __dict__
    def __init__(self, role, content, tokens, turn):
        self.role, self.content, self.tokens, self.turn = role, content, tokens, turn
    def to_dict(self): return self.__dict__.copy()

class SlottedMessage:                             # fixed schema — no __dict__
    __slots__ = ("role", "content", "tokens", "turn")   # ← declaration
    def __init__(self, role, content, tokens, turn):
        self.role, self.content, self.tokens, self.turn = role, content, tokens, turn
    def to_dict(self):                            # must build manually — no __dict__
        return {a: getattr(self, a) for a in SlottedMessage.__slots__}

def size(obj):
    s = sys.getsizeof(obj)
    if hasattr(obj, "__dict__"): s += sys.getsizeof(obj.__dict__)
    return s

def bench(cls, n=200_000):
    t = time.perf_counter()
    items = [cls("user", "Hello from pipeline", 4, i) for i in range(n)]
    ms = (time.perf_counter() - t) * 1000
    print(f"  {cls.__name__:>16} | {n:,} instances | {ms:.0f}ms | {size(items[0])}B each")
    return items[0]

# ── Demo ──────────────────────────────────────────────────────────────
r = bench(RegularMessage)
s = bench(SlottedMessage)

print(f"\nRegular  to_dict: {r.to_dict()}")
print(f"Slotted  to_dict: {s.to_dict()}")
print(f"\nMemory saved per msg : {size(r) - size(s)} bytes")
print(f"Saved at 1M messages : {(size(r)-size(s))*1_000_000//1_048_576} MB")

r.new_attr = "allowed"                            # regular: dynamic attrs OK
print(f"\nRegular new attr: {r.new_attr}")
try:   s.new_attr = "blocked"
except AttributeError as e: print(f"Slotted blocked: {e}")
