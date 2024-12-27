from typing import Dict

import dotenv
from council.llm import JSONResponseParser, LLMParsingException
from pydantic import Field

from src.utils import format_duration_and_cost, get_llm_function, read_generation, save_generation


class InventoryResponse(JSONResponseParser):
    inventory: Dict[str, int] = Field(
        description="\n".join(
            [
                "Dict[str, int], the inventory of item names and their quantities.",
                "Do not include items with zero quantity.",
            ]
        )
    )

    def validator(self) -> None:
        has_non_string_items = any(not isinstance(item, str) for item in self.inventory.keys())
        has_non_int_quantities = any(not isinstance(quantity, int) for quantity in self.inventory.values())
        if has_non_string_items or has_non_int_quantities:
            raise LLMParsingException(
                "Inventory must contain only strings as item names and integers as item quantities"
            )

        if any(quantity <= 0 for quantity in self.inventory.values()):
            raise LLMParsingException("Inventory cannot contain items with zero or negative quantity")


def generate_inventory(story: str) -> Dict[str, int]:
    """Generate an initial inventory based on a story."""
    llm_func = get_llm_function(
        "inventory-generation.yaml",
        InventoryResponse.from_response,
        response_template=InventoryResponse.to_response_template(),
    )
    print("Generating initial inventory...")

    llm_response = llm_func.execute_with_llm_response(user_message=story, response_format={"type": "json_object"})
    inventory_response = llm_response.response
    inventory = inventory_response.inventory

    print(f"Generated inventory {format_duration_and_cost(llm_response)}")
    save_generation(content=inventory, prefix="inventory_")

    return inventory


if __name__ == "__main__":
    dotenv.load_dotenv()
    story_filename = "story_example.md"
    generate_inventory(read_generation(story_filename))
