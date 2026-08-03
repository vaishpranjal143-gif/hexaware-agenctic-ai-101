import importlib

from _maf import BACKEND, MODEL, banner, get_client, run

banner("MAF - File 04 - providers - using a provider to call a tool")

PROVIDERS = [
    ("agent_framework_openai", "OpenAIChatClient", "OpenAI, Azure OpenAI, or anything OpenAI-shaped"),
    ("agent_framework.foundry", "FoundryChatClient", "Foundry, a local LLM provider"),
    ("agent_framework.foundry", "FoundryLocalClient", "Foundry, a local LLM provider"),
    ("agent_framework_anthropic", "AnthropicClient", "Anthropic Claude"),
    ("agent_framework_anthropic", "AnthropicVertexClient", "Claude via Google Vertex"),
]

print("WHICH PROVIDERS ARE AVAILABLE?")
for module_name, class_name, reaches in PROVIDERS:
    try:
        module = importlib.import_module(module_name)
        status = "yes" if hasattr(module, class_name) else "no name"
    except ModuleNotFoundError as error:
        status = "no pkg"
    except Exception:
        status = "error"
    print(f" [{status}] {class_name} {reaches}")
print()

async def main():
    agent = get_client().as_agent(name="p", instructions="Answer in exactly four words.")
    result = await agent.run("What is Microsoft Agent Framework?")
    print(f" this run read. : {BACKEND} / {MODEL}")
    print(f" the agent said : {result.text}")
    print()

run(main())