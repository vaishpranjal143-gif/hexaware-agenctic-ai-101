# CONCEPT 3 — POLYMORPHISM
# Same method name, different behaviour per class.
# dispatch() calls .execute() on ANY tool — no isinstance(), no if/elif.

class WebSearchTool:
    def name(self): return "web_search"
    def execute(self, q): return f"[Web]   Top 3 results for '{q}'"

class CalculatorTool:
    def name(self): return "calculator"
    def execute(self, q):
        try:    return f"[Calc]  {q} = {eval(q)}"
        except: return f"[Calc]  Cannot evaluate '{q}'"

class CodeRunnerTool:
    def name(self): return "code_runner"
    def execute(self, q): return f"[Code]  Executed: {q[:40]}"

def dispatch(tools, query):
    """Works for ANY tool with .name() and .execute() — no type checking ever."""
    print(f"\nQuery: '{query}'")
    for tool in tools:
        print(f"  {tool.execute(query)}")   # same call → different output

# ── Demo ──────────────────────────────────────────────────────────────
tools = [WebSearchTool(), CalculatorTool(), CodeRunnerTool()]
dispatch(tools, "25 * 4 + 10")
dispatch(tools, "latest AI research")

# Adding a new tool needs ZERO changes to dispatch()
class TranslatorTool:
    def name(self): return "translator"
    def execute(self, q): return f"[Trans] '{q}' → (French)"

tools.append(TranslatorTool())
dispatch(tools, "What is RAG?")
