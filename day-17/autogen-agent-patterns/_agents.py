import asyncio
import os
import warnings
from typing import Any
from dotenv import find_dotenv, load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ModelFamily, ModelInfo
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

warnings.filterwarnings("ignore", message="Resolved model mismatch")
load_dotenv(find_dotenv())

def get_client() -> AzureOpenAIChatCompletionClient:
    """"Return a ready-to-use Azure OpenAI client built from the .env file."""
    return AzureOpenAIChatCompletionClient(
        azure_deployment=os.environ["AZURE_OPENAI_MODEL"],
        model=os.environ["AZURE_OPENAI_MODEL"],
        api_version=os.environ["AZURE_OPENAI_API_VERSION"],
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        model_info=ModelInfo(
            vision=True, function_calling=True, json_output=True,
            family=ModelFamily.UNKNOWN, structured_output=True,
            multiple_system_messages=True
        )
    )

async def agent_step(name: str, instruction: str, task: str, client: Any = None) -> str:
    """Run ONE agent as ONE workflow step, and hand back what it said."""
    own_client = client is None
    client = client or get_client()
    try:
        agent = AssistantAgent(name=name, model_client=client, system_message=instruction)
        result = await agent.run(task=task)
        return result.messages[-1].to_text().strip()
    finally:
        if own_client:
            await client.close()

def run(coro):
    """Run an async workflow from a plain script. Just asyncio.run with nicer name"""
    return asyncio.run(coro)