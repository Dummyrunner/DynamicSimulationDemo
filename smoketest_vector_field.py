from pymunk import Vec2d
from vector_field import VectorField2d, VectorFieldVisualizationConfig
import pygame


def cyclone_field(pos: Vec2d):
    x = pos.x - MAP_REFERENCE_POINT[0]
    y = pos.y - MAP_REFERENCE_POINT[1]
    pos = Vec2d(x, y)
    return Vec2d(SCALE * pos.y, SCALE * -pos.x)


pygame.init()
screen = pygame.display.set_mode((1200, 800))
pygame.display.set_caption("Vector field test")
SQUARE_LENGTH = 500
SCALE = 0.3
clock = pygame.time.Clock()
MAP_REFERENCE_POINT = (600, 400)

visu_config = VectorFieldVisualizationConfig(
    visualization_corner_a=Vec2d(200, 200),
    visualization_corner_b=Vec2d(200 + SQUARE_LENGTH, 200 + SQUARE_LENGTH),
    color=(200, 0, 200),
    grid_width=30,
)
vector_field = VectorField2d(cyclone_field, visu_config)

running = True
frame_counter = 0
while running:
    print("HI: ", frame_counter)
    screen.fill((255, 255, 255))
    vector_field.draw(screen)
    frame_counter += 1
    if frame_counter > 8e3:
        running = False
    pygame.display.flip()
