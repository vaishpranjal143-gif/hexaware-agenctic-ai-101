"""
╔══════════════════════════════════════════════════════════════════════╗
║  CONCEPT 8 — MRO (Method Resolution Order)                          ║
║  File    : 08_mro.py                                                ║
║  Run     : python 08_mro.py                                         ║
╠══════════════════════════════════════════════════════════════════════╣
║  WHAT IS IT?                                                        ║
║  When a class inherits from multiple parents, Python must decide     ║
║  which parent's version of a method to call. The MRO is the precise ║
║  order Python searches through parent classes.                      ║
║                                                                     ║
║  THE C3 LINEARISATION ALGORITHM:                                    ║
║  Python uses C3 linearisation to compute the MRO. The rule is:     ║
║    1. The class itself comes first                                   ║
║    2. Then parents, left to right                                   ║
║    3. Then grandparents, respecting the left-to-right order         ║
║    4. object is always last                                         ║
║                                                                     ║
║  KEY TOOL:                                                          ║
║    MyClass.__mro__     → shows the exact resolution order           ║
║    super()             → calls the NEXT class in the MRO            ║
║                                                                     ║
║  AGENTIC AI USE CASE: Multi-Modal Agent                             ║
║  An agent that handles text, images, and audio inherits from three  ║
║  capability classes. MRO determines which process() is called by    ║
║  default and how super() chains through all three.                  ║
╚══════════════════════════════════════════════════════════════════════╝
"""


# ─────────────────────────────────────────────────────────────────────
#  PART 1 — THE PROBLEM: The Diamond Problem
# ─────────────────────────────────────────────────────────────────────

print("=" * 60)
print("PART 1 — THE DIAMOND PROBLEM")
print("=" * 60)

print("""
  The Diamond Problem occurs when two parents share a common ancestor:

          object
         /      \\
       A          B
         \\      /
            C

  class A(object): def hello(self): return "A"
  class B(object): def hello(self): return "B"
  class C(A, B):   pass       ← whose hello() does C use?

  Python's C3 linearisation gives a consistent, predictable answer.
""")

class GrandParent:
    def greet(self):
        return "GrandParent.greet()"

class ParentA(GrandParent):
    def greet(self):
        return f"ParentA.greet() → {super().greet()}"

class ParentB(GrandParent):
    def greet(self):
        return f"ParentB.greet() → {super().greet()}"

class Child(ParentA, ParentB):
    pass   # no greet() defined

c = Child()
print(f"Child().greet() = {c.greet()}")
print(f"\nChild.__mro__ = {[cls.__name__ for cls in Child.__mro__]}")
print("""
  Notice:
    1. Child → ParentA → ParentB → GrandParent → object
    2. GrandParent appears ONCE despite two paths reaching it (C3 prevents duplication)
    3. super() inside ParentA calls ParentB (the next in MRO), NOT GrandParent
""")


# ─────────────────────────────────────────────────────────────────────
#  PART 2 — Capability Classes for a Multi-Modal Agent
# ─────────────────────────────────────────────────────────────────────

print("=" * 60)
print("PART 2 — MULTI-MODAL AGENT (Practical MRO)")
print("=" * 60)


class TextCapability:
    """
    Handles text and natural language processing.
    Can be used as a standalone class or mixed into a multi-modal agent.
    """

    def process(self, data: str) -> str:
        return f"[TextCapability] Processing text: '{data}'"

    def capabilities(self) -> list:
        return ["text", "nlp", "summarise", "translate", "sentiment"]

    def describe(self) -> str:
        return "Text-capable (NLP, summarisation, translation)"

    def __repr__(self):
        return "TextCapability()"


class VisionCapability:
    """
    Handles image analysis and computer vision tasks.
    """

    def process(self, data: str) -> str:
        return f"[VisionCapability] Analysing image: '{data}'"

    def capabilities(self) -> list:
        return ["image", "ocr", "object_detection", "caption", "face_recognition"]

    def describe(self) -> str:
        return "Vision-capable (OCR, object detection, captioning)"

    def __repr__(self):
        return "VisionCapability()"


class AudioCapability:
    """
    Handles speech recognition and audio processing tasks.
    """

    def process(self, data: str) -> str:
        return f"[AudioCapability] Transcribing audio: '{data}'"

    def capabilities(self) -> list:
        return ["audio", "speech", "transcribe", "tts", "speaker_id"]

    def describe(self) -> str:
        return "Audio-capable (speech-to-text, TTS, speaker ID)"

    def __repr__(self):
        return "AudioCapability()"


# ── Single-capability agents (simple inheritance) ─────────────────────

class TextOnlyAgent(TextCapability):
    """Agent that only handles text. Simple single-parent inheritance."""
    def __init__(self, name): self.name = name

class VisionOnlyAgent(VisionCapability):
    """Agent that only handles images."""
    def __init__(self, name): self.name = name


# ── Multi-modal agent (multiple inheritance) ──────────────────────────

class MultiModalAgent(TextCapability, VisionCapability, AudioCapability):
    """
    Combines all three capabilities via multiple inheritance.

    MRO order (C3 linearisation):
      MultiModalAgent → TextCapability → VisionCapability → AudioCapability → object

    This means:
      - self.process() by default calls TextCapability.process()
        (TextCapability is first in the MRO after MultiModalAgent itself)
      - self.describe() also calls TextCapability.describe()
      - To reach VisionCapability or AudioCapability, we must call them explicitly
    """

    # Map file extensions to modality names
    EXTENSION_MAP = {
        ".jpg"  : "image",  ".jpeg": "image",
        ".png"  : "image",  ".gif" : "image",
        ".webp" : "image",  ".bmp" : "image",
        ".mp3"  : "audio",  ".wav" : "audio",
        ".ogg"  : "audio",  ".m4a" : "audio",
        ".txt"  : "text",   ".md"  : "text",
        ".pdf"  : "text",   ".csv" : "text",
    }

    def __init__(self, name: str):
        self.name = name
        # With multiple inheritance, avoid calling super().__init__() here
        # unless ALL parent classes define __init__ with super() chains.
        # For mixin-style classes with no __init__, this is not needed.

    def route(self, modality: str, data: str) -> str:
        """
        EXPLICIT DISPATCH — recommended for multi-modal agents.

        Instead of relying on MRO to "accidentally" pick the right parent,
        we explicitly name which parent's process() to call.

        This makes the code clear and predictable — no surprises.
        """
        modality = modality.lower()
        if modality == "text":
            return TextCapability.process(self, data)    # explicit parent call
        elif modality in ("image", "vision"):
            return VisionCapability.process(self, data)
        elif modality in ("audio", "speech"):
            return AudioCapability.process(self, data)
        else:
            raise ValueError(
                f"Unknown modality '{modality}'. "
                f"Choose: text / image / audio"
            )

    def auto_route(self, filename: str) -> str:
        """
        Detect modality from file extension and route automatically.
        Falls back to 'text' for unknown extensions.
        """
        import os
        ext      = os.path.splitext(filename)[1].lower()
        modality = self.EXTENSION_MAP.get(ext, "text")
        return self.route(modality, filename)

    def process_all(self, data: str) -> list:
        """
        Run ALL THREE modalities on the same input.
        Useful for cross-modal analysis (e.g. a document with embedded images).

        Note: we call each parent explicitly to ensure all three run,
        not just the first one found in the MRO.
        """
        return [
            TextCapability.process(self, data),
            VisionCapability.process(self, data),
            AudioCapability.process(self, data),
        ]

    def all_capabilities(self) -> list:
        """Combine capabilities from all three parents (no duplicates)."""
        combined = []
        for parent in [TextCapability, VisionCapability, AudioCapability]:
            combined.extend(parent.capabilities(self))
        return sorted(set(combined))

    def __repr__(self):
        return f"MultiModalAgent(name='{self.name}')"


# ── Using super() to chain all parents ───────────────────────────────

class ChainedTextCapability:
    def process(self, data: str) -> str:
        result = f"[Text] '{data}'"
        # super() calls the NEXT class in the MRO — could be Vision or object
        if hasattr(super(), "process"):
            return result + "\n" + super().process(data)
        return result

class ChainedVisionCapability:
    def process(self, data: str) -> str:
        result = f"[Vision] '{data}'"
        if hasattr(super(), "process"):
            return result + "\n" + super().process(data)
        return result

class ChainedAudioCapability:
    def process(self, data: str) -> str:
        return f"[Audio] '{data}'"

class ChainedMultiModalAgent(
    ChainedTextCapability,
    ChainedVisionCapability,
    ChainedAudioCapability
):
    """Demonstrates how super() chains through the MRO automatically."""
    def __init__(self, name: str):
        self.name = name


# ─────────────────────────────────────────────────────────────────────
#  DEMO
# ─────────────────────────────────────────────────────────────────────

print("\n── MRO: which class handles what ────────────────────────────")
agent = MultiModalAgent("Omni")

print("MultiModalAgent.__mro__:")
for i, cls in enumerate(MultiModalAgent.__mro__):
    arrow = " ← first match for process()" if i == 1 else ""
    print(f"  {i}: {cls.__name__}{arrow}")

print()

print("Default self.process() — which parent wins?")
print(f"  {agent.process('some_data')}")
print("  → TextCapability wins. It is index 1 in the MRO (leftmost parent).")

print()

print("self.describe() — also TextCapability:")
print(f"  {agent.describe()}")

print("\n── Explicit routing (recommended) ──────────────────────────")
print(agent.route("text",  "What is retrieval-augmented generation?"))
print(agent.route("image", "architecture_diagram.png"))
print(agent.route("audio", "interview_recording.mp3"))

print("\n── Auto-routing from file extension ────────────────────────")
test_files = [
    "report.pdf", "photo.jpg", "podcast.mp3",
    "notes.txt", "screenshot.png", "unknown_file"
]
for f in test_files:
    result = agent.auto_route(f)
    print(f"  {f:20s} → {result}")

print("\n── process_all — all three modalities at once ────────────────")
for result in agent.process_all("sensor_data_001"):
    print(f"  {result}")

print("\n── All combined capabilities ─────────────────────────────────")
caps = agent.all_capabilities()
print(f"  {caps}")

print("\n── super() chaining through the full MRO ────────────────────")
chained = ChainedMultiModalAgent("ChainBot")
print("ChainedMultiModalAgent MRO:")
for i, cls in enumerate(ChainedMultiModalAgent.__mro__):
    print(f"  {i}: {cls.__name__}")

print(f"\nchained.process('data') — all three fire via super() chain:")
print(chained.process("shared_data"))

print("\n── MRO of single-capability agents ─────────────────────────")
print(f"TextOnlyAgent MRO: {[c.__name__ for c in TextOnlyAgent.__mro__]}")
print(f"VisionOnlyAgent MRO: {[c.__name__ for c in VisionOnlyAgent.__mro__]}")

text_agent = TextOnlyAgent("Scribe")
print(f"\ntext_agent.process('hello'): {text_agent.process('hello')}")
print(f"text_agent.capabilities(): {text_agent.capabilities()}")

print("\n── MRO consistency check: invalid order raises TypeError ─────")
# Python C3 will raise TypeError if the MRO is logically impossible
class A: pass
class B(A): pass
try:
    class Invalid(A, B): pass  # A before B, but B extends A → impossible
except TypeError as e:
    print(f"  Invalid MRO → TypeError: {e}")

print("\n── Key takeaways ────────────────────────────────────────────")
print("""
  1. MRO = the exact order Python searches for methods in parent classes
  2. Computed by C3 linearisation: left parents before right, no repeats
  3. Inspect with: MyClass.__mro__ or MyClass.mro()
  4. Default self.method() → first match in MRO (leftmost parent)
  5. Explicit parent call → TextCapability.process(self, data) — recommended
  6. super() → calls the NEXT class in the MRO (not necessarily the parent!)
  7. Multi-modal agents: use explicit routing for clarity and predictability
""")
