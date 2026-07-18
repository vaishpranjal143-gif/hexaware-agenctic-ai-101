import gradio as gr
from chatbot import get_response #type: ignore

def chat_interface(message, history):
    return get_response(message) #type: ignore


demo = gr.ChatInterface(
    fn=chat_interface,
    title="Caramel AI - Your Personal Chatbot with Memory",
    description="Chat with Caramel AI")

if __name__ == "__main__":
    demo.launch()