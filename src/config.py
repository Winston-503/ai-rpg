import os
from dataclasses import dataclass
from typing import Optional

import yaml

from src.utils import BASE_PATH


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
    generation: GenerationConfig
    difficulty: DifficultyConfig

    @classmethod
    def from_yaml(cls, path: str) -> "AIRPGConfig":
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        generation = GenerationConfig.from_yaml(data["generation"])
        difficulty = DifficultyConfig.from_yaml(data["difficulty"])

        return cls(generation=generation, difficulty=difficulty)

    @classmethod
    def load(cls) -> "AIRPGConfig":
        """Load config from default location"""
        return cls.from_yaml(os.path.join(BASE_PATH, "data", "config.yaml"))
