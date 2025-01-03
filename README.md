# AI RPG 🤖⚔️

An AI-powered text adventure game that uses LLM to create dynamic, interactive storytelling experiences.

## Features

- Dynamic world & story & character generation
- Interactive storytelling that adapts to player choices
- Dice-based action resolution
- Inventory management system
- Configurable difficulty settings
- Support for any language the configured LLM can speak

## Prerequisites

- Python 3.12 or higher
- OpenAI API key by default (could use other LLM providers)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/ai-rpg.git
cd ai-rpg
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
cp .env.example .env
```

Edit `.env` to add your [OpenAI API key](https://platform.openai.com/api-keys):

```
OPENAI_API_KEY=your_api_key_here
```

## Configuration

The game can be configured through YAML files in the `data/config` directory:

- `ai-rpg-config.yaml`: main game settings, including:
    - World generation options
    - Story generation options
    - Starting inventory
    - Difficulty settings
    - Response language

- `llm-config.yaml`: LLM model settings including model selection and temperature. Support all models [supported by Council](https://council.dev/en/stable/reference/llm/llm_config_object.html#council.llm.LLMConfigObject).

## Usage

Run the game:

```bash
python main.py
```

### Commands

During gameplay, you can use special commands prefixed with `/`:

- `/inventory`: Check your current inventory
- `/save`: Save the current game state and show the total cost

Any other input will be treated as an action for your character to perform in the game world.

### Manual Generation

For a more manual approach, you can run any of `tests/test_x_generation.py` to test the generation of a specific type of content for your input. 
This will produce a file in the `data/generation` directory that you can review and refine as needed and then use in the main configuration.

Example workflow:
1. Generate a custom world:
   ```bash
   python tests/test_world_generation.py
   ```
2. Review and edit the generated file in `data/generation/world_*.md`
3. Pass the filename to the `tests/test_story_generation.py` script to generate a story for your world and then pass the story filename to the `tests/test_starting_inventory_generation.py` script to generate a starting inventory for your character.
4. Update `ai-rpg-config.yaml` to use your custom world:
   ```yaml
   generation:
     world: world_2025-01-01_revised.md
     story: story_2025-01-01_revised.md
     starting_inventory: starting_inventory_2025-01-01_revised.yaml
   ```
5. Run the game with your custom content:
   ```bash
   python main.py
   ```

## Next Steps

- Add attributes such as health and max number of actions similar to inventory management system
   - Could be also generated dynamically, e.g. mana for wizards, stamina for warriors, etc.
- Add image generation (ideally "native" with gemini-2.0) & video generation potentially

## Development

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Available make commands:

- `make lint`: Check code formatting and linting
- `make dev-lint`: Format and lint code with fixes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run linting
5. Submit a pull request

## Acknowledgments

- Inspired by [Building an AI-Powered Game course](https://www.deeplearning.ai/short-courses/building-an-ai-powered-game/) by DeepLearning.AI, Together AI and AI Dungeon
- Build with [Council](https://github.com/chain-ml/council)
