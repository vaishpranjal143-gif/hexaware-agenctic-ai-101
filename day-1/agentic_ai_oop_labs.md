# OOP for Agentic AI Engineers — Practical Lab Exercises

> Each lab maps one OOP concept to a real component you will build in agentic AI systems.
> Every exercise gives you a scaffold to complete — not just code to read.

---

## Basic OOP Labs

---

### Lab 1 — Encapsulation: Build an LLM API Client

**OOP Concept:** Encapsulation
**Agentic Context:** Every agent system starts here. The LLM client is the engine room — the API key must never leak, rate limiting must be invisible to callers, and retries should be automatic.

#### Scenario
You are building the core LLM wrapper for a multi-agent pipeline. Three rules:
- The API key is never accessible from outside the class
- Callers just call `.complete(prompt)` — they don't manage rate limits
- Usage stats are exposed, but never the secret key

#### Scaffold

```python
import time

class RateLimitError(Exception):
    pass

class LLMClient:
    def __init__(self, api_key: str, model: str = "gpt-4", rpm_limit: int = 60):
        # TODO: Store api_key as a PRIVATE attribute (name-mangled with __)
        # TODO: Store model and rpm_limit as instance attributes
        # TODO: Initialize a private __call_count = 0
        # TODO: Initialize a private __window_start = time.time()
        pass

    def complete(self, prompt: str) -> str:
        # TODO: Check if we've exceeded rpm_limit in the last 60 seconds
        #       If exceeded, raise RateLimitError("Rate limit reached. Try again later.")
        #       If the 60-second window has passed, reset the counter and window.
        # TODO: Increment __call_count
        # TODO: Return self._make_request(prompt)
        pass

    def _make_request(self, prompt: str) -> str:
        """Simulates an LLM API call — do not modify."""
        return f"[{self.model}] Response to: '{prompt[:40]}...'"

    def get_usage_stats(self) -> dict:
        # TODO: Return a dict with keys: calls_made, rpm_remaining, model
        # IMPORTANT: Never include the api_key in the return value!
        pass

    def __repr__(self):
        # TODO: Return something like: LLMClient(model='gpt-4', key='sk-****1234')
        # Mask all but the last 4 characters of the key
        pass
```

#### Your Tasks
1. Store `api_key` with double underscore prefix (`__api_key`) so it cannot be accessed directly
2. Enforce the RPM limit — raise `RateLimitError` if `__call_count >= rpm_limit` within 60 seconds
3. Reset the window counter when 60 seconds pass
4. Implement `get_usage_stats()` — expose usage data but never the raw key
5. Implement `__repr__` masking the key

#### Expected Output

```python
client = LLMClient("sk-super-secret-abc1234", model="gpt-4", rpm_limit=60)
print(client.complete("What is chain-of-thought prompting?"))
print(client.complete("What are AI agents?"))
print(client.get_usage_stats())
print(client)
# print(client.__api_key)  # Should raise AttributeError
```

```
[gpt-4] Response to: 'What is chain-of-thought prompting?...'
[gpt-4] Response to: 'What are AI agents?...'
{'calls_made': 2, 'rpm_remaining': 58, 'model': 'gpt-4'}
LLMClient(model='gpt-4', key='sk-****1234')
```

#### Bonus Challenge
Add a `with_fallback(backup_client)` method that silently switches to a backup `LLMClient` instance when a `RateLimitError` is raised.

---

### Lab 2 — Inheritance: Agent Hierarchy

**OOP Concept:** Inheritance
**Agentic Context:** Real-world agent systems have specialized agents — researchers, coders, planners — that share common infrastructure (identity, memory, logging) but differ in behaviour.

#### Scenario
Build a `BaseAgent` with shared capabilities, then create two specializations: `ResearchAgent` (searches and summarizes information) and `CoderAgent` (writes and explains code). Both inherit memory management from the base class.

#### Scaffold

```python
class BaseAgent:
    def __init__(self, name: str, model: str):
        self.name = name
        self.model = model
        self.memory = []         # Shared memory store

    def remember(self, item: str):
        """Save something to agent memory."""
        self.memory.append(item)

    def recall(self) -> list:
        """Return everything in memory."""
        return self.memory

    def run(self, task: str) -> str:
        """Override this in each subclass."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement run()")

    def introduce(self) -> str:
        return f"I am {self.name}, a {self.__class__.__name__} powered by {self.model}."


class ResearchAgent(BaseAgent):
    def __init__(self, name: str, model: str, sources: list[str]):
        # TODO: Call parent __init__ using super()
        # TODO: Store sources as self.sources
        pass

    def run(self, task: str) -> str:
        # TODO: Simulate searching across self.sources
        # TODO: Save result string to memory using self.remember()
        # TODO: Return a formatted result string like:
        #   "[Research] Searched arxiv, wikipedia for: <task>\nSummary: <simulated summary>"
        pass


class CoderAgent(BaseAgent):
    def __init__(self, name: str, model: str, language: str = "python"):
        # TODO: Call parent __init__ using super()
        # TODO: Store language as self.language
        pass

    def run(self, task: str) -> str:
        # TODO: Simulate generating code for the task
        # TODO: Save result to memory using self.remember()
        # TODO: Return a formatted result like:
        #   "[Code·python] def solution():\n    # <task>\n    pass"
        pass
```

#### Your Tasks
1. Use `super().__init__(name, model)` in both subclasses — never repeat that logic
2. Each `run()` must call `self.remember(result)` to persist the output
3. Add a `ManagerAgent(BaseAgent)` that holds a list of child agents and delegates tasks

#### Expected Output

```python
researcher = ResearchAgent("Aria", "gpt-4", sources=["arxiv", "wikipedia"])
coder = CoderAgent("Dev", "claude-3", language="python")

print(researcher.introduce())
print(researcher.run("Chain-of-thought prompting"))
print(coder.run("Write a list chunker function"))
print(f"Researcher memory: {len(researcher.recall())} item(s)")
print(f"Coder memory: {len(coder.recall())} item(s)")
```

```
I am Aria, a ResearchAgent powered by gpt-4.
[Research] Searched arxiv, wikipedia for: Chain-of-thought prompting
Summary: Simulated findings on Chain-of-thought prompting

[Code·python] def solution():
    # Write a list chunker function
    pass

Researcher memory: 1 item(s)
Coder memory: 1 item(s)
```

#### Bonus Challenge
Build `ManagerAgent(BaseAgent)` that holds `[researcher, coder]` and routes tasks: if `"code"` is in the task it delegates to the coder, otherwise to the researcher.

---

### Lab 3 — Polymorphism: Tool Dispatcher

**OOP Concept:** Polymorphism
**Agentic Context:** Agents call tools. A well-designed dispatcher doesn't know or care which tool it's invoking — it just calls `.execute(query)`. New tools can be added without touching the dispatcher.

#### Scenario
Three tools, one interface: `WebSearchTool`, `CalculatorTool`, and `CodeRunnerTool`. A `dispatch()` function loops through whichever tools are active and calls `.execute(query)` on each — same call, different behaviour.

#### Scaffold

```python
class WebSearchTool:
    def name(self) -> str:
        return "web_search"

    def execute(self, query: str) -> str:
        # TODO: Return a simulated search result string
        # e.g., "[3 results found] Top result: '<query>' — Wikipedia"
        pass


class CalculatorTool:
    def name(self) -> str:
        return "calculator"

    def execute(self, query: str) -> str:
        # TODO: Try to evaluate the query as a math expression using eval()
        # If it succeeds, return "= <result>"
        # If it fails (ValueError, SyntaxError), return "Cannot evaluate: <query>"
        pass


class CodeRunnerTool:
    def name(self) -> str:
        return "code_runner"

    def execute(self, query: str) -> str:
        # TODO: Simulate executing a Python snippet
        # Return "Executed OK. Output: (simulated)" for any input
        pass


def dispatch(tools: list, query: str):
    """
    TODO: Loop through tools and call .execute(query) on each.
    Print: [tool_name] → <result>
    This function must NOT use isinstance() or check tool types.
    """
    pass
```

#### Your Tasks
1. Implement `.execute()` differently in each tool — that's polymorphism
2. Write `dispatch()` using only the shared `.name()` and `.execute()` interface
3. Confirm the same `dispatch()` works when you add a fourth tool without changing it

#### Expected Output

```python
tools = [WebSearchTool(), CalculatorTool(), CodeRunnerTool()]
dispatch(tools, "2 + 2 * 10")
print("---")
dispatch(tools, "latest LLM benchmarks")
```

```
[web_search] → [3 results found] Top result: '2 + 2 * 10' — Wikipedia
[calculator] → = 22
[code_runner] → Executed OK. Output: (simulated)
---
[web_search] → [3 results found] Top result: 'latest LLM benchmarks' — Wikipedia
[calculator] → Cannot evaluate: latest LLM benchmarks
[code_runner] → Executed OK. Output: (simulated)
```

#### Bonus Challenge
Build a `SmartDispatcher` that picks exactly one tool per query based on heuristics: if the query looks like math → calculator, if `"search"` or `"find"` is in the query → web_search, otherwise → code_runner.

---

### Lab 4 — Abstraction: Agent Tool Interface

**OOP Concept:** Abstraction
**Agentic Context:** When your agent system grows to 20+ tools, a consistent enforced contract is the only thing keeping it stable. Abstract base classes guarantee every tool is usable before it's ever tested.

#### Scenario
Define a `BaseTool` abstract class. Every tool in the ecosystem must implement `execute()` and `validate_input()`. The base class provides `safe_execute()` for free — handling validation and error catching in one place.

#### Scaffold

```python
from abc import ABC, abstractmethod

class BaseTool(ABC):

    @property
    @abstractmethod
    def description(self) -> str:
        """One-sentence description used by the LLM to pick this tool."""
        pass

    @abstractmethod
    def execute(self, input_data: str) -> dict:
        """
        Must return:
          {"success": True/False, "result": str, "tool": self.__class__.__name__}
        """
        pass

    @abstractmethod
    def validate_input(self, input_data: str) -> bool:
        """Return True if the input is usable, False otherwise."""
        pass

    def safe_execute(self, input_data: str) -> dict:
        """
        TODO: Shared execution wrapper — do NOT override this in subclasses.
        Steps:
          1. Call validate_input(). If False, return error dict.
          2. Call execute() inside a try/except.
          3. On exception, return error dict with the exception message.
        Always return a dict with keys: success, result, tool.
        """
        pass


class SerpAPITool(BaseTool):
    # TODO: Implement description property — "Searches the web for current information"
    # TODO: Implement execute() — simulate returning search results
    # TODO: Implement validate_input() — input must be non-empty and at least 3 chars
    pass


class PythonREPLTool(BaseTool):
    # TODO: Implement description property — "Runs Python code and returns output"
    # TODO: Implement execute() — simulate running a code snippet
    # TODO: Implement validate_input() — input must contain at least one newline or '='
    pass
```

#### Your Tasks
1. Complete `safe_execute()` in the base class — this is the shared error boundary
2. Fully implement both concrete tools including their `description` properties
3. Try instantiating `BaseTool()` directly — it should raise `TypeError`

#### Expected Output

```python
tools = [SerpAPITool(), PythonREPLTool()]

for tool in tools:
    print(f"\n{tool.__class__.__name__}: {tool.description}")
    print(tool.safe_execute("print('hello world')"))
    print(tool.safe_execute(""))    # invalid input
```

```
SerpAPITool: Searches the web for current information
{'success': True, 'result': "Search results for: print('hello world')", 'tool': 'SerpAPITool'}
{'success': False, 'result': 'Invalid input', 'tool': 'SerpAPITool'}

PythonREPLTool: Runs Python code and returns output
{'success': True, 'result': "Executed: print('hello world')", 'tool': 'PythonREPLTool'}
{'success': False, 'result': 'Invalid input', 'tool': 'PythonREPLTool'}
```

#### Bonus Challenge
Add an abstract `@property` called `max_input_length: int`. In `safe_execute()`, automatically truncate (or reject) inputs that exceed this limit before calling `validate_input()`.

---

## Advanced OOP Labs

---

### Lab 5 — Magic Methods: Agent Memory Store

**OOP Concept:** Magic / Dunder Methods
**Agentic Context:** Agent memory should feel native to Python. If you have to explain how to use it, the abstraction isn't good enough.

#### Scenario
Build a `MemoryStore` that an agent uses to store and retrieve facts across turns. It should behave like a dictionary (`memory["key"]`), support `in` checks, `len()`, `for` iteration, and print beautifully.

#### Scaffold

```python
from datetime import datetime

class MemoryStore:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self._store: dict = {}

    def __setitem__(self, key: str, value: str):
        # TODO: Store the value alongside an auto-generated timestamp
        # Store as: self._store[key] = {"value": value, "timestamp": datetime.now()}
        pass

    def __getitem__(self, key: str):
        # TODO: Return the value (not the whole dict entry)
        # Raise KeyError if not found, just like a real dict
        pass

    def __contains__(self, key: str) -> bool:
        # TODO: Support: "task_plan" in memory
        pass

    def __len__(self) -> int:
        # TODO: Support: len(memory)
        pass

    def __repr__(self) -> str:
        # TODO: Return: MemoryStore(agent='Aria', items=3)
        pass

    def __iter__(self):
        # TODO: Support: for key in memory
        pass

    def __delitem__(self, key: str):
        # TODO: Support: del memory["key"]
        pass

    def __add__(self, other: "MemoryStore") -> "MemoryStore":
        # TODO: Merge two MemoryStores — return a NEW MemoryStore
        # The new store's agent_name = f"{self.agent_name}+{other.agent_name}"
        # Later keys overwrite earlier ones on conflict
        pass

    def when(self, key: str) -> str:
        """Return the timestamp for a stored key as a readable string."""
        if key not in self._store:
            raise KeyError(key)
        return self._store[key]["timestamp"].strftime("%H:%M:%S")
```

#### Your Tasks
1. Implement all dunder methods above
2. `__setitem__` must auto-timestamp every entry
3. `__add__` must return a new merged `MemoryStore` without mutating either original

#### Expected Output

```python
mem = MemoryStore("Aria")
mem["task_plan"] = "Research → Summarize → Output"
mem["user_name"] = "Alice"
mem["context"]   = "AI safety research"

print(mem)                          # MemoryStore(agent='Aria', items=3)
print(len(mem))                     # 3
print("task_plan" in mem)           # True
print("budget" in mem)              # False
print(mem["user_name"])             # Alice

for key in mem:
    print(f"  {key}: {mem[key]}")

mem2 = MemoryStore("Dev")
mem2["context"] = "Coding tasks"
merged = mem + mem2
print(merged)                       # MemoryStore(agent='Aria+Dev', items=3)
print(merged["context"])            # Coding tasks  (mem2 wins the conflict)
```

#### Bonus Challenge
Add `__or__` as an alias for merge (so `mem | mem2` works like `mem + mem2`), and `keys()`, `values()`, `items()` methods that mirror dict behaviour.

---

### Lab 6 — Properties: Token Budget Manager

**OOP Concept:** Properties & Descriptors
**Agentic Context:** LLM context windows are finite. Agents that don't track token usage will silently fail mid-task. A property-driven budget makes it impossible to exceed limits accidentally.

#### Scenario
Build a `TokenBudget` that tracks input and output tokens across multiple agent turns. Computed properties expose real-time stats; validated setters prevent bad data from ever entering the system.

#### Scaffold

```python
class TokenBudgetExceededError(Exception):
    pass

class TokenBudget:
    WARN_THRESHOLD = 0.80   # 80% used → yellow
    DANGER_THRESHOLD = 0.95 # 95% used → red

    def __init__(self, total_limit: int):
        self._total_limit = total_limit
        self._input_tokens = 0
        self._output_tokens = 0

    # --- Computed properties ---

    @property
    def used(self) -> int:
        # TODO: Total tokens consumed (input + output)
        pass

    @property
    def remaining(self) -> int:
        # TODO: Tokens left in the budget
        pass

    @property
    def usage_pct(self) -> float:
        # TODO: Percentage consumed as 0.0–100.0
        pass

    @property
    def status(self) -> str:
        # TODO: Return "green", "yellow", or "red" based on WARN/DANGER thresholds
        pass

    # --- Validated setters ---

    @property
    def input_tokens(self) -> int:
        return self._input_tokens

    @input_tokens.setter
    def input_tokens(self, value: int):
        # TODO: Validate value >= 0
        # TODO: If setting this would push total over limit, raise TokenBudgetExceededError
        pass

    @property
    def output_tokens(self) -> int:
        return self._output_tokens

    @output_tokens.setter
    def output_tokens(self, value: int):
        # TODO: Same validation as input_tokens setter
        pass

    # --- Helpers ---

    def add_turn(self, input_t: int, output_t: int):
        """Record tokens for one agent turn."""
        # TODO: Accumulate to _input_tokens and _output_tokens safely
        pass

    def is_safe(self, margin: float = 0.10) -> bool:
        """True if usage is below (1 - margin) of total limit."""
        # TODO: Implement
        pass

    def __repr__(self):
        return (f"TokenBudget(used={self.used}/{self._total_limit}, "
                f"{self.usage_pct:.1f}%, status={self.status})")
```

#### Your Tasks
1. Implement all four computed properties
2. Validated setters must raise `ValueError` for negative values and `TokenBudgetExceededError` if the total would be exceeded
3. `add_turn()` should use the setters (so validation runs automatically)

#### Expected Output

```python
budget = TokenBudget(total_limit=8000)
budget.add_turn(512, 256)
budget.add_turn(1024, 512)

print(budget)
print(f"Remaining: {budget.remaining}")
print(f"Safe to continue: {budget.is_safe()}")
print(f"Status: {budget.status}")

# Push to danger zone
budget.add_turn(5000, 500)
print(budget)
```

```
TokenBudget(used=2304/8000, 28.8%, status=green)
Remaining: 5696
Safe to continue: True
Status: green
TokenBudget(used=7804/8000, 97.6%, status=red)
```

#### Bonus Challenge
Add a `@contextmanager`-style `reserve(n_tokens)` method that temporarily earmarks tokens, checks if the reservation fits, and releases them on exit (useful for planning ahead before a long generation).

---

### Lab 7 — Metaclasses: Auto-Registering Tool Catalog

**OOP Concept:** Metaclasses
**Agentic Context:** As your agent system grows, manually registering tools in a central registry becomes a maintenance burden. Metaclasses let tools register themselves the moment they are defined — zero glue code.

#### Scenario
Build a `ToolMeta` metaclass so that every class inheriting from `RegisteredTool` automatically appears in a global tool registry. The agent can query the registry to discover available tools and pick the right one.

#### Scaffold

```python
class ToolMeta(type):
    registry: dict[str, type] = {}

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)

        # TODO: Skip registration for the base class itself (name == "RegisteredTool")
        # TODO: Use cls.tool_name if defined, else fall back to the class name lowercased
        # TODO: Add to mcs.registry: mcs.registry[tool_key] = cls
        # TODO: Also store the class docstring as metadata if present
        #        Store in: mcs.registry_meta[tool_key] = {"description": cls.__doc__}

        return cls


class RegisteredTool(metaclass=ToolMeta):
    tool_name: str = None   # Subclasses should set this

    def execute(self, query: str) -> str:
        raise NotImplementedError


# Defining these classes auto-registers them — no extra code needed:

class WebSearch(RegisteredTool):
    """Searches the web for current information."""
    tool_name = "web_search"

    def execute(self, query: str) -> str:
        return f"[Web] Results for: {query}"


class Calculator(RegisteredTool):
    """Evaluates mathematical expressions."""
    tool_name = "calculator"

    def execute(self, query: str) -> str:
        try:
            return f"= {eval(query)}"
        except Exception:
            return "Cannot evaluate"


class CodeRunner(RegisteredTool):
    """Executes Python code snippets in a sandbox."""
    tool_name = "code_runner"

    def execute(self, query: str) -> str:
        return f"[Run] Executed: {query}"
```

#### Your Tasks
1. Complete `ToolMeta.__new__()` — register every non-base subclass automatically
2. Skip the `RegisteredTool` base class itself from registering
3. Store the docstring as a description alongside each registration
4. Implement `find_tool(query: str)` that picks a tool by fuzzy-matching its description

#### Expected Output

```python
print(list(ToolMeta.registry.keys()))
# ['web_search', 'calculator', 'code_runner']

tool_cls = ToolMeta.registry["web_search"]
instance = tool_cls()
print(instance.execute("latest AI research"))

# Tool descriptions for LLM tool-use prompting:
for name, cls in ToolMeta.registry.items():
    print(f"  {name}: {cls.__doc__}")
```

```
['web_search', 'calculator', 'code_runner']
[Web] Results for: latest AI research
  web_search: Searches the web for current information.
  calculator: Evaluates mathematical expressions.
  code_runner: Executes Python code snippets in a sandbox.
```

#### Bonus Challenge
Add a `ToolMeta.for_llm()` class method that returns a formatted JSON-like string of all registered tools — ready to inject into an LLM system prompt as the "Available tools:" section.

---

### Lab 8 — MRO: Multi-Modal Agent

**OOP Concept:** Multiple Inheritance & Method Resolution Order
**Agentic Context:** Frontier agents handle text, images, audio, and structured data. Understanding MRO lets you compose capabilities safely — knowing exactly which method runs and why.

#### Scenario
Build three capability classes (`TextAgent`, `VisionAgent`, `AudioAgent`) and combine them into a `MultiModalAgent`. First observe which `process()` Python calls automatically (and why). Then build a `route()` method that dispatches to each modality intentionally.

#### Scaffold

```python
class TextAgent:
    def process(self, data: str) -> str:
        return f"[Text] Analysing text: '{data}'"

    def capabilities(self) -> list[str]:
        return ["text"]


class VisionAgent:
    def process(self, data: str) -> str:
        return f"[Vision] Analysing image: '{data}'"

    def capabilities(self) -> list[str]:
        return ["image", "video"]


class AudioAgent:
    def process(self, data: str) -> str:
        return f"[Audio] Transcribing audio: '{data}'"

    def capabilities(self) -> list[str]:
        return ["audio", "speech"]


class MultiModalAgent(TextAgent, VisionAgent, AudioAgent):
    def __init__(self, name: str):
        self.name = name

    def route(self, modality: str, data: str) -> str:
        """
        TODO: Dispatch to the correct parent's process() based on modality.
        Accepted modalities: "text", "image", "audio"
        Use explicit parent class calls, not just self.process()
        Raise ValueError for unknown modalities.
        """
        pass

    def process_all(self, data: str) -> list[str]:
        """
        TODO: Call process() from ALL three parents and return results as a list.
        Hint: call TextAgent.process(self, data), VisionAgent.process(self, data), etc.
        """
        pass
```

#### Your Tasks
1. Print `MultiModalAgent.__mro__` and write a one-sentence explanation of the order
2. Call `agent.process("hello.wav")` and explain which class handles it and why
3. Implement `route(modality, data)` using explicit parent class calls
4. Implement `process_all(data)` that collects results from all three parents

#### Expected Output

```python
agent = MultiModalAgent("Omni")

# Part 1: Understand MRO
print(MultiModalAgent.__mro__)
print(agent.process("test_input"))    # Which parent handles this?

# Part 2: Intentional routing
print(agent.route("text", "Hello world"))
print(agent.route("image", "photo.jpg"))
print(agent.route("audio", "speech.mp3"))

# Part 3: All modalities
for result in agent.process_all("sensor_data"):
    print(result)
```

```
(<class '__main__.MultiModalAgent'>, <class '__main__.TextAgent'>, <class '__main__.VisionAgent'>, <class '__main__.AudioAgent'>, <class 'object'>)
[Text] Analysing text: 'test_input'   ← TextAgent wins (leftmost in MRO)

[Text] Analysing text: 'Hello world'
[Vision] Analysing image: 'photo.jpg'
[Audio] Transcribing audio: 'speech.mp3'

[Text] Analysing text: 'sensor_data'
[Vision] Analysing image: 'sensor_data'
[Audio] Transcribing audio: 'sensor_data'
```

#### Bonus Challenge
Add auto-detection: `agent.auto_route("photo.jpg")` → detects `.jpg` extension and routes to VisionAgent; `.mp3` → AudioAgent; everything else → TextAgent.

---

### Lab 9 — Dataclasses: Agent Message Schema

**OOP Concept:** Dataclasses
**Agentic Context:** Agents communicate through structured messages. A well-defined schema prevents entire classes of bugs — wrong types, missing fields, mutable results that shouldn't be changed.

#### Scenario
Define the message protocol for an agentic pipeline: `Message`, `ToolCall`, `ToolResult`, and `AgentResponse`. These pass between agent components on every turn.

#### Scaffold

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid

@dataclass
class Message:
    """A single message in the agent conversation."""
    role: str                         # "system", "user", "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    token_count: int = 0

    def __post_init__(self):
        # TODO: Auto-calculate token_count as an approximation:
        #       len(self.content.split()) if token_count was not set
        #       Only override if token_count == 0
        pass


@dataclass
class ToolCall:
    """A request from the agent to invoke a tool."""
    tool_name: str
    arguments: dict
    call_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_prompt_string(self) -> str:
        # TODO: Return a formatted string like:
        # "Tool: web_search | Args: {'query': 'AI agents'} | ID: a1b2c3d4"
        pass


@dataclass(frozen=True)            # Immutable — results must not be edited
class ToolResult:
    """The outcome of a tool call."""
    call_id: str
    success: bool
    output: str
    error: Optional[str] = None

    def to_message(self) -> "Message":
        # TODO: Convert this result to a Message with role="tool"
        # Content: the output if success, else f"Error: {self.error}"
        pass


@dataclass
class AgentResponse:
    """Everything the agent produces in one turn."""
    messages: list[Message] = field(default_factory=list)
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_results: list[ToolResult] = field(default_factory=list)
    finished: bool = False

    @property
    def total_tokens(self) -> int:
        # TODO: Sum token_count across all messages
        pass

    def add_message(self, role: str, content: str):
        # TODO: Create a Message and append to self.messages
        pass
```

#### Your Tasks
1. Use `field(default_factory=...)` for all mutable defaults — never a bare `[]` or `{}`
2. Implement `__post_init__` in `Message` to auto-estimate `token_count`
3. `ToolResult` must be frozen — confirm that mutating it raises `FrozenInstanceError`
4. Implement all helper methods

#### Expected Output

```python
# Build a conversation turn
response = AgentResponse()
response.add_message("user", "Find recent papers on multi-agent systems")
response.add_message("assistant", "I'll search for that now.")

call = ToolCall(tool_name="web_search", arguments={"query": "multi-agent systems 2024"})
print(call.to_prompt_string())

result = ToolResult(call_id=call.call_id, success=True, output="Found 15 papers.")
response.tool_results.append(result)

print(f"Total tokens: {response.total_tokens}")
print(result.to_message())
```

```
Tool: web_search | Args: {'query': 'multi-agent systems 2024'} | ID: a1b2c3d4
Total tokens: 11
Message(role='tool', content='Found 15 papers.', timestamp=..., token_count=3)
```

#### Bonus Challenge
Add a `Conversation` dataclass that holds a list of `AgentResponse` objects and a `summary()` method returning total turns, total tokens, and number of tool calls across the whole session.

---

### Lab 10 — Mixins: Agent Capability Packs

**OOP Concept:** Mixins
**Agentic Context:** Production agents need logging, automatic retries, and observability. Mixins let you bolt on these cross-cutting concerns without touching the agent's core logic — and any agent can opt in.

#### Scenario
Build three standalone mixins and compose them into a `ProductionAgent`. Each mixin is independently useful and can be added to any future agent class.

#### Scaffold

```python
import time
import functools

class LoggingMixin:
    """Adds structured logging to any agent."""

    def log(self, level: str, msg: str):
        # TODO: Print: [LEVEL] AgentName: message
        # Use self.name if it exists, else "Unknown"
        pass

    def logged(self, fn):
        """Decorator: logs before and after any method call."""
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            # TODO: Log "Calling: <fn name>" before
            # TODO: Call fn, log "Done: <fn name>" after
            # TODO: If exception, log it at ERROR level and re-raise
            pass
        return wrapper


class RetryMixin:
    """Adds automatic retry logic to any agent."""

    def with_retry(self, fn, max_attempts: int = 3, delay: float = 0.5):
        """
        TODO: Call fn(). On exception, wait `delay` seconds and retry.
        After max_attempts failures, raise the last exception.
        Log each retry attempt (use self.log() if available).
        """
        pass


class ObservabilityMixin:
    """Tracks call metrics for any agent."""

    def __init__(self):
        self._metrics = {
            "calls": 0,
            "errors": 0,
            "total_latency_ms": 0.0
        }

    def track(self, fn, *args, **kwargs):
        """
        TODO: Call fn(*args, **kwargs), measure wall-clock latency.
        Increment self._metrics["calls"].
        Accumulate latency in self._metrics["total_latency_ms"].
        On exception, increment self._metrics["errors"] then re-raise.
        """
        pass

    @property
    def avg_latency_ms(self) -> float:
        calls = self._metrics["calls"]
        return self._metrics["total_latency_ms"] / calls if calls else 0.0

    def report(self) -> dict:
        return {**self._metrics, "avg_latency_ms": round(self.avg_latency_ms, 2)}


class ProductionAgent(LoggingMixin, RetryMixin, ObservabilityMixin):
    def __init__(self, name: str):
        self.name = name
        ObservabilityMixin.__init__(self)

    def run(self, task: str) -> str:
        self.log("INFO", f"Starting: {task}")
        result = f"Completed: {task}"
        self.log("INFO", "Done")
        return result
```

#### Your Tasks
1. Implement all three mixins fully
2. `ProductionAgent.run()` should call `self.track(self._run_task, task)` internally — wire it up
3. Demonstrate `with_retry()` by making a flaky function fail twice then succeed

#### Expected Output

```python
agent = ProductionAgent("Atlas")
result = agent.run("Summarise Q3 earnings report")
print(result)
print(agent.report())

# Retry demo
attempt = [0]
def flaky():
    attempt[0] += 1
    if attempt[0] < 3:
        raise ConnectionError("API timeout")
    return "Success on attempt 3"

print(agent.with_retry(flaky, max_attempts=3, delay=0.1))
```

```
[INFO] Atlas: Starting: Summarise Q3 earnings report
[INFO] Atlas: Done
Completed: Summarise Q3 earnings report
{'calls': 1, 'errors': 0, 'total_latency_ms': 0.5, 'avg_latency_ms': 0.5}

[WARN] Atlas: Attempt 1 failed: API timeout. Retrying...
[WARN] Atlas: Attempt 2 failed: API timeout. Retrying...
Success on attempt 3
```

#### Bonus Challenge
Build a `CachingMixin` that memoises agent responses by task string. If an identical task has been run before, return the cached result immediately and mark it as `(cached)` in the log.

---

### Lab 11 — Context Managers: Sandboxed Code Execution

**OOP Concept:** Context Managers
**Agentic Context:** Code-executing agents are powerful and dangerous. A context manager guarantees that resources are always cleaned up, output is always captured, and errors never crash the outer process.

#### Scenario
Build a `CodeSandbox` context manager that wraps `exec()`. It captures stdout, measures execution time, enforces a character limit on output, and handles exceptions gracefully — regardless of what the agent-generated code does.

#### Scaffold

```python
import time
import io
import sys

class ExecutionError(Exception):
    pass

class CodeSandbox:
    def __init__(self, timeout_sec: float = 5.0, max_output_chars: int = 2000):
        self.timeout_sec = timeout_sec
        self.max_output_chars = max_output_chars
        self.execution_time_ms = 0.0
        self.captured_output = ""
        self.error = None
        self._start_time = None
        self._stdout_buffer = None
        self._original_stdout = None

    def __enter__(self):
        # TODO: Record self._start_time
        # TODO: Redirect sys.stdout to a StringIO buffer (save original to restore later)
        # TODO: Return self (so caller can use: with CodeSandbox() as sb:)
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        # TODO: Restore sys.stdout from self._original_stdout
        # TODO: Capture self._stdout_buffer.getvalue() into self.captured_output
        # TODO: Truncate captured_output if longer than max_output_chars
        # TODO: Calculate self.execution_time_ms from _start_time to now
        # TODO: If an exception occurred (exc_type is not None), store it in self.error
        # TODO: Return True to suppress the exception (the sandbox swallows errors)
        pass

    @property
    def succeeded(self) -> bool:
        return self.error is None

    def result(self) -> dict:
        return {
            "output": self.captured_output,
            "exec_time_ms": round(self.execution_time_ms, 2),
            "truncated": len(self.captured_output) >= self.max_output_chars,
            "error": str(self.error) if self.error else None,
            "success": self.succeeded
        }
```

#### Your Tasks
1. Implement `__enter__` and `__exit__` fully
2. `__exit__` must return `True` — exceptions inside the `with` block must not crash the caller
3. Test with: valid code, code that raises an exception, and code that prints too much

#### Expected Output

```python
# Valid code
with CodeSandbox() as sb:
    exec("for i in range(5):\n    print(f'Step {i}')")
print(sb.result())

# Code with an error
with CodeSandbox() as sb:
    exec("result = 1 / 0")
print(sb.result())

# Truncation
with CodeSandbox(max_output_chars=20) as sb:
    exec("print('A' * 100)")
print(sb.result())
```

```
{'output': 'Step 0\nStep 1\nStep 2\nStep 3\nStep 4\n', 'exec_time_ms': 0.1, 'truncated': False, 'error': None, 'success': True}
{'output': '', 'exec_time_ms': 0.05, 'truncated': False, 'error': 'division by zero', 'success': False}
{'output': 'AAAAAAAAAAAAAAAAAAAA', 'exec_time_ms': 0.05, 'truncated': True, 'error': None, 'success': True}
```

#### Bonus Challenge
Use `threading.Timer` to enforce the `timeout_sec` limit — after the timeout, set `self.error = TimeoutError(...)` and terminate the thread running the `exec()`. This is a real-world requirement for safe code execution agents.

---

### Lab 12 — `__slots__`: High-Throughput Message Pipeline

**OOP Concept:** `__slots__`
**Agentic Context:** Agent pipelines that process thousands of messages per second — RAG chunkers, streaming token processors, log pipelines — cannot afford per-instance dictionary overhead. `__slots__` cuts memory usage by 3–5× at scale.

#### Scenario
You're building the message queue layer for a high-throughput agentic pipeline. A standard `Message` class is too heavy. Build a `SlottedMessage`, benchmark both, and implement a serializer since `__dict__` won't be available.

#### Scaffold

```python
import sys
import time

class Message:
    """Standard message — each instance carries a full __dict__."""
    def __init__(self, role: str, content: str, tokens: int, turn: int):
        self.role = role
        self.content = content
        self.tokens = tokens
        self.turn = turn


class SlottedMessage:
    """Memory-efficient message using __slots__."""
    __slots__ = ['role', 'content', 'tokens', 'turn']

    def __init__(self, role: str, content: str, tokens: int, turn: int):
        # TODO: Same as Message — identical interface, smaller footprint
        pass

    def to_dict(self) -> dict:
        # TODO: Since __dict__ doesn't exist, manually build the dict
        # Return: {"role": ..., "content": ..., "tokens": ..., "turn": ...}
        pass

    def __repr__(self):
        return f"SlottedMessage(role={self.role!r}, tokens={self.tokens})"


def measure_size(obj) -> int:
    """Return approximate memory size of one instance in bytes."""
    size = sys.getsizeof(obj)
    if hasattr(obj, '__dict__'):
        size += sys.getsizeof(obj.__dict__)
    return size


def benchmark(cls, n: int = 100_000) -> None:
    # TODO: Create n instances of cls
    # TODO: Measure wall-clock time with time.perf_counter()
    # TODO: Measure per-instance size using measure_size() on instances[0]
    # TODO: Print a formatted comparison row
    pass
```

#### Your Tasks
1. Implement `SlottedMessage` with `__slots__` and identical `__init__` signature
2. Implement `to_dict()` — required because `__dict__` won't exist
3. Implement `benchmark()` and run it for both classes
4. Confirm that assigning a new attribute to `SlottedMessage` raises `AttributeError`

#### Expected Output

```python
benchmark(Message,       100_000)
benchmark(SlottedMessage, 100_000)

s = SlottedMessage("user", "Hello agent", 3, 1)
print(s.to_dict())
print(s)

try:
    s.new_field = "oops"
except AttributeError as e:
    print(f"Slots enforce a fixed schema: {e}")
```

```
        Message | 100,000 instances | 61.3ms | 232B/instance
 SlottedMessage | 100,000 instances | 42.1ms |  72B/instance

{'role': 'user', 'content': 'Hello agent', 'tokens': 3, 'turn': 1}
SlottedMessage(role='user', tokens=3)
Slots enforce a fixed schema: 'SlottedMessage' object has no attribute 'new_field'
```

#### Bonus Challenge
Build a `MessageBatch` class using `__slots__` that holds a fixed-size array of `SlottedMessage` objects (using a plain `list` as the one allowed slot). Add `__iter__`, `__len__`, and `to_jsonl()` for exporting to JSON Lines format.

---

## Capstone: Mini Agentic System

Wire all 12 concepts into a single working loop.

```
LLMClient         (Lab 1)  — secure LLM access
BaseAgent +
  CoderAgent      (Lab 2)  — specialised agent type
BaseTool /
  polymorphic     (Labs 3,4) — pluggable tools
MemoryStore       (Lab 5)  — agent memory between turns
TokenBudget       (Lab 6)  — context window tracking
ToolMeta          (Lab 7)  — auto-discovered tool registry
Message / ToolCall(Lab 9)  — structured communication
LoggingMixin +
  RetryMixin      (Lab 10) — production reliability
CodeSandbox       (Lab 11) — safe code execution
SlottedMessage    (Lab 12) — efficient pipeline messages
```

**Goal:** Implement `run_agent_loop(task: str, max_turns: int = 3)` that:
1. Initialises an `LLMClient`, `MemoryStore`, and `TokenBudget`
2. On each turn, selects a tool from `ToolMeta.registry`, calls it inside a `CodeSandbox`, and saves the result to `MemoryStore`
3. Tracks tokens with `TokenBudget` and stops early if `status == "red"`
4. Logs every action using `LoggingMixin`
5. Returns a final `AgentResponse` dataclass with all messages and tool results

**Stretch goal:** Add `RetryMixin` to the tool calls and a `MultiModalAgent` (Lab 8) that routes different input types before feeding into the loop.
