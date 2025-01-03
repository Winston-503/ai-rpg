import random
from typing import List


class DiceAggregator:
    """Handles aggregation of multiple dice rolls."""

    SUPPORTED_METHODS = {"avg", "min", "max"}

    def __init__(self, method: str):
        if method not in self.SUPPORTED_METHODS:
            raise ValueError(f"Invalid aggregation method: '{method}'. Must be one of {self.SUPPORTED_METHODS}")
        self.method = method

    def aggregate(self, rolls: List[int]) -> int:
        if self.method == "min":
            return min(rolls)
        elif self.method == "max":
            return max(rolls)

        return round(sum(rolls) / len(rolls))


class DiceRoller:
    """A class for simulating dice rolls in D&D."""

    def __init__(self, num_dice: int = 1, aggregation: str = "avg"):
        self.num_dice = num_dice
        self.aggregator = DiceAggregator(aggregation)
        self.sides = 20

    def _roll_die(self) -> int:
        """Simulate rolling a single die."""
        return random.randint(1, self.sides)

    def roll_dice(self) -> int:
        """
        Roll self.num_dice number of dice and combine the results.

        For example, if num_dice=2, it will roll 2d20 and then
        either take the average, the minimum, or the maximum depending on self.aggregation.
        """
        rolls = [self._roll_die() for _ in range(self.num_dice)]
        return self.aggregator.aggregate(rolls)
