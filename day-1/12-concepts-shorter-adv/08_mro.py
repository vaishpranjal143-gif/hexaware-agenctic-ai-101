# CONCEPT 8 — MRO (Method Resolution Order)
# When a class inherits from multiple parents, Python uses C3 linearisation
# to decide WHICH parent's method runs.  Print __mro__ to see the order.

class TextCapability:
    def process(self, data): return f"[Text]   '{data}'"
    def modality(self):      return "text"

class VisionCapability:
    def process(self, data): return f"[Vision] '{data}'"
    def modality(self):      return "image"

class AudioCapability:
    def process(self, data): return f"[Audio]  '{data}'"
    def modality(self):      return "audio"

class MultiModalAgent(TextCapability, VisionCapability, AudioCapability):
    ROUTES = {".jpg":"image", ".png":"image", ".mp3":"audio",
              ".wav":"audio", ".txt":"text",  ".pdf":"text"}

    def __init__(self, name): self.name = name

    def route(self, modality, data):        # explicit — recommended
        if   modality == "text":  return TextCapability.process(self, data)
        elif modality == "image": return VisionCapability.process(self, data)
        elif modality == "audio": return AudioCapability.process(self, data)

    def auto_route(self, filename):         # detect from extension
        import os
        mod = self.ROUTES.get(os.path.splitext(filename)[1], "text")
        return self.route(mod, filename)

# ── Demo ──────────────────────────────────────────────────────────────
print("MRO:", [c.__name__ for c in MultiModalAgent.__mro__])
print("Default process() uses:", MultiModalAgent.__mro__[1].__name__, "← leftmost parent")

agent = MultiModalAgent("Omni")
print(agent.process("hello"))                     # TextCapability wins (index 1)
print(agent.route("image", "photo.jpg"))
print(agent.route("audio", "meeting.mp3"))

for f in ["report.pdf", "photo.jpg", "speech.mp3", "unknown"]:
    print(agent.auto_route(f))
