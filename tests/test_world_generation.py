import dotenv

from ai_rpg.generators.world import generate_world

if __name__ == "__main__":
    dotenv.load_dotenv()
    setting = ""  # Enter a setting for the world or keep empty
    generate_world(setting)
