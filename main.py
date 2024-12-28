"""
The main entry point for the AI RPG.
Loads environment variables, configures the game, and starts the Gradio UI.
"""

import dotenv

from ai_rpg import AIRPG, AIRPGConfig

if __name__ == "__main__":
    dotenv.load_dotenv()
    config = AIRPGConfig.load()
    game = AIRPG(config)
    game.run()
