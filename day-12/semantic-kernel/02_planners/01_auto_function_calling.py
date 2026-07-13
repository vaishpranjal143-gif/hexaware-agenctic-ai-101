import asyncio
from semantic_kernel.functions import kernel_function, KernelArguments
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings
from _setup import build_kernel

class InventoryPlugin:
    @kernel_function(description="How many units of a product are in stock")
    def get_stock(self, product: str) -> str:
        stock = {"red shirt": 3, "blue jeans": 0}
        return str(stock.get(product.lower(), 0))
    
async def main():
    kernel = build_kernel()
    kernel.add_plugin(InventoryPlugin(), "Inventory")
    settings = AzureChatPromptExecutionSettings()
    settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
    answer = await kernel.invoke_prompt(
        "Any red blue jeans left in stock?",
        arguments=KernelArguments(settings=settings),
    )
    print(answer)

asyncio.run(main())