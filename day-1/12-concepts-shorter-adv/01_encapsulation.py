# CONCEPT 1 — ENCAPSULATION
# Bundle data + methods. Control what the outside world can touch.
# __double  = private (name-mangled)   _single = protected (convention)

class LLMClient:
    def __init__(self, api_key, model="gpt-4"):
        self.__api_key = api_key        # private — hidden from callers
        self._model    = model          # protected — internal use
        self.__calls   = 0

    def complete(self, prompt):         # public — only interface callers need
        self.__calls += 1
        return f"[{self._model}] Response #{self.__calls}: {prompt[:30]}..."

    def stats(self):                    # safe: exposes usage but never the key
        return {"model": self._model, "calls": self.__calls}

    def __repr__(self):                 # masked: last 4 chars only
        return f"LLMClient(model={self._model!r}, key='****{self.__api_key[-4:]}')"

# ── Demo ──────────────────────────────────────────────────────────────
client = LLMClient("sk-secret-xyz1234", "gpt-4")
print(client.complete("What is an AI agent?"))   # works ✓
print(client.stats())                             # safe ✓
print(client)                                     # key is masked ✓
try:
    print(client.__api_key)                       # should fail
except AttributeError as e:
    print(f"Private blocked: {e}")                # blocked ✓
