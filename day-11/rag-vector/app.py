import gradio as gr
from chatbot import get_streaming_response
from rag_pipeline import DOCUMENT_PATH

def chat_interface(message, history):
    response_text = ""

    for kind, text in get_streaming_response(message):
        if kind == "response":
            response_text += text
            yield response_text

demo = gr.ChatInterface(
    fn=chat_interface,
    title="Caramel AI - RAG with Vector Store",
    description=f"Chat with the AI based on the content of the document located at: {DOCUMENT_PATH}",
)

if __name__ == "__main__":
    demo.launch()