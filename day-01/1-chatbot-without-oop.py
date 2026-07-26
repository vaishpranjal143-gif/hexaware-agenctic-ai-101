def chatbot(message):
    if "hello" in message.lower():
        return "Hi there!"
    elif "bye" in message.lower():
        return "Goodbye!"
    else:
        return "I don't understand."

# chatbot session
while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        break

    response = chatbot(user_input)
    print("Bot:", response)
print("Chatbot session ended.")