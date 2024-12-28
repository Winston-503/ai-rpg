import dotenv

from ai_rpg.generators import generate_inventory
from ai_rpg.utils import read_generation

if __name__ == "__main__":
    dotenv.load_dotenv()
    story_filename = "story_example.md"
    generate_inventory(read_generation(story_filename))
