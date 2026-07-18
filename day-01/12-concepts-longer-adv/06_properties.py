"""
╔══════════════════════════════════════════════════════════════════════╗
║  CONCEPT 6 — PROPERTIES                                             ║
║  File    : 06_properties.py                                         ║
║  Run     : python 06_properties.py                                  ║
╠══════════════════════════════════════════════════════════════════════╣
║  WHAT IS IT?                                                        ║
║  @property turns a method into an attribute that computes its       ║
║  value on access. Adding a setter lets you validate before storing. ║
║                                                                     ║
║  THREE DECORATORS:                                                  ║
║    @property               → getter (read access)                   ║
║    @name.setter            → setter (write access + validation)     ║
║    @name.deleter           → deleter (delete access)                ║
║                                                                     ║
║  WHY USE @property?                                                 ║
║    1. Computed values look like attributes (no parentheses needed)  ║
║    2. Validation runs automatically on every assignment             ║
║    3. You can make attributes read-only by omitting the setter      ║
║    4. Can change internal implementation without breaking callers   ║
║                                                                     ║
║  AGENTIC AI USE CASE: Token Budget Manager                          ║
║  Track LLM token usage. Computed stats (usage_pct, remaining,       ║
║  status). Validated setters prevent budget corruption.              ║
╚══════════════════════════════════════════════════════════════════════╝
"""


# ─────────────────────────────────────────────────────────────────────
#  PART 1 — THE PROBLEM: Unvalidated raw attributes
# ─────────────────────────────────────────────────────────────────────

print("=" * 60)
print("PART 1 — THE PROBLEM (no validation, no computed values)")
print("=" * 60)

class BadTokenBudget:
    """Token budget with raw attributes — easy to corrupt."""

    def __init__(self, total: int):
        self.total   = total
        self.used    = 0          # ← EXPOSED: can be set to anything

    def add(self, tokens: int):
        self.used += tokens


bad = BadTokenBudget(8000)
bad.add(3000)

print(f"used = {bad.used}")

# Problems:
print("\nProblem 1: Anyone can corrupt the budget:")
bad.used = -5000             # Nonsensical negative value!
print(f"  bad.used = {bad.used}  ← nonsensical")

print("\nProblem 2: Computed stats require method calls (verbose):")
bad.used = 4000
print(f"  Usage %: {bad.used / bad.total * 100:.1f}%  ← must compute manually every time")
print(f"  Remaining: {bad.total - bad.used}           ← must compute manually every time")
print()


# ─────────────────────────────────────────────────────────────────────
#  PART 2 — THE SOLUTION: Properties with validation
# ─────────────────────────────────────────────────────────────────────

print("=" * 60)
print("PART 2 — THE SOLUTION (Properties)")
print("=" * 60)


class TokenBudgetError(Exception):
    """Raised when token budget operations are invalid."""
    pass


class TokenBudget:
    """
    Token budget with computed properties and validated setters.

    PRIVATE STORAGE:
        _total_limit      → the maximum token allowance
        _input_tokens     → tokens used in prompts (inputs)
        _output_tokens    → tokens used in responses (outputs)

    READ-ONLY COMPUTED PROPERTIES (no setter — cannot be set directly):
        used              → _input_tokens + _output_tokens
        remaining         → _total_limit - used
        usage_pct         → percentage consumed (0.0 to 100.0)
        status            → 'green' / 'yellow' / 'red'
        status_bar        → visual ASCII progress bar

    VALIDATED PROPERTIES (setter runs validation on every assignment):
        input_tokens      → cannot go negative or exceed budget
        output_tokens     → same rule
    """

    # Class-level thresholds — shared across all instances
    WARN_THRESHOLD   = 0.80   # 80% used → status turns yellow
    DANGER_THRESHOLD = 0.95   # 95% used → status turns red

    def __init__(self, total_limit: int, session_name: str = "session"):
        if total_limit <= 0:
            raise ValueError("total_limit must be a positive integer.")

        # Store with _single_underscore — do not access directly from outside
        self._total_limit   = total_limit
        self._input_tokens  = 0
        self._output_tokens = 0
        self._turn_history  = []
        self.session_name   = session_name

    # ══════════════════════════════════════════════════════════════════
    #  COMPUTED PROPERTIES (read-only — no setter defined)
    # ══════════════════════════════════════════════════════════════════

    @property
    def used(self) -> int:
        """
        Total tokens consumed so far.

        Callers write:  budget.used         (not budget.used())
        Python calls:   TokenBudget.used.fget(budget)
        """
        return self._input_tokens + self._output_tokens

    @property
    def remaining(self) -> int:
        """Tokens still available in the budget."""
        return self._total_limit - self.used

    @property
    def usage_pct(self) -> float:
        """
        Percentage of budget consumed. Range: 0.0 to 100.0.

        Example: 4000 used of 8000 total → 50.0
        """
        return (self.used / self._total_limit) * 100.0

    @property
    def status(self) -> str:
        """
        Traffic-light status string based on usage ratio.

        green  → below 80%   — safe to continue
        yellow → 80% to 94%  — plan to wrap up soon
        red    → 95%+        — stop immediately
        """
        ratio = self.used / self._total_limit
        if ratio >= self.DANGER_THRESHOLD:
            return "red"
        elif ratio >= self.WARN_THRESHOLD:
            return "yellow"
        else:
            return "green"

    @property
    def status_bar(self) -> str:
        """
        ASCII progress bar — 20 segments, each = 5%.

        Example at 55% used:
            [###########.........] 55.0% (GREEN)
        """
        filled   = int(self.usage_pct / 5)
        empty    = 20 - filled
        label    = self.status.upper()
        return f"[{'#' * filled}{'.' * empty}] {self.usage_pct:.1f}% ({label})"

    # ══════════════════════════════════════════════════════════════════
    #  VALIDATED PROPERTIES (getter + setter pair)
    # ══════════════════════════════════════════════════════════════════

    @property
    def input_tokens(self) -> int:
        """Current number of input tokens consumed."""
        return self._input_tokens

    @input_tokens.setter
    def input_tokens(self, value: int):
        """
        SETTER — runs every time you write: budget.input_tokens = X

        Validation rules:
          1. Must be a non-negative integer
          2. input_tokens + output_tokens must not exceed total_limit

        If either rule fails, raises an exception BEFORE the value is stored.
        The stored value is never corrupted.
        """
        if not isinstance(value, int) or value < 0:
            raise ValueError(
                f"input_tokens must be a non-negative integer, got {value!r}"
            )
        if (value + self._output_tokens) > self._total_limit:
            raise TokenBudgetError(
                f"Cannot set input_tokens={value:,}. "
                f"Would exceed total_limit={self._total_limit:,}. "
                f"Current output_tokens={self._output_tokens:,}."
            )
        self._input_tokens = value

    @property
    def output_tokens(self) -> int:
        """Current number of output tokens consumed."""
        return self._output_tokens

    @output_tokens.setter
    def output_tokens(self, value: int):
        """SETTER — validates and stores output token count."""
        if not isinstance(value, int) or value < 0:
            raise ValueError(
                f"output_tokens must be a non-negative integer, got {value!r}"
            )
        if (self._input_tokens + value) > self._total_limit:
            raise TokenBudgetError(
                f"Cannot set output_tokens={value:,}. "
                f"Would exceed total_limit={self._total_limit:,}. "
                f"Current input_tokens={self._input_tokens:,}."
            )
        self._output_tokens = value

    # ══════════════════════════════════════════════════════════════════
    #  HELPERS
    # ══════════════════════════════════════════════════════════════════

    def add_turn(self, input_t: int, output_t: int, label: str = ""):
        """
        Add tokens for one complete agent turn.
        Internally uses the validated setters — validation runs automatically.
        """
        self.input_tokens  = self._input_tokens  + input_t
        self.output_tokens = self._output_tokens + output_t
        self._turn_history.append({
            "turn"  : len(self._turn_history) + 1,
            "label" : label,
            "input" : input_t,
            "output": output_t,
            "total" : self.used,
            "status": self.status,
        })

    def is_safe(self, margin: float = 0.10) -> bool:
        """True if usage is below (1 - margin) × total_limit."""
        return self.used < self._total_limit * (1 - margin)

    def turn_history(self) -> list:
        return self._turn_history

    def summary(self) -> str:
        return "\n".join([
            f"TokenBudget [{self.session_name}]",
            f"  {self.status_bar}",
            f"  Used       : {self.used:,} / {self._total_limit:,} tokens",
            f"  Input      : {self._input_tokens:,}",
            f"  Output     : {self._output_tokens:,}",
            f"  Remaining  : {self.remaining:,}",
            f"  Turns      : {len(self._turn_history)}",
            f"  Status     : {self.status.upper()}",
        ])

    def __repr__(self) -> str:
        return (
            f"TokenBudget("
            f"used={self.used:,}/{self._total_limit:,}, "
            f"{self.usage_pct:.1f}%, "
            f"{self.status})"
        )


# ─────────────────────────────────────────────────────────────────────
#  DEMO
# ─────────────────────────────────────────────────────────────────────

print("\n── Creating a TokenBudget ──────────────────────────────────")
budget = TokenBudget(total_limit=8000, session_name="research-session-42")

print("\n── Simulating 4 agent turns ────────────────────────────────")
budget.add_turn(512,  256, "System prompt + initial query")
budget.add_turn(1024, 512, "Tool call and result summarisation")
budget.add_turn(800,  400, "Follow-up web search")
budget.add_turn(600,  300, "Draft final answer")

print(budget.summary())

print("\n── Computed properties — no parentheses needed ─────────────")
print(f"budget.used       = {budget.used:,}")       # property, not method
print(f"budget.remaining  = {budget.remaining:,}")  # property, not method
print(f"budget.usage_pct  = {budget.usage_pct:.1f}%")
print(f"budget.status     = {budget.status}")
print(f"budget.status_bar = {budget.status_bar}")
print(f"budget.is_safe()  = {budget.is_safe()}")

print("\n── Attempting to SET a computed property (should fail) ──────")
try:
    budget.used = 999      # 'used' has no setter → read-only!
except AttributeError as e:
    print(f"  AttributeError: {e}")
    print("  → 'used' is read-only because no setter is defined.")

print("\n── Validated setter blocks negative value ───────────────────")
try:
    budget.input_tokens = -500
except ValueError as e:
    print(f"  ValueError: {e}")

print("\n── Validated setter blocks budget overflow ──────────────────")
try:
    budget.add_turn(5000, 3000, "Huge request")
except TokenBudgetError as e:
    print(f"  TokenBudgetError: {e}")

print(f"\n  Budget after failed add: {budget}")  # unchanged — guard worked

print("\n── Push into yellow then red zone ──────────────────────────")
budget.add_turn(2000, 1000, "Analysis")
print(f"  After analysis turn: {budget.status_bar}")

budget2 = TokenBudget(1000, "tiny-budget")
budget2.add_turn(960, 0, "Big call")
print(f"  Tiny budget near limit: {budget2.status_bar}")

print("\n── Turn history ─────────────────────────────────────────────")
print(f"Turns recorded: {len(budget.turn_history())}")
for t in budget.turn_history():
    print(f"  Turn {t['turn']}: +{t['input']} in / +{t['output']} out "
          f"→ total={t['total']:,}  status={t['status']}")

print("\n── Key takeaways ────────────────────────────────────────────")
print("""
  @property               → makes method accessible as attribute (no ())
  @name.setter            → validates BEFORE storing the value
  No setter defined       → attribute is read-only (AttributeError on write)
  Computed properties     → always reflect current state, never stale
  Validated setters       → state corruption becomes impossible from outside
  Callers use syntax:     budget.used, budget.status  (not .used(), .status())
""")
