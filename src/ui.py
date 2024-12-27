from typing import Callable, List, Optional

import gradio as gr  # type: ignore


def start_game_ui(main_loop: Callable, greeting_message: Optional[str] = None, share=False):
    demo = gr.ChatInterface(
        main_loop,
        chatbot=gr.Chatbot(value=[[None, greeting_message]], placeholder="The story begins... "),
        textbox=gr.Textbox(placeholder="What do you do next?", container=False, scale=8),
        title="AI RPG",
        theme="soft",
        cache_examples=False,
        retry_btn="Retry",
        undo_btn="Undo",
        clear_btn="Clear",
    )
    demo.launch(share=share, server_name="localhost")


def test_main_loop(message: str, history: List[List[str]]) -> str:
    history_str = "\n".join([f"User: {h[0]}\nAssistant: {h[1]}" for h in history])
    return f"History:\n{history_str}\n---\nEntered Action: {message}"


if __name__ == "__main__":
    start_game_ui(test_main_loop)
