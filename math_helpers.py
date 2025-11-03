import math
import pygame
from pymunk import Vec2d


def clamp(value, minimum, maximum):
    # Check types
    if not isinstance(value, (float, int)):
        raise TypeError(
            f"value in clamp function should be float or int, but is {type(value)}"
        )

    # Validate thresholds
    if minimum > maximum:
        raise ValueError(
            f"Minimum threshold ({minimum}) cannot be greater than maximum threshold ({maximum})"
        )

    # Perform clamping
    return max(min(value, maximum), minimum)


def angle_from_vertical(vector: Vec2d) -> float:
    """Calculate the angle in radians between the given vector and the vertical axis.

    Args:
        vector (Vec2d): The input vector.
    Returns:
        float: The angle in radians between the vector and the vertical axis.
    """
    angle = -pygame.math.Vector2(vector.x, vector.y).angle_to((0, 1))
    return math.radians(angle)
