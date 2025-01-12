from datetime import datetime
from typing import Dict, List

from council.llm import LLMFunction, LLMFunctionResponse, LLMMessage, YAMLBlockResponseParser
from pydantic import Field

from .config import AIRPGConfig
from .dice import DiceRoller
from .generators import generate_inventory, generate_story, generate_world
from .ui import start_game_ui
from .utils import get_llm_function, get_prompt, read_generation, save_generation


class InventoryChange(YAMLBlockResponseParser):
    """Single change to an item in the player's inventory."""

    _name_description = "\n".join(
        [
            "Name of the item to change.",
            "Make sure it's a valid item name, especially if you're responding in a language other than English.",
        ]
    )
    name: str = Field(..., description=_name_description)
    amount: int = Field(..., description="Change amount, e.g. +1, -5 etc.")


class AIRPGResponse(YAMLBlockResponseParser):
    """AI's response to a player's action."""

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


class Inventory:
    """Manages the player's in-game inventory."""

    def __init__(self, items: Dict[str, int]):
        self._items = items.copy()

    @property
    def items(self) -> Dict[str, int]:
        return self._items

    def update(self, changes: List[InventoryChange]) -> None:
        """Update the inventory items based on the list of InventoryChange objects."""
        for inventory_change in changes:
            if inventory_change.name not in self.items:
                self.items[inventory_change.name] = 0
            self.items[inventory_change.name] += inventory_change.amount

    def format(self) -> str:
        """String representation of the inventory contents."""

        if not self.items:
            return "Inventory is empty."
        return "\n".join(["Inventory content:", *[f"- {item}: {amount}" for item, amount in self._items.items()]])

    @staticmethod
    def format_changes(changes: List[InventoryChange]) -> str:
        """Format a sequence of inventory changes as a string."""

        if not changes:
            return ""
        return "\n".join(
            [
                "Your inventory has changed:",
                *[f"- {change.name}: {change.amount:+d}" for change in changes],
            ]
        )


class AIRPG:
    """
    The main AI RPG class which ties together world/story generation, inventory management,
    and the interactive game loop.
    """

    MAIN_PROMPT_FILENAME = "ai-game-master.yaml"
    STARTING_MESSAGE_PROMPT_FILENAME = "starting-message.yaml"

    def __init__(self, game_config: AIRPGConfig):
        """Initialize the AI RPG with a given configuration."""

        self.config = game_config
        self.user_prompt_template = self._load_user_prompt_template()
        self.total_cost = 0.0
        self.language_instructions = f"- Respond in {self.config.language}" if self.config.language is not None else ""
        self.dice_roller = DiceRoller(
            num_dice=self.config.difficulty.number_of_dice,
            aggregation=self.config.difficulty.dice_combine_method,
        )

        self.world_description = self._load_world()
        self.story = self._load_story()
        self.starting_inventory = self._load_inventory()
        self.inventory = Inventory(self.starting_inventory)

        self.game_loop_llm_func = self._load_main_llm_function()
        self.starting_message_llm_func = self._load_starting_message_llm_function()

    def _load_world(self) -> str:
        """Load or generate the world description."""
        if self.config.generation.world is not None and self.config.generation.world.endswith(".md"):
            return read_generation(self.config.generation.world)

        return generate_world(self.config.generation.world or "")

    def _load_story(self) -> str:
        """Load or generate the story based on the world description."""
        if self.config.generation.story is not None:
            return read_generation(self.config.generation.story)

        return generate_story(self.world_description)

    def _load_inventory(self) -> Dict[str, int]:
        """Load or generate the character's starting inventory based on the story."""
        if self.config.generation.starting_inventory is not None:
            return read_generation(self.config.generation.starting_inventory)

        return generate_inventory(self.story)

    def _load_main_llm_function(self) -> LLMFunction[AIRPGResponse]:
        """Prepare the main LLM function for the game loop interactions."""

        return get_llm_function(
            prompt_filename=self.MAIN_PROMPT_FILENAME,
            response_parser=AIRPGResponse.from_response,
            dice_legend=self.config.difficulty.dice_legend,
            world_description=self.world_description,
            story=self.story,
            inventory=self.inventory.format(),
            language_instructions=self.language_instructions,
            response_template=AIRPGResponse.to_response_template(),
        )

    def _load_starting_message_llm_function(self) -> LLMFunction[str]:
        """Prepare an LLM function to generate the starting message for the game."""

        return get_llm_function(
            prompt_filename=self.STARTING_MESSAGE_PROMPT_FILENAME,
            world_description=self.world_description,
            story=self.story,
            inventory=self.inventory.format(),
            language_instructions=self.language_instructions,
        )

    def _load_user_prompt_template(self) -> str:
        """Load the user prompt template from a YAML-based prompt config file."""
        prompt = get_prompt(self.MAIN_PROMPT_FILENAME)
        return prompt.get_user_prompt_template("default")  # pylint: disable=no-member

    @staticmethod
    def _history_to_messages(history: List[List[str]]) -> List[LLMMessage]:
        """Convert a Gradio-style chat history into a list of LLMMessage objects."""
        messages = []
        for action in history:
            # None checks to handle first assistant message without the user input
            if action[0] is not None:
                messages.append(LLMMessage.user_message(action[0]))
            if action[1] is not None:
                messages.append(LLMMessage.assistant_message(action[1]))

        return messages

    def generate_starting_message(self) -> str:
        """Generate the first greeting/intro message for the player."""
        llm_response = self.starting_message_llm_func.execute_with_llm_response()
        self.track_cost(llm_response)
        return llm_response.response

    def track_cost(self, llm_response: LLMFunctionResponse) -> None:
        """Accumulate token cost from the LLM response into self.total_cost if this information is available."""

        for consumption in llm_response.consumptions:
            if consumption.kind.endswith("total_tokens_cost"):
                self.total_cost += consumption.value
                return

    def save_game_state(self, history: List[List[str]]) -> str:
        """Save the current game state into a YAML file."""

        game_state = {
            "timestamp": datetime.now().isoformat(),
            "total_cost": self.total_cost,
            "world_description": self.world_description,
            "story": self.story,
            "starting_inventory": self.starting_inventory,
            "history": [
                {"role": message.role.value, "content": message.content}
                for message in self._history_to_messages(history)
            ],
        }

        filename = save_generation(content=game_state, prefix="game_state_")

        return f"Game state saved to {filename}!\nTotal cost: ${self.total_cost:.4f}"

    @staticmethod
    def format_response(roll: int, llm_response: str, inventory_changes: List[InventoryChange]) -> str:
        """Format the final text response for the user, including dice roll info and inventory changes."""

        response_parts = [f"You roll {roll}.", llm_response, ""]

        if inventory_changes:
            response_parts.append(Inventory.format_changes(inventory_changes))

        return "\n".join(response_parts)

    def game_loop(self, message: str, history: List[List[str]]) -> str:
        """
        The main game loop function.
        Processes the user's action, obtains the AI's response, and updates the inventory accordingly.

        Compatible with Gradio's ChatInterface signature.
        """

        if message == "/inventory":
            return self.inventory.format()
        elif message == "/save":
            return self.save_game_state(history)

        messages = self._history_to_messages(history)

        roll = self.dice_roller.roll_dice()
        user_message = LLMMessage.user_message(self.user_prompt_template.format(roll=roll, action=message))
        messages.append(user_message)

        llm_response = self.game_loop_llm_func.execute_with_llm_response(messages=messages)
        response = llm_response.response

        self.inventory.update(response.inventory_changes)
        self.track_cost(llm_response)

        return self.format_response(roll, response.message, response.inventory_changes)

    def run(self):
        """
        Entry point for running the entire game in a Gradio UI loop.
        Generates the starting message and then calls the Gradio UI function to begin interactive play.
        """

        print("Generating the starting message...")
        starting_message = self.generate_starting_message()

        print("Running the UI...")
        start_game_ui(self.game_loop, greeting_message=starting_message)
