from typing import List

import dotenv

from src.utils import get_llm_function, history_to_messages, read_generation

dotenv.load_dotenv()


# TODO: hardcoded
world_description = read_generation("world_example.md")
story = read_generation("story_example.md")


def main_loop(message: str, history: List[List[str]]) -> str:
    messages = history_to_messages(message, history)

    llm_func = get_llm_function("ai-game-master.yaml", world_description=world_description, story=story)

    result = llm_func.execute(messages=messages)

    return result
