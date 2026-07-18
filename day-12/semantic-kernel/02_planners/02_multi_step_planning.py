import asyncio
from semantic_kernel.functions import kernel_function, KernelArguments
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings
from _setup import build_kernel

class CurrencyPlugin:
    @kernel_function(description="Get the exchange rate for a currency")
    def get_rate(self, from_currency: str, to_currency: str) -> float:
        return 95.33 if (from_currency.upper(), to_currency.upper()) == ("USD", "INR") else 1.0

    @kernel_function(description="Convert an amount from one currency to another")
    def convert(self, amount: float, rate: float) -> float:
        return round(amount * rate, 2)
    
async def main():
    kernel = build_kernel()
    kernel.add_plugin(CurrencyPlugin(), "Currency")
    settings = AzureChatPromptExecutionSettings()
    settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
    answer = await kernel.invoke_prompt("Convert 100 USD to INR", arguments=KernelArguments(settings=settings)
    )
    print(answer)

asyncio.run(main())