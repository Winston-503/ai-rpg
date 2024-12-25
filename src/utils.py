import os
from datetime import datetime
from typing import Final, Optional

from council import OpenAILLM
from council.llm import (
    LLMBase,
    LLMFileLoggingMiddleware,
    LLMFunctionResponse,
    LLMFunctionWithPrompt,
    LLMLoggingStrategy,
    LLMMiddlewareChain,
    StringResponseParser,
)
from council.llm.llm_function.llm_response_parser import LLMResponseParser
from council.prompt import LLMPromptConfigObject
from council.utils import OsEnviron

BASE_PATH: Final[str] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA_PATH: Final[str] = os.path.join(BASE_PATH, "data")
LOGS_PATH: Final[str] = os.path.join(BASE_PATH, "logs")
PROMPTS_PATH: Final[str] = os.path.join(BASE_PATH, "prompts")


def get_llm() -> LLMBase:
    # gpt-4o-2024-08-06
    # gpt-4o-mini-2024-07-18
    with OsEnviron("OPENAI_LLM_MODEL", "gpt-4o-mini-2024-07-18"), OsEnviron("OPENAI_LLM_TEMPERATURE", "0.5"):
        return OpenAILLM.from_env()


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


def get_llm_function(prompt_path: str, response_parser: Optional[LLMResponseParser] = None) -> LLMFunctionWithPrompt:
    parser = response_parser or StringResponseParser.from_response
    return LLMFunctionWithPrompt(
        llm=get_llm_with_logging(),
        response_parser=parser,
        prompt_config=LLMPromptConfigObject.from_yaml(os.path.join(PROMPTS_PATH, prompt_path)),
    )


def format_duration_and_cost(llm_response: LLMFunctionResponse) -> str:
    message = f"in {llm_response.duration:.2f} seconds"
    for consumption in llm_response.consumptions:
        if consumption.kind.endswith("total_tokens_cost"):
            message += f" for ${consumption.value:.8f}"
            break

    return message


def save_generation(*, content: str, prefix: str) -> None:
    filename = f"{prefix}{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.md"
    path = os.path.join(DATA_PATH, filename)
    with open(path, "w") as f:
        f.write(content)
    print(f"Saved into {filename}")


def read_from_data(filename: str) -> str:
    path = os.path.join(DATA_PATH, filename)
    with open(path, "r") as f:
        return f.read()
