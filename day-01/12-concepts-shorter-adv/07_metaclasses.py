# CONCEPT 7 — METACLASSES
# A metaclass is the "class of a class" — controls HOW classes are created.
# When Python reads:  class Foo(Bar): ...
#   it calls:         ToolMeta.__new__(ToolMeta, "Foo", (Bar,), {body})
# We intercept that call to auto-register every tool in a catalog.

class ToolMeta(type):
    catalog = {}                              # {tool_name: class}

    def __new__(mcs, name, bases, ns):
        cls = super().__new__(mcs, name, bases, ns)
        if bases:                             # skip the base class itself
            key = getattr(cls, "tool_name", name.lower())
            mcs.catalog[key] = cls
            print(f"  [ToolMeta] Registered: '{key}' ({name})")
        return cls

class Tool(metaclass=ToolMeta):               # base — not registered
    tool_name = None
    def execute(self, q): raise NotImplementedError

# ── Just defining these classes registers them automatically ──────────
class WebSearch(Tool):
    """Searches the web for current information."""
    tool_name = "web_search"
    def execute(self, q): return f"[Web] Results for: {q}"

class Calculator(Tool):
    """Evaluates math expressions."""
    tool_name = "calculator"
    def execute(self, q): return f"[Calc] {q} = {eval(q)}"

class CodeRunner(Tool):
    """Runs Python code snippets."""
    tool_name = "code_runner"
    def execute(self, q): return f"[Code] Executed: {q[:30]}"

# ── Demo ──────────────────────────────────────────────────────────────
print(f"\nAll registered tools: {list(ToolMeta.catalog.keys())}")

tool = ToolMeta.catalog["web_search"]()   # fetch from catalog + instantiate
print(tool.execute("multi-agent RAG"))

print("\nTool descriptions for LLM prompt:")
for name, cls in ToolMeta.catalog.items():
    print(f"  {name}: {cls.__doc__.strip()}")
