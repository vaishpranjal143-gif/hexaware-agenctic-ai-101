# CONCEPT 4 — ABSTRACTION
# Define a contract (interface) every tool must follow.
# ABC + @abstractmethod = Python enforces the contract at class creation time.

from abc import ABC, abstractmethod

class BaseTool(ABC):
    @property
    @abstractmethod
    def description(self): pass           # every tool must have a description

    @abstractmethod
    def execute(self, input_data): pass   # every tool must implement this

    @abstractmethod
    def validate(self, input_data): pass  # every tool must validate input

    def safe_run(self, input_data):       # shared logic — provided FREE to all tools
        if not self.validate(input_data):
            return {"ok": False, "result": "Invalid input"}
        try:
            return self.execute(input_data)
        except Exception as e:
            return {"ok": False, "result": str(e)}

class WebSearch(BaseTool):
    @property
    def description(self): return "Searches the web for information"
    def validate(self, q):  return isinstance(q, str) and len(q) > 2
    def execute(self, q):   return {"ok": True, "result": f"Results for '{q}'"}

class Calculator(BaseTool):
    @property
    def description(self): return "Evaluates math expressions"
    def validate(self, q):  return all(c in "0123456789+-*/() ." for c in q)
    def execute(self, q):   return {"ok": True, "result": f"{q} = {eval(q)}"}

# ── Demo ──────────────────────────────────────────────────────────────
try:    BaseTool()                         # cannot instantiate abstract class
except TypeError as e: print(f"Abstract blocked: {e}")

for tool in [WebSearch(), Calculator()]:
    print(f"\n{tool.__class__.__name__}: {tool.description}")
    print(tool.safe_run("RAG systems"))    # valid input
    print(tool.safe_run(""))              # invalid — caught by safe_run
