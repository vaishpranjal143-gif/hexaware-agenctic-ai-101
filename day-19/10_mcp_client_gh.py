import os
import gradio as gr
from httpx import AsyncClient
from agent_framework import FunctionInvocationContext, MCPStreamableHTTPTool, Message
from _maf import BACKEND, MODEL, banner, get_client

banner("File -10 - GH MCP Client")

URL = "https://api.githubcopilot.com/mcp"
TOKEN = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN", "")
if not TOKEN:
    raise SystemExit("Set GITHUB_PERSONAL_ACCESS_TOKEN in .env before running this app.")

READ = ["get_me", "search_repositories", "get_file_contents", "list_commits"]
WRITE = ["create_repository", "create_or_update_file", "delete_file"]
ALLOWED = READ + WRITE
INSTRUCTIONS = ("You are a GitHub assistant. Use the tools for anything about "
                "GitHub - never guess a name or a number. You CAN create "
                "repositories and create or delete files; do it when asked, "
                "then say what you did. Answer in a few lines.")

async def answer(message: str, history: list[dict]) -> str:
    """One user message in, one reply out. Gradio supplies the history"""
    used: list[str] = []

    async def watch(context: FunctionInvocationContext, next):
        used.append(context.function.name)
        await next()

    http = AsyncClient(headers={"Authorization": f"Bearer {TOKEN}"},
                       follow_redirects=True, timeout=60)
    async with MCPStreamableHTTPTool(name="github", url=URL,
                                     http_client=http, allowed_tools=ALLOWED) as github:
        agent = get_client().as_agent(name="gh", tools=[github],
                                      middleware=[watch], instructions=INSTRUCTIONS)
        past = [Message(m["role"], [m["content"]]) for m in history
                if isinstance(m.get("content"), str)]
        result = await agent.run([*past, Message("user", [message])])

    return f"{result.text}\n\n`tools used: {', '.join(used) or 'none'}`"

demo = gr.ChatInterface(
    fn=answer,
    title="GH MCP CLIENT",
    description=f"backend: {BACKEND} - model: {MODEL} - MCP GITHUB",
    examples=[
        {"text": "Who am I on GitHub?"},
        {"text": "Create a public repo called maf-demo-001 with a README."},
        {"text": "Add a file hello.txt saying 'hi from MCP' to maf-demo-01"},
        {"text": "Delete hello.txt from maf-demo-001"},
    ]
)

if __name__ == "__main__":
    demo.launch()