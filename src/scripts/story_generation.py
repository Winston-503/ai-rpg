import dotenv

from src.utils import format_duration_and_cost, get_llm_function, read_from_data, save_generation

if __name__ == "__main__":
    dotenv.load_dotenv()
    llm_func = get_llm_function("story-generation.yaml")

    world_filename = "world_example.md"
    print(f"Generating main character and story for {world_filename}...")

    llm_response = llm_func.execute_with_llm_response(user_message=read_from_data(world_filename))
    story = llm_response.response

    print(f"Generated story {format_duration_and_cost(llm_response)}")

    save_generation(content=story, prefix="story_")
