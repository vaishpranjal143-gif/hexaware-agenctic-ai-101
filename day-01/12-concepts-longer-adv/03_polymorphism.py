"""
╔══════════════════════════════════════════════════════════════════════╗
║  CONCEPT 3 — POLYMORPHISM                                           ║
║  File    : 03_polymorphism.py                                       ║
║  Run     : python 03_polymorphism.py                                ║
╠══════════════════════════════════════════════════════════════════════╣
║  WHAT IS IT?                                                        ║
║  The same method call produces different results depending on the   ║
║  type of object it's called on. 'poly' = many, 'morph' = forms.    ║
║                                                                     ║
║  TWO KINDS IN PYTHON:                                               ║
║    Subclass polymorphism  — override a method in a child class      ║
║    Duck typing            — "if it has .execute(), it works"        ║
║                             (Python's preferred style)              ║
║                                                                     ║
║  AGENTIC AI USE CASE: Tool Dispatcher                               ║
║  An agent dispatcher calls .execute(query) on any tool without      ║
║  knowing or caring what type it is. Adding a new tool requires      ║
║  zero changes to the dispatcher.                                    ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import sys
import io


# ─────────────────────────────────────────────────────────────────────
#  PART 1 — THE PROBLEM: Type-checking dispatcher (anti-pattern)
# ─────────────────────────────────────────────────────────────────────

print("=" * 60)
print("PART 1 — THE PROBLEM (if/elif type-checking)")
print("=" * 60)

class BadDispatcher:
    """
    Every time a new tool is added, this function must be updated.
    This violates the Open/Closed Principle:
      Open for EXTENSION (new tools)
      Closed for MODIFICATION (shouldn't touch dispatch code)
    """
    @staticmethod
    def dispatch(tool_type: str, query: str) -> str:
        if tool_type == "search":
            return f"Searching for: {query}"
        elif tool_type == "calculator":
            return f"Calculating: {query}"
        elif tool_type == "code":
            return f"Running code: {query}"
        # ← Adding a new tool means editing this function — FRAGILE!
        else:
            return f"Unknown tool type: {tool_type}"

print(BadDispatcher.dispatch("search", "LLM benchmarks"))
print(BadDispatcher.dispatch("calculator", "25 * 4"))
print("Problem: Must edit dispatch() every time a new tool is added.\n")


# ─────────────────────────────────────────────────────────────────────
#  PART 2 — THE SOLUTION: Polymorphism via a common interface
# ─────────────────────────────────────────────────────────────────────

print("=" * 60)
print("PART 2 — THE SOLUTION (Polymorphism)")
print("=" * 60)


# ── Tool classes — same interface (.name() and .execute()), different behaviour ──

class WebSearchTool:
    """Searches the web for current information."""

    def name(self) -> str:
        return "web_search"

    def execute(self, query: str) -> str:
        # Real version: calls Serper, Bing, or Google Search API
        return (
            f"[WebSearch] 3 results for '{query}':\n"
            f"  1. Wikipedia: Overview of '{query}'\n"
            f"  2. arXiv:2401.00001 — Research paper on '{query}'\n"
            f"  3. Medium: A practical guide to '{query}'"
        )


class CalculatorTool:
    """Evaluates mathematical expressions safely."""

    def name(self) -> str:
        return "calculator"

    def execute(self, query: str) -> str:
        # Only allow pure math — block non-numeric characters for safety
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in query):
            return f"[Calculator] Blocked: '{query}' contains non-math characters."
        try:
            result = eval(query)          # safe here because we filtered input
            return f"[Calculator] {query} = {result}"
        except Exception as e:
            return f"[Calculator] Error evaluating '{query}': {e}"


class CodeRunnerTool:
    """Executes Python code snippets and returns the output."""

    def name(self) -> str:
        return "code_runner"

    def execute(self, query: str) -> str:
        # Capture print() output using StringIO
        buffer     = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buffer
        try:
            exec(
                query,
                {"__builtins__": {"print": print, "range": range, "len": len}}
            )
            output = buffer.getvalue().strip()
        except Exception as e:
            output = f"Error: {e}"
        finally:
            sys.stdout = old_stdout

        return (
            f"[CodeRunner] Executed: {query[:50]}\n"
            f"  Output: {output or '(no output)'}"
        )


class WikipediaTool:
    """Fetches article summaries from Wikipedia."""

    def name(self) -> str:
        return "wikipedia"

    def execute(self, query: str) -> str:
        # Real version: calls wikipedia-api or requests Wikipedia REST API
        return (
            f"[Wikipedia] Summary for '{query}':\n"
            f"  '{query}' is a concept in computer science and AI research. "
            f"It was introduced in..."
        )


class TranslatorTool:
    """Translates text between languages."""

    def name(self) -> str:
        return "translator"

    def execute(self, query: str) -> str:
        # Real version: calls DeepL or Google Translate API
        return (
            f"[Translator] '{query}' (EN → FR):\n"
            f"  Translated: '{query[:20]}...' → (French translation)"
        )


# ─────────────────────────────────────────────────────────────────────
#  THE DISPATCHER — works for ANY tool with no changes ever
# ─────────────────────────────────────────────────────────────────────

def dispatch_all(tools: list, query: str):
    """
    Calls .execute(query) on every tool in the list.

    KEY POINT: This function has NO if/elif for tool types.
    It only uses the shared interface: .name() and .execute().
    Adding a 10th tool? Just append it to the list — nothing here changes.
    """
    print(f"\nDispatching query: '{query}'")
    print("-" * 55)
    for tool in tools:
        result = tool.execute(query)    # ← POLYMORPHIC: same call, different output
        print(result)
        print()


def dispatch_one(tools: list, query: str) -> str:
    """
    Heuristic router: picks the SINGLE best tool for a query.
    Still uses .execute() — same interface throughout.
    """
    query_lower = query.lower()

    # Math: check if the query looks like arithmetic
    if all(c in "0123456789+-*/(). " for c in query.replace(" ", "")):
        best = "calculator"
    # Search: explicit keywords
    elif any(kw in query_lower for kw in ["search", "find", "what is", "explain", "how"]):
        best = "web_search"
    # Translation
    elif any(kw in query_lower for kw in ["translate", "french", "spanish", "german"]):
        best = "translator"
    # Code: explicit keywords
    elif any(kw in query_lower for kw in ["run", "execute", "code", "print"]):
        best = "code_runner"
    else:
        best = tools[0].name()    # fallback to first tool

    chosen = next((t for t in tools if t.name() == best), tools[0])
    print(f"\n[Router] '{query}' → best tool: {chosen.name()}")
    return chosen.execute(query)


# ─────────────────────────────────────────────────────────────────────
#  DEMO
# ─────────────────────────────────────────────────────────────────────

print("\n── Creating the tool registry ──────────────────────────────")
tools = [
    WebSearchTool(),
    CalculatorTool(),
    CodeRunnerTool(),
    WikipediaTool(),
]

for t in tools:
    print(f"  Registered: {t.name()}")

print("\n── dispatch_all: math query → each tool responds differently")
dispatch_all(tools, "25 * 4 + 10")

print("\n── dispatch_all: text query → each tool responds differently")
dispatch_all(tools, "latest AI agent frameworks")

print("\n── dispatch_one: smart routing ─────────────────────────────")
queries = [
    "144 / 12 * 5",
    "search for RAG system architecture",
    "translate hello to French",
    "run: for i in range(3): print(f'step {i}')",
]

for q in queries:
    result = dispatch_one(tools, q)
    print(f"  Result: {result[:80]}...")
    print()

print("\n── Adding a new tool — dispatch_all needs ZERO changes ─────")
tools.append(TranslatorTool())
print(f"  Added TranslatorTool. Total tools: {len(tools)}")

# dispatch_all automatically includes the new tool — no edits needed
dispatch_all(tools[:2] + [tools[-1]], "What is an embedding?")

print("\n── Duck typing — any object with .execute() works ──────────")

class MockTool:
    """
    Not a subclass of anything.
    Python doesn't care — if it has .name() and .execute(), it works.
    This is 'duck typing': if it walks like a duck and quacks like a duck...
    """
    def name(self) -> str:
        return "mock_tool"

    def execute(self, query: str) -> str:
        return f"[MockTool] Processing: '{query}'"

tools_with_mock = [WebSearchTool(), MockTool()]
dispatch_all(tools_with_mock, "test query")

print("── Key takeaways ────────────────────────────────────────────")
print("""
  1. Polymorphism = same method name, different behaviour per class
  2. dispatch_all() never uses isinstance() or if/elif
  3. Adding a new tool only requires a new class + appending to list
  4. Duck typing: Python checks .execute() at runtime, not class type
  5. Open/Closed Principle: extend by adding classes, not by editing dispatch
""")
