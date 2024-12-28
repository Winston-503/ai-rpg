import os
import random
from datetime import datetime
from typing import Any, Final, List, Optional

import yaml
from council.llm import (
    LLMBase,
    LLMFileLoggingMiddleware,
    LLMFunction,
    LLMFunctionResponse,
    LLMLoggingStrategy,
    LLMMessage,
    LLMMiddlewareChain,
    StringResponseParser,
    get_llm_from_config,
)
from council.llm.llm_function.llm_response_parser import LLMResponseParser
from council.prompt import LLMPromptConfigObject

BASE_PATH: Final[str] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA_PATH: Final[str] = os.path.join(BASE_PATH, "data")
LOGS_PATH: Final[str] = os.path.join(BASE_PATH, "logs")
PROMPTS_PATH: Final[str] = os.path.join(BASE_PATH, "prompts")
LLM_CONFIG_PATH: Final[str] = os.path.join(DATA_PATH, "llm-config.yaml")


def get_llm() -> LLMBase:
    return get_llm_from_config(LLM_CONFIG_PATH)


def get_llm_with_logging() -> LLMMiddlewareChain:
    llm_middleware = LLMMiddlewareChain(
        get_llm(),
        middlewares=[
            LLMFileLoggingMiddleware(
                log_file=os.path.join(LOGS_PATH, f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"),
                strategy=LLMLoggingStrategy.VerboseWithConsumptions,
            )
        ],
    )

    return llm_middleware


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
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(content, f)


def save_generation(*, content: Any, prefix: str) -> None:
    """Save a generation to a file, either as a markdown or a yaml."""

    filename_without_extension = f"{prefix}{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    if isinstance(content, str):
        filename = f"{filename_without_extension}.md"
        save_str(content=content, path=os.path.join(DATA_PATH, filename))
    else:
        filename = f"{filename_without_extension}.yaml"
        save_yaml(content=content, path=os.path.join(DATA_PATH, filename))

    print(f"\nSaved into {filename}")


def read_generation(filename: str) -> Any:
    """Read generated content."""
    path = os.path.join(DATA_PATH, filename)
    with open(path, "r", encoding="utf-8") as f:
        if filename.endswith(".yaml"):
            return yaml.safe_load(f)
        return f.read()


def history_to_messages(history: List[List[str]]) -> List[LLMMessage]:
    """Unwrap gradio's ChatInterface history and input message to List[LLMMessage]"""
    messages = []
    for action in history:
        messages.append(LLMMessage.user_message(action[0]))
        messages.append(LLMMessage.assistant_message(action[1]))

    return messages


def roll_die(sides: int = 20) -> int:
    """Simulates rolling a die, e.g., a d20, in D&D."""
    return random.randint(1, sides)


def roll_dice(dice: int = 1, aggregation: str = "avg", sides: int = 20) -> int:
    """Simulates rolling multiple dice, e.g., 2d20, in D&D."""
    rolls = [roll_die(sides) for _ in range(dice)]
    if aggregation == "avg":
        return round(sum(rolls) / dice)
    elif aggregation == "min":
        return min(rolls)
    elif aggregation == "max":
        return max(rolls)
    else:
        raise ValueError(f"Invalid aggregation method: {aggregation}")
