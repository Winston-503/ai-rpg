from typing import Callable, Optional

import gradio as gr  # type: ignore


def start_game_ui(main_loop: Callable, greeting_message: Optional[str] = None, share=False):
    demo = gr.ChatInterface(
        main_loop,
        chatbot=gr.Chatbot(value=[[None, greeting_message]], placeholder="The story begins... "),
        textbox=gr.Textbox(placeholder="What do you do next?", container=False, scale=8),
        title="AI RPG",
        theme="soft",
        examples=["/Explore inventory", "Look around"],
        cache_examples=False,
        retry_btn="Retry",
        undo_btn="Undo",
        clear_btn="Clear",
    )
    demo.launch(share=share, server_name="localhost")
