import gradio as gr
from chatbot import get_streaming_response, PDF_PATH

def chat_interface(message, history):
    response_text = ""

    for kind, text in get_streaming_response(message):
        if kind == "response":
            response_text += text
            yield response_text

demo = gr.ChatInterface(
    fn=chat_interface,
    title="Caramel AI - PDF Document RAG",
    description=f"Chat with the AI based on the content of the PDF document located at: {PDF_PATH}",
)

if __name__ == "__main__":
    demo.launch()