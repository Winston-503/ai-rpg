import dotenv

from src.utils import format_duration_and_cost, get_llm_function, save_generation

if __name__ == "__main__":
    dotenv.load_dotenv()
    llm_func = get_llm_function("world-generation.yaml")

    setting = input("Enter a setting for the world or keep empty: ")
    print("Generating world description...")

    llm_response = llm_func.execute_with_llm_response(user_message=setting)
    world_description = llm_response.response

    print(f"Generated world description {format_duration_and_cost(llm_response)}")

    save_generation(content=world_description, prefix="world_")
