import dotenv

from src.utils import format_duration_and_cost, get_llm_function, save_generation


def generate_world_description(setting: str) -> str:
    """Generate a world description."""

    llm_func = get_llm_function("world-generation.yaml")
    print("Generating world description...")

    llm_response = llm_func.execute_with_llm_response(user_message=setting)
    world_description = llm_response.response

    print(f"Generated world description {format_duration_and_cost(llm_response)}")
    save_generation(content=world_description, prefix="world_")

    return world_description


if __name__ == "__main__":
    dotenv.load_dotenv()
    setting = input("Enter a setting for the world or keep empty: ")
    generate_world_description(setting)
