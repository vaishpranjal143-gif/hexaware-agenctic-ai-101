"""
╔══════════════════════════════════════════════════════════════════════╗
║  CONCEPT 12 — __slots__                                             ║
║  File    : 12_slots.py                                              ║
║  Run     : python 12_slots.py                                       ║
╠══════════════════════════════════════════════════════════════════════╣
║  WHAT IS IT?                                                        ║
║  By default, every Python object carries a __dict__ — a full        ║
║  Python dictionary that stores its attributes. This is flexible     ║
║  but expensive (100–200 bytes per instance in overhead).            ║
║                                                                     ║
║  __slots__ replaces __dict__ with a compact, fixed C-level array.   ║
║  Python pre-allocates exactly the listed attributes.                ║
║                                                                     ║
║  BENEFITS:                                                          ║
║    + Memory per instance drops ~60–70%                              ║
║    + Attribute access is slightly faster (index vs hash lookup)     ║
║    + Schema is enforced — no accidental new attributes              ║
║                                                                     ║
║  TRADE-OFFS:                                                        ║
║    - Cannot add new attributes at runtime                           ║
║    - No __dict__ → must implement to_dict() manually                ║
║    - No __weakref__ by default (add it to slots if needed)          ║
║    - Child classes must declare their own __slots__ too             ║
║                                                                     ║
║  WHEN TO USE:                                                       ║
║    - Classes instantiated 10,000+ times per second                  ║
║    - Microservices processing high-volume event streams             ║
║    - Fixed schema data objects (messages, tokens, events)           ║
║                                                                     ║
║  AGENTIC AI USE CASE: High-Throughput Message Pipeline              ║
║  Agent pipelines create millions of small message objects.          ║
║  Saving 90 bytes per instance × 1,000,000 = 85 MB saved.           ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import sys
import time
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────
#  PART 1 — HOW __dict__ WORKS (standard Python class)
# ─────────────────────────────────────────────────────────────────────

print("=" * 60)
print("PART 1 — HOW __dict__ WORKS (default Python class)")
print("=" * 60)

class RegularMessage:
    """
    Standard Python class.
    Every instance carries a __dict__ — a full Python dictionary
    that stores its attributes. Flexible but memory-heavy.
    """

    def __init__(self, role: str, content: str, tokens: int, turn: int):
        self.role    = role
        self.content = content
        self.tokens  = tokens
        self.turn    = turn

    def to_dict(self) -> dict:
        """__dict__ exists → easy to convert."""
        return self.__dict__.copy()

    def __repr__(self):
        return (
            f"RegularMessage("
            f"role={self.role!r}, "
            f"tokens={self.tokens}, "
            f"turn={self.turn})"
        )


msg = RegularMessage("user", "Hello, agent!", 4, 1)

print(f"msg = {msg}")
print(f"msg.__dict__ = {msg.__dict__}")
print(f"type(msg.__dict__) = {type(msg.__dict__)}")
print(f"\nBecause __dict__ is a Python dict, you can add any attribute:")
msg.surprise_field = "I wasn't in __init__!"     # Works!
msg.another_field  = 42
print(f"  msg.__dict__ after additions: {msg.__dict__}")
print(f"\nFlexibility is nice, but this costs memory.")
print(f"  sys.getsizeof(msg)         = {sys.getsizeof(msg)} bytes")
print(f"  sys.getsizeof(msg.__dict__) = {sys.getsizeof(msg.__dict__)} bytes")
print(f"  Total footprint            ≈ {sys.getsizeof(msg) + sys.getsizeof(msg.__dict__)} bytes")


# ─────────────────────────────────────────────────────────────────────
#  PART 2 — __slots__ (memory-efficient fixed schema)
# ─────────────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("PART 2 — __slots__ (Memory-Efficient Fixed Schema)")
print("=" * 60)


class SlottedMessage:
    """
    Memory-efficient message using __slots__.

    __slots__ = ('role', 'content', 'tokens', 'turn')

    What this declaration does:
      1. Tells Python: "This class will only EVER have these 4 attributes."
      2. Python pre-allocates a fixed C-level struct instead of a dict.
      3. No __dict__ is created — saving 50–100+ bytes per instance.
      4. Attribute access uses a slot descriptor (index-based) — slightly faster.
      5. Adding any attribute NOT in __slots__ raises AttributeError.

    Use __slots__ when:
      - You create this class 10k+ times per second
      - The attributes are fixed and known at design time
      - Memory footprint matters at scale
    """

    __slots__ = ("role", "content", "tokens", "turn")   # ← the declaration

    def __init__(self, role: str, content: str, tokens: int, turn: int):
        # Same interface as RegularMessage — identical from the caller's view
        self.role    = role
        self.content = content
        self.tokens  = tokens
        self.turn    = turn

    def to_dict(self) -> dict:
        """
        __dict__ does NOT exist on slotted objects.
        We must iterate __slots__ manually.

        IMPORTANT: Reference SlottedMessage.__slots__ directly — not
        self.__slots__ — because on instances of child classes,
        self.__slots__ resolves to the child's slots only.
        """
        return {attr: getattr(self, attr) for attr in SlottedMessage.__slots__}

    def __repr__(self):
        return (
            f"SlottedMessage("
            f"role={self.role!r}, "
            f"tokens={self.tokens}, "
            f"turn={self.turn})"
        )


# ─────────────────────────────────────────────────────────────────────
#  PART 3 — INHERITING FROM A SLOTTED CLASS
# ─────────────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("PART 3 — INHERITING FROM A SLOTTED CLASS")
print("=" * 60)

print("""
  RULE: When extending a slotted class, declare ONLY the NEW attributes
        in the child's __slots__. The parent's slots are inherited.

  MISTAKE to avoid: if you omit __slots__ in the child, Python adds
        a __dict__ back — defeating the memory savings!
""")


class TimestampedSlottedMessage(SlottedMessage):
    """
    Extends SlottedMessage with one additional slot: timestamp.

    Parent slots inherited:  role, content, tokens, turn  (from SlottedMessage)
    Child slots declared:    timestamp                     (new, only defined here)

    If you forget __slots__ here, Python adds __dict__ — losing all savings.
    """

    __slots__ = ("timestamp",)    # ← ONLY the new attribute

    def __init__(self, role: str, content: str, tokens: int, turn: int):
        super().__init__(role, content, tokens, turn)
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Combine parent slots and child slots."""
        d = super().to_dict()                                    # parent slots
        for attr in TimestampedSlottedMessage.__slots__:         # child slots
            d[attr] = getattr(self, attr)
        return d

    def __repr__(self):
        return (
            f"TimestampedSlottedMessage("
            f"role={self.role!r}, "
            f"tokens={self.tokens}, "
            f"ts={self.timestamp[:10]})"
        )


ts_msg = TimestampedSlottedMessage("user", "Search for RAG papers.", 8, 1)
print(f"TimestampedSlottedMessage: {ts_msg}")
print(f"to_dict(): {ts_msg.to_dict()}")
print(f"\nParent __slots__: {SlottedMessage.__slots__}")
print(f"Child  __slots__: {TimestampedSlottedMessage.__slots__}")
print(f"Combined         : {SlottedMessage.__slots__ + TimestampedSlottedMessage.__slots__}")


# ─────────────────────────────────────────────────────────────────────
#  PART 4 — BENCHMARK: Regular vs Slotted
# ─────────────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("PART 4 — BENCHMARK")
print("=" * 60)


def measure_instance_bytes(obj) -> int:
    """Approximate memory footprint of one object in bytes."""
    size = sys.getsizeof(obj)
    if hasattr(obj, "__dict__"):
        size += sys.getsizeof(obj.__dict__)
    return size


def run_benchmark(cls, n: int = 200_000) -> list:
    """Create n instances and measure creation time + per-instance size."""
    start     = time.perf_counter()
    instances = [cls("user", "Hello from the pipeline", 4, i) for i in range(n)]
    elapsed   = (time.perf_counter() - start) * 1000
    size      = measure_instance_bytes(instances[0])

    print(
        f"  {cls.__name__:>30} | "
        f"{n:>10,} instances | "
        f"{elapsed:>7.1f} ms | "
        f"{size:>4} bytes/instance"
    )
    return instances


print(f"{'Class':>30}   {'Instances':>10}   {'Time':>7}   {'Size'}")
print("-" * 62)
run_benchmark(RegularMessage)
run_benchmark(SlottedMessage)
run_benchmark(TimestampedSlottedMessage)


# ─────────────────────────────────────────────────────────────────────
#  DEMO: Functional equivalence + key differences
# ─────────────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("DEMO: Functional Equivalence and Key Differences")
print("=" * 60)

regular = RegularMessage("assistant", "Here is my answer.", 12, 3)
slotted = SlottedMessage("assistant", "Here is my answer.", 12, 3)

print("\n── Same repr output ─────────────────────────────────────────")
print(f"  regular = {regular}")
print(f"  slotted = {slotted}")

print("\n── Same to_dict() output ────────────────────────────────────")
print(f"  regular.to_dict() = {regular.to_dict()}")
print(f"  slotted.to_dict() = {slotted.to_dict()}")

print("\n── Memory sizes ─────────────────────────────────────────────")
reg_bytes  = measure_instance_bytes(regular)
slot_bytes = measure_instance_bytes(slotted)
saved      = reg_bytes - slot_bytes

print(f"  RegularMessage   : {reg_bytes} bytes")
print(f"  SlottedMessage   : {slot_bytes} bytes")
print(f"  Saved per message: {saved} bytes")
print(f"  At 1M messages   : {saved * 1_000_000 / 1_048_576:.1f} MB saved")

print("\n── __dict__ existence ───────────────────────────────────────")
print(f"  hasattr(regular, '__dict__') = {hasattr(regular, '__dict__')}")
print(f"  hasattr(slotted, '__dict__') = {hasattr(slotted, '__dict__')}")

print("\n── Dynamic attributes ───────────────────────────────────────")
regular.new_attr = "Regular allows this"    # Works
print(f"  regular.new_attr = '{regular.new_attr}'")

try:
    slotted.new_attr = "Slotted blocks this"
except AttributeError as e:
    print(f"  Slotted raises AttributeError: {e}")
    print("  → This enforces a fixed, predictable schema.")

print("\n── Iteration over slotted attributes (via __slots__) ────────")
print("  Slotted attributes:")
for attr in SlottedMessage.__slots__:
    print(f"    slotted.{attr} = {getattr(slotted, attr)!r}")

print("\n── Slot descriptors (how Python stores slot values) ─────────")
print(f"  SlottedMessage.__slots__ = {SlottedMessage.__slots__}")
# Each slot has a member_descriptor on the class
for slot in SlottedMessage.__slots__:
    descriptor = getattr(SlottedMessage, slot)
    print(f"  SlottedMessage.{slot} is a {type(descriptor).__name__}")

print("\n── Common gotcha: __slots__ in child without parent slots ───")

class MistakeChild(SlottedMessage):
    # Forgot to declare __slots__ → Python adds __dict__ back!
    pass

mistake = MistakeChild("user", "oops", 1, 1)
print(f"  MistakeChild has __dict__: {hasattr(mistake, '__dict__')}")
print(f"  MistakeChild bytes: {measure_instance_bytes(mistake)}")
print(f"  SlottedMessage bytes: {measure_instance_bytes(slotted)}")
print("  → Forgetting __slots__ in the child brings __dict__ back!")

print("\n── Key takeaways ────────────────────────────────────────────")
print("""
  Feature                 RegularMessage     SlottedMessage
  ───────────────────     ──────────────     ─────────────────
  Memory per instance     ~152 bytes         ~64 bytes
  Dynamic new attributes  Yes                No (AttributeError)
  __dict__                Yes                No
  to_dict()               self.__dict__      manual via __slots__
  Hashable                No (mutable)       No (mutable)
  Schema enforcement      None               Fixed at class level

  When to use __slots__:
    YES → creating 10,000+ instances per second
    YES → fixed schema, known at design time
    YES → tight memory budget (embedded, microservices)
    NO  → need dynamic attributes (config, plugin systems)
    NO  → using __dict__-based tools (some ORMs, pickle edge cases)

  Remember in inheritance:
    → Declare __slots__ = (...) in EVERY class in the hierarchy
    → Child declares only the NEW attributes
    → Omitting it in any level adds __dict__ back
""")
