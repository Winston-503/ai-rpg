from dataclasses import dataclass
from typing import Optional

import yaml

from .utils import AI_RPG_CONFIG_PATH


@dataclass
class GenerationConfig:
    world: Optional[str]
    story: Optional[str]
    starting_inventory: Optional[str]

    @classmethod
    def from_yaml(cls, data: dict) -> "GenerationConfig":
        return cls(world=data["world"], story=data["story"], starting_inventory=data["starting_inventory"])


@dataclass
class DifficultyConfig:
    number_of_dice: int
    dice_combine_method: str
    dice_legend: str

    @classmethod
    def from_yaml(cls, data: dict) -> "DifficultyConfig":
        return cls(
            number_of_dice=data["number_of_dice"],
            dice_combine_method=data["dice_combine_method"],
            dice_legend=data["dice_legend"],
        )


@dataclass
class AIRPGConfig:
    """Main configuration object for the AI RPG."""

    generation: GenerationConfig
    difficulty: DifficultyConfig
    language: Optional[str]

    @classmethod
    def from_yaml(cls, path: str) -> "AIRPGConfig":
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        generation = GenerationConfig.from_yaml(data["generation"])
        difficulty = DifficultyConfig.from_yaml(data["difficulty"])
        language = data.get("language", None)

        return cls(generation=generation, difficulty=difficulty, language=language)

    @classmethod
    def load(cls) -> "AIRPGConfig":
        """Load config from default location"""
        return cls.from_yaml(AI_RPG_CONFIG_PATH)
