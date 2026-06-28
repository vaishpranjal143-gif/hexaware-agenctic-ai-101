import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), #type: ignore
)

model = os.getenv("AZURE_OPENAI_MODEL")

def get_response(user_input):
    reponse = client.chat.completions.create(
        model=model, #type: ignore
        messages=[{"role": "user", "content": user_input}])
    return reponse.choices[0].message.content

if __name__ == "__main__":
    print("Caramel AI - Your Personal Chatbot")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Exiting Caramel AI. Goodbye!")
            break
        reponse = get_response(user_input)
        print("Caramel AI:", reponse)
        print()