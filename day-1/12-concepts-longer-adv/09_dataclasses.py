"""
╔══════════════════════════════════════════════════════════════════════╗
║  CONCEPT 9 — DATACLASSES                                            ║
║  File    : 09_dataclasses.py                                        ║
║  Run     : python 09_dataclasses.py                                 ║
╠══════════════════════════════════════════════════════════════════════╣
║  WHAT IS IT?                                                        ║
║  @dataclass is a decorator that auto-generates boilerplate dunder   ║
║  methods based on your class fields:                                ║
║    __init__   → so you can write Message(role="user", content="hi") ║
║    __repr__   → so print() shows all fields clearly                 ║
║    __eq__     → so msg1 == msg2 compares fields, not identity       ║
║                                                                     ║
║  KEY FEATURES:                                                      ║
║    field(default_factory=list)  → safe mutable defaults             ║
║    frozen=True                  → immutable after construction      ║
║    __post_init__                → runs after __init__ for extras    ║
║    @property inside dataclass   → computed fields                   ║
║                                                                     ║
║  AGENTIC AI USE CASE: Agent Message Schema                          ║
║  Clean, typed data structures for the agent pipeline: messages,     ║
║  tool calls, tool results, and agent turns.                         ║
╚══════════════════════════════════════════════════════════════════════╝
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


# ─────────────────────────────────────────────────────────────────────
#  PART 1 — THE PROBLEM: Verbose manual class definitions
# ─────────────────────────────────────────────────────────────────────

print("=" * 60)
print("PART 1 — THE PROBLEM (no @dataclass)")
print("=" * 60)

class ManualMessage:
    """A message class written by hand — lots of boilerplate."""

    def __init__(self, role: str, content: str):
        self.role    = role
        self.content = content

    def __repr__(self):
        return f"ManualMessage(role='{self.role}', content='{self.content}')"

    def __eq__(self, other):
        if not isinstance(other, ManualMessage):
            return False
        return self.role == other.role and self.content == other.content

    # Every new field requires updating __init__, __repr__, __eq__ manually.
    # With 8 fields this becomes dozens of extra lines.

m1 = ManualMessage("user", "hello")
m2 = ManualMessage("user", "hello")
print(f"repr  : {repr(m1)}")
print(f"equal : {m1 == m2}")
print("\nProblem: Every field change means updating __init__, __repr__, AND __eq__.")
print("Problem: With 8 fields and 20 data classes, this is hundreds of lines.\n")


# ─────────────────────────────────────────────────────────────────────
#  PART 2 — THE SOLUTION: @dataclass
# ─────────────────────────────────────────────────────────────────────

print("=" * 60)
print("PART 2 — THE SOLUTION (@dataclass)")
print("=" * 60)


# ── IMPORTANT: Mutable defaults must use field(default_factory=...) ──

print("\n── WARNING: Common beginner mistake with mutable defaults ───")
print("@dataclass raises ValueError if you write: arguments: dict = {}")
print("Python refuses to compile it. The correct fix is field(default_factory=dict).")
print("We show the shared-dict bug with a plain class instead:")
print()

# Plain class to show the BUG: shared mutable default
class BuggyToolCall:
    def __init__(self, tool_name, arguments={}):  # WRONG — shared dict!
        self.tool_name = tool_name
        self.arguments = arguments

b1 = BuggyToolCall("search")
b2 = BuggyToolCall("calc")
b1.arguments["key"] = "oops"
print(f"b1.arguments = {b1.arguments}")
print(f"b2.arguments = {b2.arguments}  <- ALSO has 'key'! Dict is shared!")
print()

# @dataclass FIX: field(default_factory=dict) gives each instance its own fresh dict
@dataclass
class CorrectToolCall:
    tool_name : str
    arguments : dict = field(default_factory=dict)   # <- CORRECT: fresh dict per instance

c3 = CorrectToolCall("search")
c4 = CorrectToolCall("calc")
c3.arguments["key"] = "value"
print(f"c3.arguments = {c3.arguments}")
print(f"c4.arguments = {c4.arguments}  <- Empty. Separate dict. Correct!")


# ─────────────────────────────────────────────────────────────────────
#  THE FOUR DATA CLASSES FOR AN AGENT PIPELINE
# ─────────────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("THE FOUR AGENT DATA CLASSES")
print("=" * 60)


# ── 1. Message ─────────────────────────────────────────────────────

@dataclass
class Message:
    """
    A single conversational message.

    @dataclass auto-generates:
        __init__(self, role, content, timestamp, token_count)
        __repr__  → Message(role='user', content='hello', ...)
        __eq__    → msg1 == msg2

    __post_init__ runs automatically after __init__ completes.
    We use it to auto-calculate token_count and validate role.
    """
    role         : str                              # "system"|"user"|"assistant"|"tool"
    content      : str
    timestamp    : datetime = field(default_factory=datetime.now)
    token_count  : int      = 0

    def __post_init__(self):
        """
        Runs automatically after __init__.
        Used for: derived fields, cross-field validation, type coercion.
        """
        # Validate role
        valid = {"system", "user", "assistant", "tool"}
        if self.role not in valid:
            raise ValueError(
                f"Invalid role '{self.role}'. Must be one of {valid}"
            )

        # Auto-calculate token_count if not provided
        # Approximation: 1 token ≈ 0.75 words (GPT convention)
        if self.token_count == 0 and self.content:
            self.token_count = max(1, int(len(self.content.split()) / 0.75))


# ── 2. ToolCall ────────────────────────────────────────────────────

@dataclass
class ToolCall:
    """
    A request from the agent to invoke a specific tool.

    call_id uses default_factory with a lambda to generate a
    unique 8-character ID for each instance automatically.
    """
    tool_name   : str
    arguments   : dict = field(default_factory=dict)                         # mutable default → field()
    call_id     : str  = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_prompt_string(self) -> str:
        """Format this tool call for embedding in an LLM conversation."""
        args = ", ".join(f"{k}={v!r}" for k, v in self.arguments.items())
        return (
            f"<tool_call "
            f"name='{self.tool_name}' "
            f"id='{self.call_id}'>"
            f"{args}"
            f"</tool_call>"
        )


# ── 3. ToolResult (frozen) ─────────────────────────────────────────

@dataclass(frozen=True)    # frozen=True → immutable after creation
class ToolResult:
    """
    The outcome of one tool call.

    frozen=True means:
      - All fields are set ONCE at construction time
      - Any attempt to reassign a field raises FrozenInstanceError
      - The object becomes hashable (can be used in sets and as dict keys)

    Why freeze tool results?
      - Results should not be modified after they are returned
      - Accidental mutation during pipeline processing is a silent bug
      - Immutability makes reasoning about data flow much simpler
    """
    call_id  : str
    success  : bool
    output   : str
    error    : Optional[str] = None

    def to_message(self) -> Message:
        """Convert this result into a Message for the conversation history."""
        content = self.output if self.success else f"Tool error: {self.error}"
        return Message(role="tool", content=content)

    def summary(self) -> str:
        icon = "OK" if self.success else "FAIL"
        return f"[{icon}] {self.call_id}: {self.output[:60]}"


# ── 4. AgentTurn ───────────────────────────────────────────────────

@dataclass
class AgentTurn:
    """
    Everything produced by the agent in one complete turn.

    Contains: messages, tool calls, tool results.
    total_tokens is a @property — computed dynamically from messages.
    finished is mutable — updated when the turn completes.
    """
    turn_number  : int
    messages     : list = field(default_factory=list)    # List[Message]
    tool_calls   : list = field(default_factory=list)    # List[ToolCall]
    tool_results : list = field(default_factory=list)    # List[ToolResult]
    finished     : bool = False

    @property
    def total_tokens(self) -> int:
        """Computed from the token_count of all Message objects in this turn."""
        return sum(
            m.token_count
            for m in self.messages
            if isinstance(m, Message)
        )

    def add_message(self, role: str, content: str) -> Message:
        """Helper: create a Message and append it in one call."""
        msg = Message(role=role, content=content)
        self.messages.append(msg)
        return msg

    def add_tool_call(self, tool_name: str, arguments: dict) -> ToolCall:
        """Helper: create a ToolCall and append it."""
        call = ToolCall(tool_name=tool_name, arguments=arguments)
        self.tool_calls.append(call)
        return call

    def add_tool_result(
        self, call_id: str, success: bool,
        output: str, error: Optional[str] = None
    ) -> ToolResult:
        """Helper: create a ToolResult and append it."""
        result = ToolResult(
            call_id=call_id, success=success,
            output=output, error=error
        )
        self.tool_results.append(result)
        return result

    def summary(self) -> str:
        return (
            f"AgentTurn #{self.turn_number}: "
            f"{len(self.messages)} message(s), "
            f"{len(self.tool_calls)} tool call(s), "
            f"{self.total_tokens} total tokens, "
            f"finished={self.finished}"
        )


# ─────────────────────────────────────────────────────────────────────
#  DEMO
# ─────────────────────────────────────────────────────────────────────

print("\n── Message: auto-generated __init__ and __repr__ ────────────")
sys_msg  = Message(role="system",    content="You are a research assistant with web access.")
user_msg = Message(role="user",      content="Find recent papers on multi-agent RAG systems.")
asst_msg = Message(role="assistant", content="I will search for that now.")

for msg in [sys_msg, user_msg, asst_msg]:
    print(f"  {msg}")

print("\n── Message: token_count auto-calculated in __post_init__ ─────")
print(f"  sys_msg.token_count  = {sys_msg.token_count}")
print(f"  user_msg.token_count = {user_msg.token_count}")
print(f"  asst_msg.token_count = {asst_msg.token_count}")

print("\n── Message: validation in __post_init__ ─────────────────────")
try:
    bad = Message(role="admin", content="test")
except ValueError as e:
    print(f"  ValueError: {e}")

print("\n── ToolCall: unique call_id auto-generated ──────────────────")
call1 = ToolCall(tool_name="web_search", arguments={"query": "multi-agent RAG 2024", "n": 5})
call2 = ToolCall(tool_name="calculator", arguments={"expression": "2 ** 10"})
print(f"  call1: {call1}")
print(f"  call2: {call2}")
print(f"  IDs are unique: {call1.call_id} != {call2.call_id} → {call1.call_id != call2.call_id}")
print(f"  Prompt format : {call1.to_prompt_string()}")

print("\n── ToolResult: frozen=True prevents mutation ─────────────────")
result = ToolResult(
    call_id=call1.call_id,
    success=True,
    output="Found 12 papers on multi-agent RAG. Top: 'Self-RAG' (arXiv 2310.11511)"
)
print(f"  {result.summary()}")
print(f"  As Message: {result.to_message()}")

try:
    result.success = False            # Should fail — object is frozen!
except Exception as e:
    print(f"  Mutation blocked: {type(e).__name__}: {e}")

print("\n── AgentTurn: composing a full turn ─────────────────────────")
turn = AgentTurn(turn_number=1)

turn.add_message("system",    "You are a research assistant.")
turn.add_message("user",      "Find papers on multi-agent RAG.")
call = turn.add_tool_call("web_search", {"query": "multi-agent RAG 2024"})
result2 = turn.add_tool_result(call.call_id, True, "Found 12 papers.")
turn.add_message("assistant", "I found 12 papers on multi-agent RAG.")

turn.finished = True

print(f"  {turn.summary()}")
print(f"  total_tokens (property): {turn.total_tokens}")

print("\n── @dataclass equality: compares field values ───────────────")
m_a = Message(role="user", content="hello", token_count=1)
m_b = Message(role="user", content="hello", token_count=1)
m_c = Message(role="user", content="world", token_count=1)
print(f"  same content : m_a == m_b → {m_a == m_b}")
print(f"  diff content : m_a == m_c → {m_a == m_c}")

print("\n── frozen ToolResult is hashable (usable in sets) ───────────")
r1 = ToolResult(call_id="abc", success=True, output="result1")
r2 = ToolResult(call_id="def", success=True, output="result2")
result_set = {r1, r2}
print(f"  Set of ToolResults: {len(result_set)} items (frozen → hashable)")

print("\n── Key takeaways ────────────────────────────────────────────")
print("""
  @dataclass              → auto-generates __init__, __repr__, __eq__
  field(default_factory)  → ALWAYS use for list/dict defaults (never = [])
  __post_init__           → for computed fields and cross-field validation
  frozen=True             → immutable; also makes object hashable
  @property inside        → computed attribute, not stored in __init__
  
  Data class hierarchy:
    Message      → one conversational message (role + content + tokens)
    ToolCall     → one tool invocation request (name + args + id)
    ToolResult   → one tool outcome (frozen, immutable)
    AgentTurn    → one complete agent turn (contains all the above)
""")
