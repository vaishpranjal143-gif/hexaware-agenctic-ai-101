import json
from pathlib import Path

current_dir = Path(__file__).parent
config_file = current_dir / "config.json"

with open(config_file, "r") as file:
    config = json.load(file)

print("Model: ", config["model"])
print("Temperature: ", config["temperature"])
print("Max Tokens: ", config["max_tokens"])

print("\nCalling AI Model...")
print(f"Using {config['model']} with temperature {config['temperature']}")