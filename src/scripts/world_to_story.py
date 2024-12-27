import dotenv

from src.utils import format_duration_and_cost, get_llm_function, read_generation, save_generation


def generate_story(world_description: str) -> str:
    """Generate a story based on a world description."""
    llm_func = get_llm_function("story-generation.yaml")
    print("Generating main character and story...")

    llm_response = llm_func.execute_with_llm_response(user_message=world_description)
    story = llm_response.response

    print(f"Generated story {format_duration_and_cost(llm_response)}")
    save_generation(content=story, prefix="story_")

    return story


if __name__ == "__main__":
    dotenv.load_dotenv()
    world_filename = "world_example.md"
    generate_story(read_generation(world_filename))
