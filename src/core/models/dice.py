import random
import re
from typing import Union


def roll_dice(notation: str) -> int:
    """
    Roll dice based on the given notation string (e.g., '2d6+3', '1d20', '3d6*2').

    Args:
        notation (str): Dice notation in the format 'NdX[+/-/*//M]' where:
            - N is the number of dice to roll
            - X is the number of sides on each die
            - M is an optional modifier (can be positive or negative)

    Returns:
        int: The result of the dice roll

    Raises:
        ValueError: If the notation is invalid
    """
    # Regular expression to match dice notation (e.g., 2d6+3, 1d20, 3d6*2)
    pattern = r'^(\d+)d(\d+)([+\-*/])?(\d+)?$'
    match = re.match(pattern, notation.lower())

    if not match:
        raise ValueError(f"Invalid dice notation: {notation}")

    num_dice = int(match.group(1))
    num_sides = int(match.group(2))
    operator = match.group(3)
    modifier = int(match.group(4)) if match.group(4) else 0

    # Roll the dice
    total = sum(random.randint(1, num_sides) for _ in range(num_dice))

    # Apply modifier if present
    if operator == '+':
        total += modifier
    elif operator == '-':
        total -= modifier
    elif operator == '*':
        total *= modifier
    elif operator == '/':
        total //= modifier  # Integer division

    return total


def roll_d20() -> int:
    """Roll a single 20-sided die."""
    return random.randint(1, 20)


def roll_d6() -> int:
    """Roll a single 6-sided die."""
    return random.randint(1, 6)


def roll_2d6() -> int:
    """Roll two 6-sided dice and return the sum."""
    return random.randint(1, 6) + random.randint(1, 6)
