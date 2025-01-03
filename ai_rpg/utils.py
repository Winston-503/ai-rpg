import os
from datetime import datetime
from typing import Any, Final, Optional

import yaml
from council.llm import (
    LLMBase,
    LLMFileLoggingMiddleware,
    LLMFunction,
    LLMFunctionResponse,
    LLMLoggingStrategy,
    LLMMiddlewareChain,
    StringResponseParser,
    get_llm_from_config,
)
from council.llm.llm_function.llm_response_parser import LLMResponseParser
from council.prompt import LLMPromptConfigObject

# Base paths
BASE_PATH: Final[str] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA_PATH: Final[str] = os.path.join(BASE_PATH, "data")

# Data subdirectories
CONFIG_PATH: Final[str] = os.path.join(DATA_PATH, "config")
PROMPTS_PATH: Final[str] = os.path.join(DATA_PATH, "prompts")
GENERATION_PATH: Final[str] = os.path.join(DATA_PATH, "generation")

# Log directory
LOGS_PATH: Final[str] = os.path.join(BASE_PATH, "logs")

# Config files
LLM_CONFIG_PATH: Final[str] = os.path.join(CONFIG_PATH, "llm-config.yaml")
AI_RPG_CONFIG_PATH: Final[str] = os.path.join(CONFIG_PATH, "ai-rpg-config.yaml")


def get_llm() -> LLMBase:
    return get_llm_from_config(LLM_CONFIG_PATH)


def get_llm_with_logging() -> LLMMiddlewareChain:
    return LLMMiddlewareChain(
        llm=get_llm(),
        middlewares=[
            LLMFileLoggingMiddleware(
                log_file=os.path.join(LOGS_PATH, f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"),
                strategy=LLMLoggingStrategy.VerboseWithConsumptions,
            )
        ],
    )


def get_prompt(filename: str) -> LLMPromptConfigObject:
    return LLMPromptConfigObject.from_yaml(os.path.join(PROMPTS_PATH, filename))


def get_llm_function(
    prompt_filename: str, response_parser: Optional[LLMResponseParser] = None, **kwargs
) -> LLMFunction:
    prompt = get_prompt(prompt_filename)
    system_prompt_template = prompt.get_system_prompt_template("default")  # pylint: disable=no-member
    parser = response_parser or StringResponseParser.from_response
    return LLMFunction(
        llm=get_llm_with_logging(),
        response_parser=parser,
        system_message=system_prompt_template.format(**kwargs),
    )


def format_duration_and_cost(llm_response: LLMFunctionResponse) -> str:
    message = f"in {llm_response.duration:.2f} seconds"
    for consumption in llm_response.consumptions:
        if consumption.kind.endswith("total_tokens_cost"):
            message += f" for ${consumption.value:.8f}"
            break

    return message


def save_str(*, content: str, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def save_yaml(*, content: Any, path: str) -> None:
    class CustomDumper(yaml.Dumper):
        def represent_scalar(self, tag, value, style=None):
            if isinstance(value, str) and "\n" in value:
                style = "|"
            return super().represent_scalar(tag, value, style)

    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(content, f, sort_keys=False, default_flow_style=False, allow_unicode=True, Dumper=CustomDumper)


def save_generation(*, content: Any, prefix: str) -> str:
    """Save a generation to a file, either as a markdown or a yaml."""

    filename_without_extension = f"{prefix}{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    if isinstance(content, str):
        filename = f"{filename_without_extension}.md"
        save_str(content=content, path=os.path.join(GENERATION_PATH, filename))
    else:
        filename = f"{filename_without_extension}.yaml"
        save_yaml(content=content, path=os.path.join(GENERATION_PATH, filename))

    print(f"\nSaved into {filename}")
    return filename


def read_generation(filename: str) -> Any:
    """Read generated content."""
    path = os.path.join(GENERATION_PATH, filename)
    with open(path, "r", encoding="utf-8") as f:
        if filename.endswith(".yaml"):
            return yaml.safe_load(f)
        return f.read()
