from pymunk import Vec2d
import pygame
from dataclasses import dataclass


@dataclass
class VectorFieldVisualizationConfig:
    visualization_corner_a: Vec2d
    visualization_corner_b: Vec2d
    color: tuple
    grid_width: float


class VectorField2d:
    def __init__(self, map: callable, config: VectorFieldVisualizationConfig):
        self.map = map
        self.config = config

    def evaulate(self, position):
        if not isinstance(position, Vec2d):
            position = Vec2d(position)
        return self.map(position)

    def draw(self, screen, corner_a: Vec2d = None, corner_b: Vec2d = None):
        if corner_a is None:
            corner_a = self.config.visualization_corner_a
        if corner_b is None:
            corner_b = self.config.visualization_corner_b
        coverage_points = generate_grid_coverage(
            corner_a, corner_b, self.config.grid_width
        )
        for point in coverage_points:
            point = Vec2d(point[0], point[1])
            pos_start = point
            pos_end = point + self.map(point)
            draw_arrow(screen, pos_start, pos_end)


def generate_grid_coverage(start_pos, end_pos, grid_width):
    """
    Generate a list of grid positions covering a rectangular area.

    Args:
    - start_pos (tuple): Starting (x, y) coordinates of the rectangle
    - end_pos (tuple): Ending (x, y) coordinates of the rectangle
    - grid_width (float): Width of each grid cell

    Returns:
    - list of tuples: Grid positions covering the rectangle
    """
    # Ensure start and end positions are in the correct order
    min_x = min(start_pos[0], end_pos[0])
    max_x = max(start_pos[0], end_pos[0])
    min_y = min(start_pos[1], end_pos[1])
    max_y = max(start_pos[1], end_pos[1])

    # Generate grid positions
    grid_positions = []

    # Iterate through x and y with the specified grid width
    x = min_x
    while x <= max_x:
        y = min_y
        while y <= max_y:
            grid_positions.append((x, y))
            y += grid_width
        x += grid_width

    return grid_positions


def draw_arrow(screen, pos_start, pos_end, color=None, arrow_head_size=4) -> None:
    """
    Draw an arrow on a Pygame screen with a triangular arrowhead.

    Args:
    - screen: Pygame screen surface to draw on
    - pos_start: Starting point of the arrow
    - pos_end: Ending point of the arrow
    - color: Color of the arrow (default is green)
    - arrow_head_size: Size of the arrowhead (default is 10 pixels)
    """
    # Set default color if not provided
    if color is None:
        color = (0, 255, 0)

    # Draw the main line of the arrow
    pygame.draw.line(screen, color, pos_start, pos_end, 2)

    # Calculate the arrow direction
    arrow_vector = pos_end - pos_start

    # If the vector is too small, don't draw an arrowhead
    if arrow_vector.length < 1e-6:
        pygame.draw.circle(screen, (0, 255, 255), pos_start, 3)
        return

    # Normalize the arrow vector
    arrow_vector = arrow_vector.normalized()

    # Rotate vectors to create arrowhead sides
    arrow_rotation_amount = 30
    rotate_left = arrow_vector.rotated(-arrow_rotation_amount)
    rotate_right = arrow_vector.rotated(arrow_rotation_amount)

    # Calculate arrowhead points
    head_left = pos_end - rotate_left * arrow_head_size
    head_right = pos_end - rotate_right * arrow_head_size

    # Draw the arrowhead
    pygame.draw.polygon(screen, color, [pos_end, head_left, head_right])
