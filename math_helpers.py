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


def angle_between_vectors_radian(vec1: Vec2d, vec2: Vec2d):
    angle = pygame.math.Vector2(vec1.x, vec1.y).angle_to((vec2))
    return math.radians(angle)
