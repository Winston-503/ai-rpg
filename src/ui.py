from typing import Callable, List

import gradio as gr  # type: ignore

from src.main import main_loop


def start_game_ui(main_loop: Callable, share=False):
    demo = gr.ChatInterface(
        main_loop,
        chatbot=gr.Chatbot(placeholder="The story begins... "),
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
    return "Entered Action: " + message


if __name__ == "__main__":
    start_game_ui(main_loop)
