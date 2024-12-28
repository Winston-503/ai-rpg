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
- OpenAI API key

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

- `llm-config.yaml`: LLM model settings including model selection and temperature. Support all
  models [supported by Council](https://council.dev/en/stable/reference/llm/llm_config_object.html#council.llm.LLMConfigObject).

## Usage

Run the game:

```bash
python main.py
```

For a more manual approach, you can run any of `tests/test_x_generation.py` to test the generation of a specific type of content for your input. 
This will produce a file in the `data/generation` directory that you can review and refine as needed and then use in the main configuration.

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
