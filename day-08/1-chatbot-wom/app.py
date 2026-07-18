import gradio as gr
from chatbot import get_response

def chat_interface(message, history):
    return get_response(message)

demo = gr.ChatInterface(
    fn=chat_interface,
    title="Caramel AI - Your Personal Chatbot",
    description="Chat with Caramel AI"
) # type: ignore

if __name__ == "__main__":
    demo.launch()