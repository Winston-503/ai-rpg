from typing import List

from ai_rpg.ui import start_game_ui


def test_main_loop(message: str, history: List[List[str]]) -> str:
    history_str = "\n".join([f"User: {h[0]}\nAssistant: {h[1]}" for h in history])
    return f"History:\n{history_str}\n---\nEntered Action: {message}"


if __name__ == "__main__":
    start_game_ui(test_main_loop, greeting_message="Test greeting message")
