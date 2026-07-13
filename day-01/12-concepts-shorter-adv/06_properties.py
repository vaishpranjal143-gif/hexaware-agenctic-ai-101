# CONCEPT 6 — PROPERTIES
# @property  → computed attribute (no parentheses, always up-to-date)
# @x.setter  → validate BEFORE storing (bad values never get in)

class TokenBudget:
    WARN   = 0.80   # 80% → yellow
    DANGER = 0.95   # 95% → red

    def __init__(self, limit):
        self._limit, self._used = limit, 0

    @property
    def used(self):       return self._used                         # computed
    @property
    def remaining(self):  return self._limit - self._used           # computed
    @property
    def pct(self):        return round(self._used / self._limit * 100, 1)  # computed
    @property
    def status(self):                                               # computed
        r = self._used / self._limit
        return "red" if r >= self.DANGER else "yellow" if r >= self.WARN else "green"

    @used.setter
    def used(self, v):                   # validated setter
        if v < 0:             raise ValueError("Cannot be negative")
        if v > self._limit:   raise ValueError(f"Exceeds limit {self._limit}")
        self._used = v

    def add(self, n): self.used = self._used + n   # uses the setter → validated

    def __repr__(self):
        bar = "#" * int(self.pct / 5) + "." * (20 - int(self.pct / 5))
        return f"[{bar}] {self.pct}% ({self.status.upper()})"

# ── Demo ──────────────────────────────────────────────────────────────
b = TokenBudget(8000)
b.add(1500);  b.add(3500)
print(b)                           # progress bar
print(f"used={b.used}  remaining={b.remaining}  status={b.status}")

try:   b.used = -100               # setter rejects negative
except ValueError as e: print(f"Blocked: {e}")

try:   b.used = b.remaining + 1   # setter rejects overflow
except ValueError as e: print(f"Blocked: {e}")

try:   b.pct = 50                  # no setter → read-only
except AttributeError as e: print(f"Read-only: {e}")
