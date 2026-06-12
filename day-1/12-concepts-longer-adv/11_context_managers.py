"""
╔══════════════════════════════════════════════════════════════════════╗
║  CONCEPT 11 — CONTEXT MANAGERS                                      ║
║  File    : 11_context_managers.py                                   ║
║  Run     : python 11_context_managers.py                            ║
╠══════════════════════════════════════════════════════════════════════╣
║  WHAT IS IT?                                                        ║
║  A context manager controls what happens when you ENTER and EXIT    ║
║  a 'with' block. The __exit__ method is ALWAYS called, even if an  ║
║  exception occurs inside the block. This guarantees cleanup.        ║
║                                                                     ║
║  THE 'with' STATEMENT:                                              ║
║    with MyContextManager() as obj:                                  ║
║        # __enter__ has run; obj is what __enter__ returned          ║
║        do_something()                                               ║
║    # __exit__ has now run — resource is cleaned up                  ║
║                                                                     ║
║  TWO DUNDER METHODS:                                                ║
║    __enter__(self)                         → set up, return self    ║
║    __exit__(self, exc_type, exc_val, tb)   → tear down, return bool ║
║      Return True  → suppress the exception                         ║
║      Return False → let the exception propagate                    ║
║                                                                     ║
║  AGENTIC AI USE CASE: Code Execution Sandbox                        ║
║  Agents that run code need a sandbox that: captures output, tracks  ║
║  time, handles errors, and never crashes the outer pipeline.        ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import time
import sys
import io


# ─────────────────────────────────────────────────────────────────────
#  PART 1 — THE PROBLEM: No cleanup guarantee
# ─────────────────────────────────────────────────────────────────────

print("=" * 60)
print("PART 1 — THE PROBLEM (no cleanup guarantee)")
print("=" * 60)

def bad_execute(code: str):
    """Redirects stdout but has no cleanup guarantee on exception."""
    buffer    = io.StringIO()
    sys.stdout = buffer
    exec(code)                # ← if this raises, stdout is never restored!
    sys.stdout = sys.__stdout__
    return buffer.getvalue()

print("Calling bad_execute with code that raises an error:")
try:
    bad_execute("x = 1 / 0")    # raises ZeroDivisionError
except Exception as e:
    # stdout was NEVER restored — all subsequent print() calls break!
    pass

# Force restore for demo purposes
sys.stdout = sys.__stdout__
print("Problem: stdout was left redirected after the exception.")
print("Problem: Any subsequent print() would go into the void.")
print("Problem: Without a context manager, cleanup is not guaranteed.\n")


# ─────────────────────────────────────────────────────────────────────
#  PART 2 — SIMPLE EXAMPLE: Timer context manager
# ─────────────────────────────────────────────────────────────────────

print("=" * 60)
print("PART 2 — SIMPLE EXAMPLE: Timer Context Manager")
print("=" * 60)


class Timer:
    """
    A minimal context manager that measures elapsed time.

    __enter__: record the start time, return self
    __exit__ : calculate elapsed time, do NOT suppress exceptions
    """

    def __enter__(self):
        """
        Called when entering the 'with' block.
        Return value is bound to the 'as' variable.
        """
        self._start = time.perf_counter()
        return self          # → bound to 't' in: with Timer() as t

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called when leaving the 'with' block.

        Parameters:
            exc_type  : exception class if an exception occurred, else None
            exc_val   : exception instance, else None
            exc_tb    : traceback object, else None

        Returning False → let any exception propagate normally.
        """
        self.elapsed_ms = (time.perf_counter() - self._start) * 1000
        return False    # do not suppress exceptions

    def __repr__(self):
        return f"Timer(elapsed={self.elapsed_ms:.2f}ms)"


print("Using Timer context manager:")
with Timer() as t:
    total = sum(range(500_000))
print(f"  sum(range(500_000)) = {total}")
print(f"  Elapsed: {t.elapsed_ms:.2f}ms")

print("\nEven with an exception, elapsed is recorded:")
try:
    with Timer() as t2:
        x = sum(range(100_000))
        raise ValueError("Intentional error")
except ValueError:
    pass
print(f"  Elapsed before error: {t2.elapsed_ms:.2f}ms")


# ─────────────────────────────────────────────────────────────────────
#  PART 3 — FULL EXAMPLE: Agent Code Execution Sandbox
# ─────────────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("PART 3 — FULL EXAMPLE: CodeSandbox Context Manager")
print("=" * 60)


class CodeSandbox:
    """
    A safe execution environment for agent-generated Python code.

    __enter__:
        1. Records start time
        2. Replaces sys.stdout with a StringIO buffer
           so all print() output is captured instead of displayed

    __exit__ (ALWAYS runs — even on exception):
        1. Restores sys.stdout to the original
        2. Captures whatever was printed during execution
        3. Truncates output if it exceeds max_output_chars
        4. Records elapsed execution time
        5. If an exception occurred, stores it in self.error
        6. Returns True → SUPPRESSES the exception
           (the outer agent loop keeps running no matter what)

    SAFE_BUILTINS:
        Allows only safe built-in functions.
        Blocks: import, open, os, sys, subprocess, __import__, eval, exec.

    Usage:
        with CodeSandbox() as sb:
            exec(agent_generated_code)
        result = sb.result()
    """

    # Only safe built-ins allowed in exec() context
    SAFE_BUILTINS = {
        "print"      : print,
        "range"      : range,
        "len"        : len,
        "sum"        : sum,
        "min"        : min,
        "max"        : max,
        "abs"        : abs,
        "round"      : round,
        "int"        : int,
        "float"      : float,
        "str"        : str,
        "bool"       : bool,
        "list"       : list,
        "dict"       : dict,
        "tuple"      : tuple,
        "set"        : set,
        "enumerate"  : enumerate,
        "zip"        : zip,
        "sorted"     : sorted,
        "isinstance" : isinstance,
    }

    def __init__(self, max_output_chars: int = 2000):
        self.max_output_chars  = max_output_chars
        self.captured_output   = ""
        self.execution_time_ms = 0.0
        self.error             = None
        self._start            = None
        self._buffer           = None
        self._original_stdout  = None

    def __enter__(self):
        """
        SET UP:
            1. Start the clock
            2. Redirect stdout so print() goes to our buffer
        Returns self → bound to 'as' variable: with CodeSandbox() as sb
        """
        self._start           = time.perf_counter()
        self._buffer          = io.StringIO()
        self._original_stdout = sys.stdout
        sys.stdout            = self._buffer    # all print() now goes here
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        TEAR DOWN — runs always, even if exec() raised.

        exc_type  : ZeroDivisionError, NameError, etc., or None
        exc_val   : the exception instance, or None
        exc_tb    : the traceback, or None

        Returns True → exception is swallowed.
        The calling code (the agent pipeline) never sees it.
        """
        # Step 1: ALWAYS restore stdout first
        sys.stdout = self._original_stdout

        # Step 2: Capture what was printed during execution
        raw = self._buffer.getvalue()
        if len(raw) > self.max_output_chars:
            raw = raw[:self.max_output_chars] + "\n... [output truncated]"
        self.captured_output = raw.strip()

        # Step 3: Record how long execution took
        self.execution_time_ms = (time.perf_counter() - self._start) * 1000

        # Step 4: Record any exception details
        if exc_type is not None:
            self.error = f"{exc_type.__name__}: {exc_val}"

        # Step 5: Return True → SUPPRESS the exception
        return True

    # ── Convenience methods ───────────────────────────────────────────

    @property
    def succeeded(self) -> bool:
        """True if no exception occurred during execution."""
        return self.error is None

    def result(self) -> dict:
        """Return all execution metadata as a clean dict."""
        return {
            "output"       : self.captured_output,
            "exec_time_ms" : round(self.execution_time_ms, 3),
            "truncated"    : "truncated" in self.captured_output,
            "error"        : self.error,
            "success"      : self.succeeded,
        }

    def exec_safe(self, code: str) -> dict:
        """
        Convenience: enter sandbox, exec code with safe builtins, return result.
        Equivalent to the full 'with' block — just shorter.
        """
        with self:
            exec(code, {"__builtins__": self.SAFE_BUILTINS})
        return self.result()


# ─────────────────────────────────────────────────────────────────────
#  DEMO
# ─────────────────────────────────────────────────────────────────────

print("\n── Case 1: Valid code — output captured ─────────────────────")
with CodeSandbox() as sb:
    exec("for i in range(5): print(f'Agent step {i}')")

r = sb.result()
print(f"  success      : {r['success']}")
print(f"  output       : {r['output']}")
print(f"  exec_time_ms : {r['exec_time_ms']}")

print("\n── Case 2: ZeroDivisionError — outer code keeps running ─────")
with CodeSandbox() as sb:
    exec("result = 10 / 0")           # raises — sandbox catches it

r = sb.result()
print(f"  success : {r['success']}")
print(f"  error   : {r['error']}")
print("  → Outer agent pipeline is completely unaffected.")

print("\n── Case 3: NameError — catching unknown variable ─────────────")
with CodeSandbox() as sb:
    exec("print(undefined_variable)")

r = sb.result()
print(f"  error  : {r['error']}")
print(f"  output : '{r['output']}'")

print("\n── Case 4: Output truncation ─────────────────────────────────")
with CodeSandbox(max_output_chars=50) as sb:
    exec("print('A' * 200)")

r = sb.result()
print(f"  truncated : {r['truncated']}")
print(f"  output    : '{r['output'][:40]}...'")

print("\n── Case 5: Dangerous import blocked by SAFE_BUILTINS ─────────")
result = CodeSandbox().exec_safe("import os; os.system('echo hacked')")
print(f"  success : {result['success']}")
print(f"  error   : {result['error']}")
print("  → os module is not in SAFE_BUILTINS → ImportError caught.")

print("\n── Case 6: Timing a real computation ───────────────────────")
with CodeSandbox() as sb:
    exec("total = sum(range(1_000_000))\nprint(f'Sum = {total}')")

r = sb.result()
print(f"  output       : {r['output']}")
print(f"  exec_time_ms : {r['exec_time_ms']:.2f}ms")

print("\n── Case 7: Multiple exec blocks in one sandbox ───────────────")
sb2 = CodeSandbox()
print("  Block A:")
with sb2:
    exec("print('Block A line 1')\nprint('Block A line 2')")
print(f"  A result: {sb2.result()['output']}")

# Reuse same sandbox (state resets on each enter)
print("  Block B (same sandbox object, reused):")
with sb2:
    exec("print('Block B')")
print(f"  B result: {sb2.result()['output']}")

print("\n── __exit__ parameter explanation ───────────────────────────")
print("""
  __exit__(self, exc_type, exc_val, exc_tb):

  If NO exception occurred:
      exc_type = None, exc_val = None, exc_tb = None

  If ZeroDivisionError occurred:
      exc_type = ZeroDivisionError
      exc_val  = division by zero (the exception instance)
      exc_tb   = <traceback object>

  Return value:
      True  → Python treats the exception as "handled" → suppressed
      False → Python re-raises the exception normally
""")

print("── Key takeaways ────────────────────────────────────────────")
print("""
  __enter__  → set up resources, return 'self' (or the resource)
  __exit__   → ALWAYS runs; restore, calculate, record, and decide
               whether to suppress the exception (True/False)
  with X as y → __enter__ runs; y = what __enter__ returned
  Return True  → suppress exception; outer code continues
  Return False → exception propagates normally

  Common context manager uses:
    File handling     → open("file") as f:
    Database session  → Session() as session:
    Timing            → Timer() as t:
    Code sandbox      → CodeSandbox() as sb:
    Lock acquisition  → threading.Lock() as lock:
""")
