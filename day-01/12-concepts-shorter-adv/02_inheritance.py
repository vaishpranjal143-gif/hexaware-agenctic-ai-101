# CONCEPT 2 — INHERITANCE
# Child class reuses parent code via super(). Override only what changes.

class BaseAgent:
    def __init__(self, name, model):
        self.name, self.model, self.memory = name, model, []

    def remember(self, text):           # defined once — all agents get it free
        self.memory.append(text)

    def introduce(self):
        return f"I am {self.name} ({self.__class__.__name__}, {self.model})"

    def run(self, task):                # hook — subclasses must override
        raise NotImplementedError

class ResearchAgent(BaseAgent):
    def __init__(self, name, model, sources):
        super().__init__(name, model)   # ← always call super() first
        self.sources = sources

    def run(self, task):                # override with research-specific logic
        self.remember(task)
        return f"[Research] Searched {self.sources} for: {task}"

class CoderAgent(BaseAgent):
    def __init__(self, name, model, lang="python"):
        super().__init__(name, model)
        self.lang = lang

    def run(self, task):
        self.remember(task)
        return f"[Code/{self.lang}] def solution(): # {task}"

# ── Demo ──────────────────────────────────────────────────────────────
r = ResearchAgent("Aria", "gpt-4",    sources=["arxiv", "wikipedia"])
c = CoderAgent   ("Dev",  "claude-3", lang="python")

print(r.introduce())
print(r.run("Transformer attention mechanisms"))
print(c.run("Chunk a list into batches"))
print(f"Aria memory: {r.memory}")     # inherited from BaseAgent ✓
