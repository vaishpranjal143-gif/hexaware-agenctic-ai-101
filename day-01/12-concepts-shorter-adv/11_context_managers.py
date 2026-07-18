# CONCEPT 11 — CONTEXT MANAGERS
# __enter__ sets up a resource.  __exit__ ALWAYS cleans up — even on exception.
# Return True from __exit__ → suppress the exception.
# Return False (or None)   → let the exception propagate.

import time, sys, io

class Timer:                              # simple example: measure elapsed time
    def __enter__(self):
        self._t = time.perf_counter();  return self
    def __exit__(self, *_):
        self.ms = (time.perf_counter() - self._t) * 1000;  return False

class CodeSandbox:                        # agent example: safe code execution
    def __init__(self, max_chars=500):
        self.max_chars, self.output, self.error, self.ms = max_chars, "", None, 0

    def __enter__(self):
        self._t   = time.perf_counter()
        self._buf = io.StringIO()         # buffer captures all print() output
        sys.stdout = self._buf            # redirect stdout → buffer
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = sys.__stdout__                        # always restore first
        raw = self._buf.getvalue()
        self.output = raw[:self.max_chars] + ("…" if len(raw) > self.max_chars else "")
        self.ms     = (time.perf_counter() - self._t) * 1000
        if exc_type: self.error = f"{exc_type.__name__}: {exc_val}"
        return True                                        # swallow ANY exception

# ── Demo ──────────────────────────────────────────────────────────────
with Timer() as t:
    _ = sum(range(500_000))
print(f"Timer: {t.ms:.1f}ms")

with CodeSandbox() as sb:
    exec("for i in range(4): print(f'step {i}')")
print(f"Output : {sb.output!r}")
print(f"Time   : {sb.ms:.2f}ms")

with CodeSandbox() as sb:                # error → swallowed, not crashed
    exec("x = 1/0")
print(f"Error  : {sb.error}")
print(f"Output : {sb.output!r}")        # empty — nothing was printed

with CodeSandbox(max_chars=10) as sb:   # truncation
    exec("print('A' * 200)")
print(f"Truncated: {sb.output!r}")
