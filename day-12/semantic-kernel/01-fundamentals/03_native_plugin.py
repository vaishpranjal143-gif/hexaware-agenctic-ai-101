import asyncio
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function

class MathPlugin:
    @kernel_function(description="Add two numbers")
    def add(self, a: int, b: int) -> int:
        return a + b
    
async def main():
    kernel = Kernel()
    kernel.add_plugin(MathPlugin(), "Math")
    result = await kernel.invoke(plugin_name="Math", function_name="add", a=2, b=40)
    print(result)

asyncio.run(main())