from typing import Callable

import gradio as gr  # type: ignore
from gradio.components.chatbot import Message


def start_game_ui(main_loop: Callable, greeting_message: str, share=False):
    """Launch the Gradio chat interface."""

    demo = gr.ChatInterface(
        main_loop,
        chatbot=gr.Chatbot(
            value=[Message(role="assistant", content=greeting_message)],  # type: ignore
            placeholder="The story begins... ",
            type="messages",
        ),
        textbox=gr.Textbox(placeholder="What do you do next?", container=False, scale=8),
        title="AI RPG",
        theme="soft",
        examples=["Look around", "/inventory", "/save"],
        cache_examples=False,
    )
    demo.launch(share=share, server_name="localhost")
