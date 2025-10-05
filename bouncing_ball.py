import pygame
import pymunk
import sys

# Initialize Pygame and Pymunk
pygame.init()
WIDTH = 1200
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball Simulation")

# Create a pymunk space
space = pymunk.Space()
space.gravity = (0, 900)  # Set gravity (y is positive downwards)

# Create the load
mass = 90
radius = 15
moment = pymunk.moment_for_circle(mass, 0, radius)
ball_body = pymunk.Body(mass, moment)
ball_body.position = (WIDTH // 2, HEIGHT * 0.75)  # Start position
ball_shape = pymunk.Circle(ball_body, radius)
ball_shape.elasticity = 0.95  # Make it bouncy
ball_shape.friction = 0.9
space.add(ball_body, ball_shape)

# Create the ground (static line)
bar_body = pymunk.Body(body_type=pymunk.Body.STATIC)
BAR_LEFT_Y = 0.1 * HEIGHT
BAR_RIGHT_Y = BAR_LEFT_Y
BAR_RIGHT_X = WIDTH - 50
BAR_LEFT_X = 50
bar_shape = pymunk.Segment(
    bar_body, (BAR_RIGHT_X, BAR_LEFT_Y), (BAR_RIGHT_X, BAR_RIGHT_Y), 5
)
bar_shape.elasticity = 0.95
bar_shape.friction = 0.9
space.add(bar_body, bar_shape)

# Create Runner
runner_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
CENTER_OF_BAR = ((BAR_RIGHT_X + BAR_LEFT_X) / 2, BAR_LEFT_Y + BAR_RIGHT_Y / 2)
RUNNER_WIDTH = 100
RUNNER_HEIGHT = 20
runner_body.position = CENTER_OF_BAR
runner_shape = pymunk.Poly(
    [(0, 0), (0, RUNNER_HEIGHT), (RUNNER_WIDTH, RUNNER_HEIGHT), (RUNNER_WIDTH)],
    transform=pymunk.Transform(tx=-0.5 * RUNNER_WIDTH, ty=-0.5 * RUNNER_HEIGHT),
    radius=2,
)
# Game loop
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Reset ball position on mouse click
            [mouse_position_x, mouse_position_y] = pygame.mouse.get_pos()
            ball_body.position = (mouse_position_x, mouse_position_y)
            ball_body.velocity = (0, 0)

    # Update physics
    space.step(1 / 60.0)

    # Draw everything
    screen.fill((255, 255, 255))  # White background

    # Draw the ball
    pos = ball_body.position
    pygame.draw.circle(screen, (255, 0, 0), (int(pos.x), int(pos.y)), radius)

    # Draw the ground
    pygame.draw.line(screen, (0, 0, 0), (50, BAR_LEFT_Y), (WIDTH - 50, BAR_RIGHT_Y), 5)

    pygame.display.flip()
    clock.tick(60)
