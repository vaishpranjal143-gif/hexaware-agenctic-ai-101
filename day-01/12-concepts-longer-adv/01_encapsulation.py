"""
╔══════════════════════════════════════════════════════════════════════╗
║  CONCEPT 1 — ENCAPSULATION                                          ║
║  File    : 01_encapsulation.py                                      ║
║  Run     : python 01_encapsulation.py                               ║
╠══════════════════════════════════════════════════════════════════════╣
║  WHAT IS IT?                                                        ║
║  Bundling data (attributes) and methods together inside a class,    ║
║  and controlling what the outside world can see and touch.          ║
║                                                                     ║
║  THREE LEVELS OF ACCESS:                                            ║
║    public     no prefix       → anyone can read/write              ║
║    protected  _single         → "please don't touch" (convention)  ║
║    private    __double        → truly hidden via name mangling      ║
║                                                                     ║
║  AGENTIC AI USE CASE: LLM API Client                                ║
║  The API key must never be exposed. Rate limiting runs silently.    ║
║  Callers just call .complete(prompt) — all complexity is hidden.    ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import time


# ─────────────────────────────────────────────────────────────────────
#  PART 1 — THE PROBLEM: No Encapsulation
#  When everything is public, state can be read, changed, or corrupted
#  by anyone at any time.
# ─────────────────────────────────────────────────────────────────────

print("=" * 60)
print("PART 1 — THE PROBLEM (No Encapsulation)")
print("=" * 60)

class BadLLMClient:
    """A client with no encapsulation — everything is exposed."""

    def __init__(self, api_key: str, model: str):
        self.api_key    = api_key    # ← DANGER: anyone can read the secret key
        self.model      = model
        self.call_count = 0          # ← DANGER: anyone can tamper with counters

    def complete(self, prompt: str) -> str:
        self.call_count += 1
        return f"[{self.model}] Response to: {prompt[:40]}"


bad_client = BadLLMClient("sk-super-secret-xyz999", "gpt-4")

print(bad_client.complete("What is an AI agent?"))
print()

# Problems that encapsulation prevents:
print("Problem 1 — Key leaks into logs or error messages:")
print(f"  bad_client.api_key = '{bad_client.api_key}'")

print("\nProblem 2 — State can be corrupted from outside:")
bad_client.call_count = -999            # Tampering!
print(f"  bad_client.call_count = {bad_client.call_count}  ← this makes no sense")

print("\nProblem 3 — No rate limit enforcement:")
bad_client.call_count = 0              # Reset defeats any tracking


# ─────────────────────────────────────────────────────────────────────
#  PART 2 — THE SOLUTION: Encapsulation
# ─────────────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("PART 2 — THE SOLUTION (With Encapsulation)")
print("=" * 60)


class RateLimitError(Exception):
    """Raised when calls exceed the model's requests-per-minute limit."""
    pass


class LLMClient:
    """
    A production-ready LLM API client.

    PRIVATE  (__double_underscore):
        __api_key         → stored as _LLMClient__api_key internally
        __call_count      → internal rate-limit counter
        __window_start    → start of the current 60-second window

    PROTECTED (_single_underscore):
        _model            → readable, but callers should use .model property
        _rpm_limit        → rate limit threshold

    PUBLIC (no prefix):
        complete()        → the only method callers need
        get_stats()       → usage info (key is never included)
        model  (property) → read-only access to model name
    """

    # Class-level constant: shared across all instances, uppercase by convention
    SUPPORTED_MODELS = ["gpt-4", "gpt-4o", "claude-3-sonnet", "claude-3-opus"]

    def __init__(self, api_key: str, model: str = "gpt-4", rpm_limit: int = 60):
        # Validate early — fail loudly rather than fail silently later
        if model not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"Unknown model '{model}'. "
                f"Supported: {self.SUPPORTED_MODELS}"
            )

        # ── PRIVATE: hidden from all outside access ──────────────────
        self.__api_key         = api_key      # name-mangled → _LLMClient__api_key
        self.__call_count      = 0
        self.__window_start    = time.time()

        # ── PROTECTED: internal use, not for callers ─────────────────
        self._model            = model
        self._rpm_limit        = rpm_limit
        self._total_calls_ever = 0            # lifetime counter (not per-window)

    # ── PUBLIC INTERFACE ──────────────────────────────────────────────

    def complete(self, prompt: str) -> str:
        """
        The ONLY method external callers need.

        Rate limiting, authentication, and retry logic are all
        handled internally — the caller never manages them.
        """
        self.__enforce_rate_limit()        # private check runs silently
        self.__call_count      += 1
        self._total_calls_ever += 1
        return self.__send_request(prompt)

    def get_stats(self) -> dict:
        """
        Returns safe usage information.
        The API key is NEVER included — it never leaves this class.
        """
        return {
            "model"              : self._model,
            "calls_this_window"  : self.__call_count,
            "calls_total"        : self._total_calls_ever,
            "rpm_limit"          : self._rpm_limit,
            "rpm_remaining"      : self._rpm_limit - self.__call_count,
        }

    @property
    def model(self) -> str:
        """
        Read-only property: callers can read the model name
        but cannot change it after construction.
        """
        return self._model

    # ── PRIVATE HELPERS ───────────────────────────────────────────────

    def __enforce_rate_limit(self):
        """
        Private: called automatically inside complete().
        Resets the window counter every 60 seconds.
        External callers cannot call this directly.
        """
        now = time.time()
        window_age = now - self.__window_start

        if window_age >= 60:
            # New 60-second window started → reset counter
            self.__window_start = now
            self.__call_count   = 0
            print("  [RateLimit] Window reset — counter cleared.")

        if self.__call_count >= self._rpm_limit:
            wait_sec = int(60 - window_age)
            raise RateLimitError(
                f"Rate limit reached ({self._rpm_limit} RPM). "
                f"Retry in {wait_sec} second(s)."
            )

    def __send_request(self, prompt: str) -> str:
        """
        Private: contains the actual HTTP logic.
        The __api_key is used ONLY here — it never leaves this method.

        Real implementation would be:
            import anthropic
            client = anthropic.Anthropic(api_key=self.__api_key)
            message = client.messages.create(
                model=self._model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        """
        preview = prompt[:55] + "..." if len(prompt) > 55 else prompt
        return (
            f"[{self._model}] '{preview}'"
            f"  (call #{self._total_calls_ever})"
        )

    # ── DUNDER METHODS ────────────────────────────────────────────────

    def __repr__(self) -> str:
        """
        Shows useful debug info but MASKS the key.
        This is what prints in the REPL or error messages.
        """
        masked = f"****{self.__api_key[-4:]}"
        return (
            f"LLMClient("
            f"model='{self._model}', "
            f"key='{masked}', "
            f"rpm={self._rpm_limit})"
        )

    def __del__(self):
        """Called when the object is garbage-collected — cleanup hook."""
        print(f"\n[Cleanup] LLMClient closed after {self._total_calls_ever} total call(s).")


# ─────────────────────────────────────────────────────────────────────
#  DEMO
# ─────────────────────────────────────────────────────────────────────

print("\n── Creating LLMClient ──────────────────────────────────────")
client = LLMClient("sk-real-api-key-abc1234", model="gpt-4", rpm_limit=5)

print("\n── Normal usage ────────────────────────────────────────────")
print(client.complete("What is chain-of-thought prompting?"))
print(client.complete("List three types of AI agents."))
print(client.complete("What is the ReAct framework?"))

print("\n── Inspecting the client ───────────────────────────────────")
print(f"Stats : {client.get_stats()}")
print(f"Model : {client.model}")            # property — read-only
print(f"Repr  : {client}")                  # __repr__ — key is masked

print("\n── Proving the key is private ──────────────────────────────")
try:
    print(client.__api_key)                 # This MUST fail
except AttributeError as e:
    print(f"  Blocked correctly: {e}")

# Python mangles the name but it's still accessible if you know the trick
# (This is a teaching point — it's by convention, not cryptography)
print(f"\n  Mangled name works (but bad practice):")
print(f"  client._LLMClient__api_key = '{client._LLMClient__api_key}'")
print(f"  → Name mangling is a deterrent, not a lock.")

print("\n── Testing the rate limit (limit = 5) ──────────────────────")
for i in range(4, 8):
    try:
        client.complete(f"Question #{i}")
        print(f"  Call {i}: OK")
    except RateLimitError as e:
        print(f"  Call {i}: BLOCKED → {e}")
        break

print("\n── Invalid model raises ValueError ─────────────────────────")
try:
    bad = LLMClient("sk-xxx", model="gpt-3")
except ValueError as e:
    print(f"  {e}")

print("\n── Key takeaways ───────────────────────────────────────────")
print("""
  1. __double  → name mangled → strong deterrent (not a hard lock)
  2. _single   → convention only → communicates "internal use"
  3. @property → read-only attribute via a getter function
  4. Callers only ever see: complete(), get_stats(), model
  5. All complexity (auth, rate limit, retry) is invisible to callers
""")
