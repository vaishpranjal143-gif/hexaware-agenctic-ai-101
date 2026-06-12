# CONCEPT 9 — DATACLASSES
# @dataclass auto-generates __init__, __repr__, __eq__ from field declarations.
# field(default_factory=...)  → safe mutable defaults (never use = [] or = {})
# frozen=True                 → immutable after creation; raises FrozenInstanceError

from dataclasses import dataclass, field
from datetime   import datetime
from typing     import Optional
import uuid

@dataclass
class Message:
    role       : str
    content    : str
    timestamp  : datetime = field(default_factory=datetime.now)
    tokens     : int      = 0

    def __post_init__(self):           # runs after __init__: validation + derived fields
        if self.role not in {"system","user","assistant","tool"}:
            raise ValueError(f"Bad role: {self.role!r}")
        if self.tokens == 0:
            self.tokens = max(1, len(self.content.split()))

@dataclass
class ToolCall:
    tool_name : str
    arguments : dict = field(default_factory=dict)               # safe mutable default
    call_id   : str  = field(default_factory=lambda: uuid.uuid4().hex[:8])

@dataclass(frozen=True)               # immutable — results must not change
class ToolResult:
    call_id : str
    success : bool
    output  : str
    error   : Optional[str] = None

# ── Demo ──────────────────────────────────────────────────────────────
m = Message("user", "Find recent papers on multi-agent RAG.")
print(m)                               # auto __repr__
print(f"tokens auto-counted: {m.tokens}")

c = ToolCall("web_search", {"q": "RAG 2024"})
print(c)                               # unique call_id each time

r = ToolResult(c.call_id, True, "Found 12 papers")
print(r.output)

try:    r.success = False              # frozen → blocked
except Exception as e: print(f"Frozen blocked: {type(e).__name__}: {e}")

try:    Message("admin", "test")       # __post_init__ validation
except ValueError as e: print(f"Validation: {e}")
