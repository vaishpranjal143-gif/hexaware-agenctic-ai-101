import gradio as gr
from chatbot import MODEL, ask, new_session

def respond(message: str, history: list, session: dict):
    reply, report = ask(message, history or [], session)
    history = (history or []) + [{"role": "user", "content": message},
                                 {"role": "assistant", "content": reply}]
    return history, "", report, session

with gr.Blocks(title="Observable Chatbot - powered by Ollama Cloud") as demo:
    gr.Markdown(f"# Meridian Bank Assistant\n `{MODEL}` on Ollama Cloud | "
                "one turn = one trace | one conversation = one session")

    session = gr.State(new_session)

    with gr.Row():
        with gr.Column(scale=3):
            chat = gr.Chatbot(height=420, label="Chat")
            box = gr.Textbox(placeholder="What's the balance on SB-9001?", show_label=False, submit_btn=True)
            gr.Examples(["What's the balance on SB-9001?",
                         "What are your Saturday timings?",
                         "And SB-9003"], inputs=box)

        with gr.Column(scale=2):
            gr.Markdown("### What that took")
            report = gr.Markdown("_Send a message_")
            gr.Markdown("Open the trace. A balance question made **two** model calls: "
                        "one to pick the tool, one to answer from its result." \
                        "The second prompt is bigger - it carries the tool's output." \
                        "A trace in one turnm, so it can only every show one turn's tokens." \
                        "For the conversation's total, follow **the whole conversation** link into" \
                        "Tracing > Sessions - every turn is tagged with the same session id and" \
                        "Langfuse adds them up."
                        )
    box.submit(respond, [box, chat, session], [chat, box, report, session])

    if __name__ == "__main__":
        demo.launch()