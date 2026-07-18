from semantic_kernel.functions import kernel_function
from _setup import build_kernel

class TimePlugin:
    @kernel_function(description="Today's date")
    def today(self) -> str:
        return "2024-06-12"
    
kernel = build_kernel()
kernel.add_plugin(TimePlugin(), "Time")

print("Registerd on this kernel: ")
for plugin_name, plugin in kernel.plugins.items():
    for fn_name in plugin.functions:
        print(f" {plugin_name}.{fn_name}")