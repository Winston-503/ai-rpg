import random


class DiceRoller:
    """A class for simulating dice rolls in D&D."""

    def __init__(self, num_dice: int = 1, aggregation: str = "avg", sides: int = 20):
        self.num_dice = num_dice
        self.aggregation = aggregation
        self.sides = sides

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
        if self.aggregation == "avg":
            return round(sum(rolls) / self.num_dice)
        elif self.aggregation == "min":
            return min(rolls)
        elif self.aggregation == "max":
            return max(rolls)
        else:
            raise ValueError(f"Invalid aggregation method: {self.aggregation}")
