from typing import List

import dotenv
from council.llm import LLMMessage

from src.utils import get_llm_function, history_to_messages, read_generation, roll_dice

dotenv.load_dotenv()

# TODO: first AI message as introduction

# TODO: hardcoded
world_description = read_generation("world_example.md")
story = read_generation("story_example.md")

USER_PROMPT_TEMPLATE = """
# Roll

{roll}

# Action

{action}
"""


def main_loop(message: str, history: List[List[str]]) -> str:
    messages = history_to_messages(history)

    llm_func = get_llm_function("ai-game-master.yaml", world_description=world_description, story=story)

    roll = roll_dice()
    user_message = LLMMessage.user_message(USER_PROMPT_TEMPLATE.format(roll=roll, action=message))
    messages.append(user_message)
    result = llm_func.execute(messages=messages)

    return f"You roll {roll}.\n{result}"
