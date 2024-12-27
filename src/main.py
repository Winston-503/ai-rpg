from typing import Dict, List

import dotenv
import yaml
from council.llm import LLMFunction, LLMFunctionResponse, LLMMessage, YAMLBlockResponseParser
from pydantic import Field

from src.config import AIRPGConfig
from src.scripts.story_to_inventory import generate_inventory
from src.scripts.world_generation import generate_world_description
from src.scripts.world_to_story import generate_story
from src.ui import start_game_ui
from src.utils import get_llm_function, get_prompt, read_generation, roll_dice

# TODO: class Inventory; change(), format(), format_change()


class InventoryChange(YAMLBlockResponseParser):
    name: str = Field(..., description="Name of the item to change.")
    amount: int = Field(..., description="Change amount, e.g. +1, -5 etc.")


class AIRPGResponse(YAMLBlockResponseParser):
    _reasoning_description = "\n".join(
        [
            "Your reasoning about the current situation, player action and dice roll.",
            "It's private and will be not shown to the user.",
        ]
    )
    _message_description = "\n".join(
        [
            "Message,",
            "that will be shown to the user.",
        ]
    )

    reasoning: str = Field(..., description=_reasoning_description)
    inventory_changes: List[InventoryChange] = Field(..., description="List of inventory changes.")
    message: str = Field(..., description=_message_description)


class AIRPG:
    PROMPT_FILENAME = "ai-game-master.yaml"

    def __init__(self, game_config: AIRPGConfig):
        self.config = game_config
        self.user_prompt_template = self._load_user_prompt_template()
        self.total_cost = 0.0

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
        language_instructions = f"Respond in {self.config.language}" if self.config.language is not None else ""
        return get_llm_function(
            self.PROMPT_FILENAME,
            AIRPGResponse.from_response,
            dice_legend=self.config.difficulty.dice_legend,
            world_description=self.world_description,
            story=self.story,
            inventory=yaml.dump(self.inventory),
            language_instructions=language_instructions,
            response_template=AIRPGResponse.to_response_template(),
        )

    def _load_user_prompt_template(self) -> str:
        prompt = get_prompt(self.PROMPT_FILENAME)
        return prompt.get_user_prompt_template("default")  # pylint: disable=no-member

    @staticmethod
    def _history_to_messages(history: List[List[str]]) -> List[LLMMessage]:
        """Unwrap gradio's ChatInterface history and input message to List[LLMMessage]"""
        messages = []
        for action in history:
            if action[0] is not None:  # to handle first assistant message without the user input
                messages.append(LLMMessage.user_message(action[0]))
            messages.append(LLMMessage.assistant_message(action[1]))

        return messages

    def track_cost(self, llm_response: LLMFunctionResponse) -> None:
        for consumption in llm_response.consumptions:
            if consumption.kind.endswith("total_tokens_cost"):
                self.total_cost += consumption.value
                return

    def update_inventory(self, inventory_changes: List[InventoryChange]) -> None:
        for inventory_change in inventory_changes:
            if inventory_change.name not in self.inventory:
                self.inventory[inventory_change.name] = 0
            self.inventory[inventory_change.name] += inventory_change.amount

    @staticmethod
    def format_response(roll: int, llm_response: str, inventory_changes: List[InventoryChange]) -> str:
        response_parts = [f"You roll {roll}.", llm_response, ""]

        if inventory_changes:
            response_parts.extend(
                [
                    "Your inventory has changed:",
                    *[f"- {change.name}: {change.amount:+d}" for change in inventory_changes],
                ]
            )

        return "\n".join(response_parts)

    def game_loop(self, message: str, history: List[List[str]]) -> str:
        """Main game loop that processes player actions, compatible with gradio's chatbot."""
        if message == "/Explore inventory":
            return "\n".join(["Your inventory:", *[f"- {item}: {amount}" for item, amount in self.inventory.items()]])

        llm_func: LLMFunction[AIRPGResponse] = self._load_llm_function()

        messages = self._history_to_messages(history)

        roll = roll_dice(
            dice=self.config.difficulty.number_of_dice, aggregation=self.config.difficulty.dice_combine_method
        )

        user_message = LLMMessage.user_message(self.user_prompt_template.format(roll=roll, action=message))
        messages.append(user_message)
        llm_response = llm_func.execute_with_llm_response(messages=messages)
        response = llm_response.response

        self.update_inventory(response.inventory_changes)
        self.track_cost(llm_response)

        return self.format_response(roll, response.message, response.inventory_changes)

    def run(self):
        # TODO: separate LLMFunction
        start_message = "The story begins..."

        print("Running the UI...")
        start_game_ui(self.game_loop, greeting_message=start_message)


if __name__ == "__main__":
    dotenv.load_dotenv()
    config = AIRPGConfig.load()
    game = AIRPG(config)
    game.run()
