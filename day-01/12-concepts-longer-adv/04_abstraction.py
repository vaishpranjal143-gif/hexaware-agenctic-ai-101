"""
╔══════════════════════════════════════════════════════════════════════╗
║  CONCEPT 4 — ABSTRACTION                                            ║
║  File    : 04_abstraction.py                                        ║
║  Run     : python 04_abstraction.py                                 ║
╠══════════════════════════════════════════════════════════════════════╣
║  WHAT IS IT?                                                        ║
║  Hiding complex implementation behind a clean interface.            ║
║  An abstract class defines a CONTRACT — a set of methods that       ║
║  every subclass MUST implement. You cannot instantiate it directly. ║
║                                                                     ║
║  KEY TOOLS IN PYTHON:                                               ║
║    from abc import ABC, abstractmethod                              ║
║    class MyBase(ABC):                   → abstract base class       ║
║    @abstractmethod def my_method():     → must be implemented       ║
║    @property @abstractmethod            → abstract property         ║
║                                                                     ║
║  AGENTIC AI USE CASE: Abstract Tool Interface                       ║
║  Every agent tool must implement execute() and validate_input().    ║
║  The base class provides safe_execute() (error boundary) for free.  ║
║  If a tool forgets to implement anything, Python raises TypeError.  ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import sys
import io
from abc import ABC, abstractmethod


# ─────────────────────────────────────────────────────────────────────
#  PART 1 — THE PROBLEM: No contract, inconsistent interfaces
# ─────────────────────────────────────────────────────────────────────

print("=" * 60)
print("PART 1 — THE PROBLEM (no contract enforced)")
print("=" * 60)

class BadSearchTool:
    def search(self, query):           # ← method named 'search' not 'execute'
        return f"Results: {query}"

class BadCalcTool:
    def run(self, expression):         # ← named 'run' not 'execute'
        return eval(expression)

class BadCodeTool:
    def execute(self, code):           # ← only this one uses 'execute'
        return f"Ran: {code}"

tools = [BadSearchTool(), BadCalcTool(), BadCodeTool()]

print("Trying to call .execute() on all three tools:")
for tool in tools:
    try:
        print(tool.execute("test"))
    except AttributeError as e:
        print(f"  FAILED: {e}")

print("\nProblem: No consistent interface. Dispatcher cannot work reliably.")
print("Problem: Errors only appear at runtime, not at class definition.\n")


# ─────────────────────────────────────────────────────────────────────
#  PART 2 — THE SOLUTION: Abstract Base Class (ABC)
# ─────────────────────────────────────────────────────────────────────

print("=" * 60)
print("PART 2 — THE SOLUTION (Abstract Base Class)")
print("=" * 60)


class BaseTool(ABC):
    """
    Abstract contract for ALL tools in the agent ecosystem.

    This class CANNOT be instantiated directly. It only serves as a template.
    Any class inheriting from BaseTool MUST implement:
        description      (abstract property)
        execute()        (abstract method)
        validate_input() (abstract method)

    Any class inheriting from BaseTool GETS FOR FREE:
        safe_execute()   (concrete shared method — error boundary)
        for_llm_prompt() (concrete shared method — prompt formatting)
        __repr__         (concrete shared method)

    Python enforces the contract at instantiation time — not at runtime.
    If a subclass forgets to implement any abstract member, Python raises
    TypeError when you try to create an instance of that subclass.
    """

    # ── ABSTRACT PROPERTY — subclasses MUST define this ──────────────

    @property
    @abstractmethod
    def description(self) -> str:
        """
        One-sentence description used by the LLM to select this tool.
        Example: "Searches the web for current, up-to-date information."
        """
        pass

    # ── ABSTRACT METHODS — subclasses MUST implement both ─────────────

    @abstractmethod
    def execute(self, input_data: str) -> dict:
        """
        Perform the tool's actual work.

        MUST return a dict with exactly these keys:
            {"success": bool, "result": str, "tool": str}

        Returning anything else will break the dispatcher.
        """
        pass

    @abstractmethod
    def validate_input(self, input_data: str) -> bool:
        """
        Check whether input_data is valid before doing any work.

        Return True  → input is usable, proceed with execute()
        Return False → input is bad, return an error dict

        Common checks: non-empty, correct type, no dangerous keywords.
        """
        pass

    # ── CONCRETE METHODS — provided for free, do NOT override ─────────

    def safe_execute(self, input_data: str) -> dict:
        """
        Shared error boundary for ALL tools.
        This is the ONLY way agents should invoke a tool.

        Flow:
          1. Validate input (calls your validate_input())
          2. If valid, call execute() (calls your execute())
          3. If execute() raises an exception, catch it gracefully
          4. Always return a well-formed dict

        Because this is concrete (not abstract), subclasses inherit it
        without having to implement it. One place to maintain.
        """
        tool_name = self.__class__.__name__

        # Step 1: validate
        try:
            is_valid = self.validate_input(input_data)
        except Exception as exc:
            return {
                "success" : False,
                "result"  : f"Validation error: {exc}",
                "tool"    : tool_name,
            }

        if not is_valid:
            return {
                "success" : False,
                "result"  : f"Invalid input: '{input_data}'",
                "tool"    : tool_name,
            }

        # Step 2: execute
        try:
            return self.execute(input_data)
        except Exception as exc:
            return {
                "success" : False,
                "result"  : f"Tool error during execute(): {exc}",
                "tool"    : tool_name,
            }

    def for_llm_prompt(self) -> str:
        """
        Generate the tool definition for an LLM system prompt.
        Concrete: every tool gets this automatically from the base class.
        """
        return (
            f"- tool_name  : {self.__class__.__name__}\n"
            f"  description: {self.description}\n"
            f"  input      : plain string"
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(description='{self.description[:45]}...')"


# ─────────────────────────────────────────────────────────────────────
#  CONCRETE TOOL IMPLEMENTATIONS
# ─────────────────────────────────────────────────────────────────────

class SerpAPITool(BaseTool):
    """Web search tool backed by the Serp API."""

    @property
    def description(self) -> str:
        return "Searches the web for current, up-to-date information."

    def validate_input(self, input_data: str) -> bool:
        # Must be a non-empty string of at least 3 characters
        if not isinstance(input_data, str):
            return False
        return len(input_data.strip()) >= 3

    def execute(self, input_data: str) -> dict:
        # Real version: response = requests.get(SERP_URL, params={"q": input_data})
        return {
            "success" : True,
            "result"  : (
                f"Top results for '{input_data}':\n"
                f"  1. Wikipedia: Overview\n"
                f"  2. arXiv paper\n"
                f"  3. Blog tutorial"
            ),
            "tool"    : "SerpAPITool",
        }


class PythonREPLTool(BaseTool):
    """Safe Python code execution tool."""

    BLOCKED_KEYWORDS = [
        "import os", "import sys", "open(",
        "__import__", "subprocess", "eval(", "exec(",
    ]

    @property
    def description(self) -> str:
        return "Executes a Python code snippet and returns the printed output."

    def validate_input(self, input_data: str) -> bool:
        if not isinstance(input_data, str) or len(input_data.strip()) < 2:
            return False
        # Block dangerous patterns
        for blocked in self.BLOCKED_KEYWORDS:
            if blocked in input_data:
                return False
        return True

    def execute(self, input_data: str) -> dict:
        buf        = io.StringIO()
        sys.stdout = buf
        try:
            exec(
                input_data,
                {"__builtins__": {
                    "print": print, "range": range,
                    "sum": sum, "len": len, "max": max,
                }}
            )
            output = buf.getvalue().strip()
        finally:
            sys.stdout = sys.__stdout__

        return {
            "success" : True,
            "result"  : output or "(executed with no printed output)",
            "tool"    : "PythonREPLTool",
        }


class MemoryReadTool(BaseTool):
    """Reads facts from the agent's in-memory key-value store."""

    def __init__(self, memory_store: dict):
        self._memory = memory_store

    @property
    def description(self) -> str:
        return "Reads a stored fact from the agent's long-term memory by key."

    def validate_input(self, input_data: str) -> bool:
        return isinstance(input_data, str) and len(input_data.strip()) > 0

    def execute(self, input_data: str) -> dict:
        key   = input_data.strip()
        value = self._memory.get(key)

        if value is None:
            return {
                "success" : False,
                "result"  : f"Key '{key}' not found in agent memory.",
                "tool"    : "MemoryReadTool",
            }

        return {
            "success" : True,
            "result"  : f"memory['{key}'] = {value}",
            "tool"    : "MemoryReadTool",
        }


class IncompleteToolError(BaseTool):
    """
    INTENTIONALLY INCOMPLETE — missing description property and execute().
    Used to demonstrate what happens when a subclass forgets an abstract member.
    """
    def validate_input(self, input_data: str) -> bool:
        return True
    # description and execute() are NOT implemented


# ─────────────────────────────────────────────────────────────────────
#  DEMO
# ─────────────────────────────────────────────────────────────────────

print("\n── Abstract class cannot be instantiated directly ───────────")
try:
    t = BaseTool()
except TypeError as e:
    print(f"  TypeError: {e}")

print("\n── Incomplete subclass also fails at instantiation ──────────")
try:
    bad = IncompleteToolError()
except TypeError as e:
    print(f"  TypeError: {e}")
    print("  → Python enforces the contract BEFORE any code runs.")

print("\n── Creating properly implemented tools ─────────────────────")
memory = {
    "user_goal" : "Build a research agent",
    "last_topic": "RAG systems",
}

tools = [
    SerpAPITool(),
    PythonREPLTool(),
    MemoryReadTool(memory),
]
for t in tools:
    print(f"  {repr(t)}")

print("\n── Tool definitions for LLM system prompt ──────────────────")
print("Available tools:")
for t in tools:
    print(t.for_llm_prompt())

print("\n── safe_execute: valid inputs ──────────────────────────────")
r = tools[0].safe_execute("multi-agent RAG systems 2024")
print(f"1. Web search:\n   success={r['success']}, result snippet='{r['result'][:60]}...'")

r = tools[1].safe_execute("for i in range(3):\n    print(f'Agent step {i}')")
print(f"\n2. Code runner:\n   success={r['success']}, result='{r['result']}'")

r = tools[2].safe_execute("user_goal")
print(f"\n3. Memory read (key exists):\n   success={r['success']}, result='{r['result']}'")

print("\n── safe_execute: invalid / error inputs ────────────────────")
print("4. Too-short search query:")
print("  ", tools[0].safe_execute("ai"))

print("\n5. Dangerous code blocked by validate_input:")
print("  ", tools[1].safe_execute("import os; os.system('ls')"))

print("\n6. Memory read — key missing:")
print("  ", tools[2].safe_execute("budget_remaining"))

print("\n── All tools share the same safe_execute() interface ────────")
def run_all_tools(tools: list, query: str):
    """Works for any tool — polymorphism + abstraction together."""
    print(f"  Query: '{query}'")
    for tool in tools:
        r = tool.safe_execute(query)
        icon = "OK" if r["success"] else "FAIL"
        print(f"  [{icon}] {r['tool']}: {r['result'][:60]}")

run_all_tools(tools, "user_goal")

print("\n── Key takeaways ────────────────────────────────────────────")
print("""
  1. ABC prevents instantiating incomplete classes
  2. @abstractmethod forces subclasses to implement that method
  3. @property @abstractmethod forces a computed attribute
  4. safe_execute() is written ONCE in the base class — all tools inherit it
  5. Callers only need to call .safe_execute() — never .execute() directly
  6. The contract is enforced at class creation time, not runtime
""")
