import dotenv

from ai_rpg.generators import generate_story
from ai_rpg.utils import read_generation

if __name__ == "__main__":
    dotenv.load_dotenv()
    world_filename = "world_example.md"
    generate_story(read_generation(world_filename))
