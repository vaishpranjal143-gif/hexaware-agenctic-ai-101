from os import getenv
from dotenv import load_dotenv, find_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

load_dotenv(find_dotenv())

def azure_chat(service_id="chat"):
    return AzureChatCompletion(
        service_id=service_id,
        deployment_name=getenv("AZURE_OPENAI_MODEL"),
        endpoint=getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=getenv("AZURE_OPENAI_API_KEY"),
        api_version=getenv("AZURE_OPENAI_API_VERSION")
    )

def build_kernel():
    kernel = Kernel()
    kernel.add_service(azure_chat())
    return kernel