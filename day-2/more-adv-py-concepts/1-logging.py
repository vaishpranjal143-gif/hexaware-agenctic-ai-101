import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def ask_ai(question):
    logging.info("Question received")
    logging.info(f"Question: {question}")
    logging.info("Calling AI model")

    # Simulating LLM processing
    response = f"AI Response for: {question}"
    logging.info("Response generated")
    return response

# Application
question = "What is Artificial Intelligence?"
answer = ask_ai(question)
logging.info(f"Final Answer: {answer}")