def call_llm(prompt):
    if prompt == "":
        raise ValueError("Prompt cannot be empty")
    return f"Response for: {prompt}"

try:
    user_prompt = ""
    response = call_llm(user_prompt)
    print(response)

except ValueError as error:
    print("User Error:", error)

except Exception as error:
    print("Unexpected Error:", error)

finally:
    print("Request completed")