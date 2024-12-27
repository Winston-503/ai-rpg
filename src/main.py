from typing import List

import dotenv

from src.utils import history_to_messages, get_llm_function, read_from_data

dotenv.load_dotenv()


world_description = read_from_data("world_example.md")
story = read_from_data("story_example.md")


def main_loop(message: str, history: List[List[str]]) -> str:
    messages = history_to_messages(message, history)

    llm_func = get_llm_function("ai-game-master.yaml", world_description=world_description, story=story)

    result = llm_func.execute(messages=messages)

    return result
