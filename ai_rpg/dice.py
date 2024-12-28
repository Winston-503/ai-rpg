import random


class DiceRoller:
    """A class for simulating dice rolls in D&D."""

    def __init__(self, dice: int = 1, aggregation: str = "avg", sides: int = 20):
        self.dice = dice
        self.aggregation = aggregation
        self.sides = sides

    def _roll_die(self) -> int:
        """Simulates rolling a die, e.g., a d20, in D&D."""
        return random.randint(1, self.sides)

    def roll_dice(self) -> int:
        """Simulates rolling multiple dice, e.g., 2d20, in D&D."""
        rolls = [self._roll_die() for _ in range(self.dice)]
        if self.aggregation == "avg":
            return round(sum(rolls) / self.dice)
        elif self.aggregation == "min":
            return min(rolls)
        elif self.aggregation == "max":
            return max(rolls)
        else:
            raise ValueError(f"Invalid aggregation method: {self.aggregation}")
