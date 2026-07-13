"""
╔══════════════════════════════════════════════════════════════════════╗
║  CONCEPT 7 — METACLASSES                                            ║
║  File    : 07_metaclasses.py                                        ║
║  Run     : python 07_metaclasses.py                                 ║
╠══════════════════════════════════════════════════════════════════════╣
║  WHAT IS IT?                                                        ║
║  A metaclass is the "class of a class". It controls HOW a class     ║
║  is created, just like a class controls HOW an object is created.   ║
║                                                                     ║
║  MENTAL MODEL:                                                      ║
║    object = MyClass()          → MyClass controls object creation   ║
║    MyClass = MyMeta(...)       → MyMeta controls class creation      ║
║                                                                     ║
║  WHAT HAPPENS WHEN PYTHON READS: class Foo(Bar): ...               ║
║    Python calls: type.__new__(type, "Foo", (Bar,), {body})          ║
║    A custom metaclass intercepts this call before Foo exists.       ║
║                                                                     ║
║  AGENTIC AI USE CASE: Auto-Registering Tool Catalog                 ║
║  Every tool class registers itself in a global catalog the instant  ║
║  Python reads its class definition. No manual registration needed.  ║
║  The agent discovers tools automatically.                           ║
╚══════════════════════════════════════════════════════════════════════╝
"""


# ─────────────────────────────────────────────────────────────────────
#  PART 1 — THE PROBLEM: Manual registration is error-prone
# ─────────────────────────────────────────────────────────────────────

print("=" * 60)
print("PART 1 — THE PROBLEM (manual registration)")
print("=" * 60)

TOOL_REGISTRY = {}

class ManualWebSearch:
    tool_name = "web_search"
    def execute(self, q): return f"Search: {q}"

class ManualCalculator:
    tool_name = "calculator"
    def execute(self, q): return f"Calc: {q}"

# Must manually register each tool — forgetting one is a silent bug!
TOOL_REGISTRY["web_search"] = ManualWebSearch
TOOL_REGISTRY["calculator"] = ManualCalculator
# ← What if a developer adds a new tool and forgets this line?

print(f"Manually registered: {list(TOOL_REGISTRY.keys())}")
print("Problem 1: Every new tool needs a manual registration line.")
print("Problem 2: Forgetting to register is a SILENT bug — no error raised.")
print("Problem 3: With 50 tools across 10 files, this becomes a maintenance nightmare.\n")


# ─────────────────────────────────────────────────────────────────────
#  PART 2 — THE SOLUTION: Metaclass for auto-registration
# ─────────────────────────────────────────────────────────────────────

print("=" * 60)
print("PART 2 — THE SOLUTION (Metaclass)")
print("=" * 60)

# ── Step 1: Understand how type works ────────────────────────────────

print("\n── How type() creates classes ───────────────────────────────")
# In Python, 'type' is the default metaclass.
# Every class you write is actually an instance of 'type'.
print(f"type(int)   = {type(int)}")
print(f"type(str)   = {type(str)}")
print(f"type(list)  = {type(list)}")

# You can even create a class dynamically using type():
DynamicClass = type("DynamicClass", (object,), {"hello": lambda self: "hi"})
obj = DynamicClass()
print(f"Dynamically created class: {obj.hello()}")
print()


# ── Step 2: Build the metaclass ───────────────────────────────────────

class ToolMeta(type):
    """
    Metaclass that auto-registers every subclass of RegisteredTool.

    How it works:
      When Python reads:  class WebSearch(RegisteredTool): ...
      Python calls:       ToolMeta.__new__(ToolMeta, "WebSearch", (RegisteredTool,), {body})

      Inside __new__:
        1. We let type create the class normally via super().__new__(...)
        2. We register it in our catalog before returning it

    Parameters of __new__:
        mcs        : the metaclass itself (ToolMeta)
        class_name : the name of the new class being created, e.g. "WebSearch"
        bases      : tuple of parent classes, e.g. (RegisteredTool,)
        namespace  : dict containing everything in the class body
    """

    catalog:  dict = {}   # { "web_search": WebSearch class }
    metadata: dict = {}   # { "web_search": {description, class_name, order} }
    _counter: int  = 0    # registration order counter

    def __new__(mcs, class_name, bases, namespace):
        # Step 1: Let type create the class normally
        cls = super().__new__(mcs, class_name, bases, namespace)

        # Step 2: Skip the base class RegisteredTool itself
        # (we only want to register actual tool implementations)
        is_base_class = (class_name == "RegisteredTool") or (not bases)
        if is_base_class:
            return cls

        # Step 3: Determine the registration key
        # Use cls.tool_name if explicitly set, else default to lowercase class name
        tool_key = getattr(cls, "tool_name", None) or class_name.lower()

        # Step 4: Increment the order counter (tells us registration sequence)
        mcs._counter += 1

        # Step 5: Register the class in the catalog
        mcs.catalog[tool_key] = cls

        # Step 6: Store metadata alongside the class
        mcs.metadata[tool_key] = {
            "description" : (cls.__doc__ or "No description provided.").strip(),
            "class_name"  : class_name,
            "order"       : mcs._counter,
        }

        # This print fires when the class is DEFINED, not when it's instantiated
        print(f"  [ToolMeta] Auto-registered: '{tool_key}' ({class_name})")
        return cls

    # ── Class methods on the metaclass (accessible as ToolMeta.xxx) ───

    @classmethod
    def get(mcs, tool_name: str):
        """
        Retrieve a fresh instance of the named tool.
        Raises KeyError with helpful message if tool not found.
        """
        if tool_name not in mcs.catalog:
            raise KeyError(
                f"Tool '{tool_name}' not in catalog.\n"
                f"  Available: {list(mcs.catalog.keys())}"
            )
        return mcs.catalog[tool_name]()    # instantiate and return

    @classmethod
    def all_names(mcs) -> list:
        """Return all registered tool names in registration order."""
        return sorted(
            mcs.catalog.keys(),
            key=lambda k: mcs.metadata[k]["order"]
        )

    @classmethod
    def for_llm_prompt(mcs) -> str:
        """
        Generate the 'Available tools:' block for an LLM system prompt.
        This is what you inject into the system message before the agent runs.
        """
        lines = ["Available tools:"]
        for key in mcs.all_names():
            desc = mcs.metadata[key]["description"]
            lines.append(f"  - {key}: {desc}")
        return "\n".join(lines)

    @classmethod
    def describe(mcs) -> str:
        """Pretty-print the full catalog."""
        lines = [f"Tool Catalog ({len(mcs.catalog)} tools):"]
        for key in mcs.all_names():
            meta = mcs.metadata[key]
            lines.append(
                f"  #{meta['order']:2d}  [{key}]  "
                f"class={meta['class_name']}  "
                f"desc='{meta['description'][:50]}'"
            )
        return "\n".join(lines)


# ── Step 3: Base class that triggers registration in all subclasses ───

class RegisteredTool(metaclass=ToolMeta):
    """
    Base class for all agent tools.
    Any class that inherits from this is automatically registered.

    The metaclass=ToolMeta argument means:
      ToolMeta.__new__() is called whenever a subclass of RegisteredTool
      is defined — even in a different file.
    """
    tool_name: str = None   # subclasses should set this to a short string

    def execute(self, query: str) -> str:
        """Override this in subclasses."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement execute()")


# ── Step 4: Just define the tool classes — registration is automatic ──

print("\nDefining tool classes (registration happens on class definition):")

class WebSearch(RegisteredTool):
    """Searches the web for current, up-to-date information about any topic."""
    tool_name = "web_search"

    def execute(self, query: str) -> str:
        return (
            f"[WebSearch] 3 results for '{query}':\n"
            f"  1. Wikipedia overview\n"
            f"  2. arXiv research paper\n"
            f"  3. Tutorial blog post"
        )


class Calculator(RegisteredTool):
    """Evaluates a mathematical expression and returns the numeric result."""
    tool_name = "calculator"

    def execute(self, query: str) -> str:
        try:
            result = eval(query)
            return f"[Calculator] {query} = {result}"
        except Exception as e:
            return f"[Calculator] Error: {e}"


class PythonREPL(RegisteredTool):
    """Executes a Python code snippet in a safe sandbox and returns the output."""
    tool_name = "python_repl"

    def execute(self, query: str) -> str:
        return f"[PythonREPL] Executed: {query[:50]}"


class MemoryLookup(RegisteredTool):
    """Retrieves a stored fact from the agent's long-term memory by key name."""
    tool_name = "memory_lookup"

    def execute(self, query: str) -> str:
        return f"[MemoryLookup] Fetching: '{query}'"


class FileReader(RegisteredTool):
    """Reads and returns the text content of a file at the specified path."""
    # No tool_name set → defaults to lowercase class name: "filereader"

    def execute(self, query: str) -> str:
        return f"[FileReader] Content of: '{query}'"


# ─────────────────────────────────────────────────────────────────────
#  DEMO
# ─────────────────────────────────────────────────────────────────────

print("\n── Catalog after all class definitions ─────────────────────")
print(ToolMeta.describe())

print("\n── LLM system prompt block ─────────────────────────────────")
print(ToolMeta.for_llm_prompt())

print("\n── Using ToolMeta.get() to fetch and run tools ──────────────")
tool = ToolMeta.get("web_search")
print(tool.execute("multi-agent systems 2024"))

print()
tool2 = ToolMeta.get("calculator")
print(tool2.execute("(2 ** 10) * 1.5"))

print()
tool3 = ToolMeta.get("python_repl")
print(tool3.execute("print('Hello from the agent!')"))

print("\n── Fetching a non-existent tool raises helpful KeyError ─────")
try:
    ToolMeta.get("voice_assistant")
except KeyError as e:
    print(f"  KeyError:\n  {e}")

print("\n── Adding a new tool at runtime — still auto-registers ──────")
print("Defining SentimentAnalyzer now:")

class SentimentAnalyzer(RegisteredTool):
    """Analyses the emotional tone of a text as positive, neutral, or negative."""
    tool_name = "sentiment"

    def execute(self, query: str) -> str:
        # Simple heuristic for demo — real version uses an ML model
        positive_words = ["great", "excellent", "good", "love", "amazing"]
        score = sum(1 for w in query.lower().split() if w in positive_words)
        tone  = "positive" if score > 0 else "neutral"
        return f"[Sentiment] '{query}' → {tone} (score: {score})"


print(f"\nUpdated catalog: {ToolMeta.all_names()}")
print(ToolMeta.get("sentiment").execute("This AI agent is great and amazing!"))

print("\n── Demonstrate metaclass hierarchy ──────────────────────────")
print(f"type(RegisteredTool) = {type(RegisteredTool)}")    # → ToolMeta
print(f"type(WebSearch)      = {type(WebSearch)}")          # → ToolMeta
print(f"type(ToolMeta)       = {type(ToolMeta)}")           # → type (built-in)

# Every registered tool IS an instance of ToolMeta (as a class)
print(f"\nAll tool classes are instances of ToolMeta:")
for name in ToolMeta.all_names():
    cls = ToolMeta.catalog[name]
    print(f"  isinstance({name} class, ToolMeta) = {isinstance(cls, ToolMeta)}")

print("\n── Key takeaways ────────────────────────────────────────────")
print("""
  1. metaclass=ToolMeta → ToolMeta.__new__() fires on every subclass definition
  2. Registration happens at IMPORT TIME — before any agent code runs
  3. Adding a new tool only requires writing a class — zero extra code
  4. Forgetting to inherit from RegisteredTool = tool is not in catalog
  5. ToolMeta.catalog stores classes; ToolMeta.metadata stores descriptions
  6. type is Python's built-in metaclass — every class is an instance of type
  7. Use case: plugin systems, ORMs (Django models), command registries
""")
