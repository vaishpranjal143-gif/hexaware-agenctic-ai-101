import os
import warnings
from dotenv import find_dotenv, load_dotenv
from autogen_core.models import ModelFamily, ModelInfo
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

warnings.filterwarnings("ignore", message="Resolved model mismatch")
load_dotenv(find_dotenv())

def get_client(deployment: str | None = None) -> AzureOpenAIChatCompletionClient:
    """Return a ready-to-use AzureOpenAIChatCompletionClient instance."""
    deployment=deployment or os.environ["AZURE_OPENAI_MODEL"]
    return AzureOpenAIChatCompletionClient(
    azure_deployment=deployment,
    model=deployment,
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

# def get_client() -> AzureOpenAIChatCompletionClient:
#     """Return a ready-to-use AzureOpenAIChatCompletionClient instance."""
#     return AzureOpenAIChatCompletionClient(
#     azure_deployment=os.environ["AZURE_OPENAI_MODEL"],
#     model=os.environ["AZURE_OPENAI_MODEL"],
#     api_version=os.environ["AZURE_OPENAI_API_VERSION"],
#     azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
#     api_key=os.environ["AZURE_OPENAI_API_KEY"],
#     model_info=ModelInfo(
#         vision=True,
#         function_calling=True,
#         json_output=True,
#         family=ModelFamily.UNKNOWN,
#         structured_output=True,
#         multiple_system_messages=True,
#     ),
# )