from dotenv import load_dotenv
from os import getenv
from langchain_cerebras import ChatCerebras
from system_prompt import system_prompt

load_dotenv()
llm = ChatCerebras(model=getenv("MODEL")) #type:ignore

context = f"System: {system_prompt}\n"

def get_response(user_input):
    global context
    context += f"User: {user_input}\n"
    response = llm.invoke(context)
    context += f"Caramel AI: {response.content}\n"
    return response.content

if __name__ == "__main__":
    print("Caramel AI - with system prompt")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Exiting Caramel AI. Goodbye!")
            break
        print("Caramel AI:", get_response(user_input), "\n")