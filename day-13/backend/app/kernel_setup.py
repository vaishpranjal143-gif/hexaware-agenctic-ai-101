from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextEmbedding
from app.config import get_settings

def azure_chat(service_id: str = "chat") -> AzureChatCompletion:
    s = get_settings()
    return AzureChatCompletion(
        service_id=service_id,
        deployment_name=s.azure_openai_model,
        endpoint=s.azure_openai_endpoint,
        api_key=s.azure_openai_api_key,
        api_version=s.azure_openai_api_version,
    )

def azure_embedding() -> AzureTextEmbedding:
    s = get_settings()
    return AzureTextEmbedding(
        deployment_name=s.azure_openai_embedding_model,
        endpoint=s.azure_openai_endpoint,
        api_key=s.azure_openai_api_key,
        api_version=s.azure_openai_api_version,
    )

def build_kernel() -> Kernel:
    kernel = Kernel()
    kernel.add_service(azure_chat())
    return kernel