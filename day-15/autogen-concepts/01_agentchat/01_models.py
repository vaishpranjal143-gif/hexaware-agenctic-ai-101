import asyncio
import os
import warnings
from dotenv import find_dotenv, load_dotenv
from autogen_core.models import ModelFamily, ModelInfo, UserMessage
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

load_dotenv(find_dotenv())
warnings.filterwarnings("ignore", message="Resolved 'openai' package is not installed.")

client = AzureOpenAIChatCompletionClient(
    azure_deployment=os.environ["AZURE_OPENAI_MODEL"],
    model=os.environ["AZURE_OPENAI_MODEL"],
    api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    model_info=ModelInfo(
        vision=True,
        function_calling=True,
        json_output=True,
        family=ModelFamily.UNKNOWN,
        structured_output=True,
        multiple_system_messages=True,
    ),
)

async def main():
    reply = await client.create([
        UserMessage(content="A customer's headphones arrived cracked."
                            "Reply in one sentence.",
                    source="customer")
    ])
    print("\nREPLY :", reply.content)
    print("USAGE :", reply.usage)
    await client.close()

asyncio.run(main())