# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ Confidential: instructor-only assessments (never push to GitHub)

This repository is shared with **students**. The `hexaware-assessment/` folder holds the
instructor assessment papers (`hexaware-assessment-1.docx`, `hexaware-assessment-2.docx`,
answer keys, etc.) and **must never be committed, pushed, or otherwise exposed to students**.
Both the folder and any `hexaware-assessment-*.docx` file at the repo root are gitignored.

Rules:
- Always create/edit assessment material **inside `hexaware-assessment/`**, never at the repo root.
- Never run `git add -f`, `git rm` the ignore rule, or otherwise force-track these files.
- Assessment 1 covers **Days 1–6**; Assessment 2 covers **Days 7–12**.

## What this repo is

A 92-hour training program on Agentic AI and Microsoft Foundry (formerly Azure AI Foundry). It is **not a single application** — it is a chronological collection of self-contained lesson artifacts organized as `day-01/` … `day-12/`. Each day is independent; there is no shared library imported across days. `main.py` at the root is a throwaway stub, not an entry point for the lessons.

The progression is roughly: Python/async fundamentals (day 1–3) → transformers & attention from scratch (day 3–5, see `day-05/tinylm/`) → quantization/LoRA fine-tuning (day 6–7) → chatbots on Azure OpenAI (day 8–9) → RAG (day 10–11) → Semantic Kernel agents (day 12).

## Environment & commands

- Python **>=3.14**, managed with **uv** (`uv.lock`, `pyproject.toml`). The `.venv` is committed-adjacent; activate or use `uv run`.
- Install/sync deps: `uv sync`
- Run any lesson script: `uv run python day-N/.../script.py` (run from repo root, but note the caveat below about `_setup.py` imports).
- Run a Gradio app (day 8+): `uv run python day-11/rag-vector/app.py` → opens a local web UI via `demo.launch()`.
- There is **no test suite, linter, or build step**. Lessons are validated by running them and observing output.

## Azure OpenAI configuration (critical)

Almost every runnable lesson from day 8 onward talks to **Azure OpenAI**, configured via a `.env` file read with `python-dotenv`. Required keys:

```
AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_MODEL,
AZURE_OPENAI_API_VERSION, AZURE_OPENAI_EMBEDDING_MODEL  (RAG only)
```

`.env` files are gitignored. Note there are **multiple `.env` files** (root `.env`, `day-08/.env`) — scripts call `load_dotenv()` / `load_dotenv(find_dotenv())`, which resolves the nearest one. When adding a lesson, match whichever `.env` the sibling scripts expect.

Three different client styles appear depending on the day — match the surrounding day's style rather than unifying:
- **Raw OpenAI SDK**: `openai.AzureOpenAI(...)` (day 8).
- **LangChain**: `langchain_openai.AzureChatOpenAI` / `AzureOpenAIEmbeddings` (day 10–11 RAG).
- **Semantic Kernel**: `semantic_kernel.connectors.ai.open_ai.AzureChatCompletion` (day 12).

## Recurring patterns to follow

**Chatbot lessons (day 8–9, 11)** consistently split into three files — replicate this shape when extending:
- `chatbot.py` — LLM client + a generator/function that yields streaming responses.
- `app.py` — thin Gradio `gr.ChatInterface` wrapper calling into `chatbot.py`.
- `system_prompt.py` — a `SYSTEM_PROMPT` string constant. The assistant persona across lessons is **"Caramel AI"**.

**RAG lessons (day 11)** add `rag_pipeline.py`: download a source doc → chunk with `RecursiveCharacterTextSplitter` → embed → `FAISS.from_documents` in-memory vector store → `retrieve(query, k)`. Variants (`rag-text`, `rag-pdf`, `rag-pdf-gemini`, `rag-vector`) demonstrate the same pipeline over different source formats / providers (note `rag-pdf-gemini` uses `google-genai`, not Azure).

**Semantic Kernel lessons (day 12)** share a per-folder `_setup.py` exposing `azure_chat()` and `build_kernel()` helpers. Lesson scripts (`01_...py`, `02_...py`) `from _setup import build_kernel` and are typically `asyncio.run(main())`. **These scripts import `_setup` as a sibling module, so run them from inside their own folder** (`cd day-12/semantic-kernel/01-fundamentals && uv run python 01_hello_kernel.py`), not from repo root.

## Local models

`models/` holds downloaded HuggingFace weights (`gemma-4-e2b`, `qwen-0.5b`) used by the from-scratch/fine-tuning days. `models/` is gitignored — do not commit `.safetensors`. `day-05/tinylm/` is a minimal transformer implemented from scratch (`src/{attention,model,tokenizer,transformer,train}.py`).
