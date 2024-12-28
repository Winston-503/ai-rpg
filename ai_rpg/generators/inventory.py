from typing import Dict

from council.llm import JSONResponseParser, LLMParsingException
from pydantic import Field

from ..utils import format_duration_and_cost, get_llm_function, save_generation


class InventoryGenerationResponse(JSONResponseParser):
    inventory: Dict[str, int] = Field(
        description="\n".join(
            [
                "Dict[str, int], the inventory of item names and their quantities.",
                "Do not include items with zero quantity.",
            ]
        )
    )

    def validator(self) -> None:
        if any(quantity <= 0 for quantity in self.inventory.values()):
            raise LLMParsingException("Inventory cannot contain items with zero or negative quantity")


def generate_inventory(story: str) -> Dict[str, int]:
    """Generate an initial inventory based on a story."""
    llm_func = get_llm_function(
        "inventory-generation.yaml",
        InventoryGenerationResponse.from_response,
        response_template=InventoryGenerationResponse.to_response_template(),
    )
    print("Generating initial inventory...")

    llm_response = llm_func.execute_with_llm_response(user_message=story, response_format={"type": "json_object"})
    inventory_response = llm_response.response
    inventory = inventory_response.inventory

    print(f"Generated inventory {format_duration_and_cost(llm_response)}")
    save_generation(content=inventory, prefix="inventory_")

    return inventory
