from typing import Dict, List

import dotenv
import yaml
from council.llm import LLMFunction, LLMMessage

from src.config import AIRPGConfig
from src.scripts.story_to_inventory import generate_inventory
from src.scripts.world_generation import generate_world_description
from src.scripts.world_to_story import generate_story
from src.ui import start_game_ui
from src.utils import get_llm_function, get_prompt, read_generation, roll_dice


class AIRPG:
    PROMPT_FILENAME = "ai-game-master.yaml"

    def __init__(self, game_config: AIRPGConfig):
        self.config = game_config
        self.user_prompt_template = self._load_user_prompt_template()

        self.world_description = self._load_world()
        self.story = self._load_story()
        self.inventory = self._load_inventory()

    def _load_world(self) -> str:
        if self.config.generation.world is not None and self.config.generation.world.endswith(".md"):
            return read_generation(self.config.generation.world)

        return generate_world_description(self.config.generation.world or "")

    def _load_story(self) -> str:
        if self.config.generation.story is not None:
            return read_generation(self.config.generation.story)

        return generate_story(self.world_description)

    def _load_inventory(self) -> Dict[str, int]:
        if self.config.generation.starting_inventory is not None:
            return read_generation(self.config.generation.starting_inventory)

        return generate_inventory(self.story)

    def _load_llm_function(self) -> LLMFunction:
        return get_llm_function(
            self.PROMPT_FILENAME,
            world_description=self.world_description,
            story=self.story,
            inventory=yaml.dump(self.inventory),
        )

    def _load_user_prompt_template(self) -> str:
        prompt = get_prompt(self.PROMPT_FILENAME)
        return prompt.get_user_prompt_template("default")  # pylint: disable=no-member

    @staticmethod
    def _history_to_messages(history: List[List[str]]) -> List[LLMMessage]:
        """Unwrap gradio's ChatInterface history and input message to List[LLMMessage]"""
        messages = []
        for action in history:
            messages.append(LLMMessage.user_message(action[0]))
            messages.append(LLMMessage.assistant_message(action[1]))

        return messages

    def game_loop(self, message: str, history: List[List[str]]) -> str:
        """Main game loop that processes player actions, compatible with gradio's chatbot."""
        llm_func = self._load_llm_function()

        messages = self._history_to_messages(history)

        roll = roll_dice(
            dice=self.config.difficulty.number_of_dice, aggregation=self.config.difficulty.dice_combine_method
        )

        user_message = LLMMessage.user_message(self.user_prompt_template.format(roll=roll, action=message))
        messages.append(user_message)
        result = llm_func.execute(messages=messages)

        return f"You roll {roll}.\n{result}"

    def run(self):
        # TODO: separate LLMFunction
        start_message = "The story begins..."
        start_game_ui(self.game_loop, greeting_message=start_message)


if __name__ == "__main__":
    dotenv.load_dotenv()
    config = AIRPGConfig.load()
    game = AIRPG(config)
    game.run()
