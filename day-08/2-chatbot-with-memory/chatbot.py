import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), #type: ignore
)

model = os.getenv("AZURE_OPENAI_MODEL") #type: ignore

context = ""

def get_response(user_input):
    global context
    context += f"User: {user_input}\n"
    response = client.chat.completions.create(
        model=model, #type: ignore
        messages=[{"role": "user", "content": context}])
    reply = response.choices[0].message.content
    context += f"Caramel AI: {reply}\n"
    return reply

if __name__ == "__main__":
    print("Caramel AI - Your Personal Chatbot with Memory")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Exiting Caramel AI. Goodbye!")
            break
        reply = get_response(user_input)
        print("Caramel AI:", reply)
        print()
