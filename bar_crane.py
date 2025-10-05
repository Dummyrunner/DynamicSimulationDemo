import pygame
import pymunk
import pymunk.pygame_util
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

# Constants for simulation
RUNNER_WIDTH = 100
RUNNER_HEIGHT = 20
RUNNER_SPEED = 300  # pixels per second
RUNNER_MAX_SPEED = 600  # maximum speed in pixels per second
ROPE_LENGTH = 100  # length of the rope in pixels
ROPE_SEGMENTS = 1  # number of segments in rope

# Create Runner
runner_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
CENTER_OF_BAR = ((BAR_RIGHT_X + BAR_LEFT_X) / 2, BAR_LEFT_Y + BAR_RIGHT_Y / 2)
runner_body.position = CENTER_OF_BAR
runner_shape = pymunk.Poly(
    runner_body,
    vertices=[
        (0, 0),
        (0, RUNNER_HEIGHT),
        (RUNNER_WIDTH, RUNNER_HEIGHT),
        (RUNNER_WIDTH, 0),
    ],
    transform=pymunk.Transform(tx=-0.5 * RUNNER_WIDTH, ty=-0.5 * RUNNER_HEIGHT),
    radius=1,
)
runner_shape.color = (0, 255, 0, 255)
space.add(runner_body, runner_shape)

# Create direct connection between runner and ball with PinJoint
connection = pymunk.PinJoint(
    runner_body,
    ball_body,
    (0, RUNNER_HEIGHT / 2),  # Attach point on runner (bottom center)
    (0, 0),  # Attach point on ball (center)
)
connection.collide_bodies = False  # Prevent collision between runner and ball
space.add(connection)

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

    # Handle continuous keyboard input
    keys = pygame.key.get_pressed()
    current_velocity_x = runner_body.velocity.x
    current_position_x = runner_body.position.x

    # Define screen bounds with margin
    MARGIN = RUNNER_WIDTH / 2 + 10
    LEFT_BOUND = MARGIN
    RIGHT_BOUND = WIDTH - MARGIN

    # Check for screen bounds collision and bounce
    if current_position_x <= LEFT_BOUND and current_velocity_x < 0:
        # Bounce off left wall
        runner_body.velocity = (-current_velocity_x, 0)
        runner_body.position = (LEFT_BOUND, runner_body.position.y)
    elif current_position_x >= RIGHT_BOUND and current_velocity_x > 0:
        # Bounce off right wall
        runner_body.velocity = (-current_velocity_x, 0)
        runner_body.position = (RIGHT_BOUND, runner_body.position.y)

    # Normal movement handling
    if keys[pygame.K_LEFT]:
        # Accelerate left
        new_velocity = max(
            current_velocity_x - RUNNER_SPEED * (1 / 60.0), -RUNNER_MAX_SPEED
        )
        runner_body.velocity = (new_velocity, 0)
    elif keys[pygame.K_RIGHT]:
        # Accelerate right
        new_velocity = min(
            current_velocity_x + RUNNER_SPEED * (1 / 60.0), RUNNER_MAX_SPEED
        )
        runner_body.velocity = (new_velocity, 0)
    else:
        # Decelerate when no keys are pressed
        if abs(current_velocity_x) > 1:
            # Apply deceleration in the opposite direction of movement
            if current_velocity_x > 0:
                new_velocity = max(0, current_velocity_x - RUNNER_SPEED * (1 / 60.0))
            else:
                new_velocity = min(0, current_velocity_x + RUNNER_SPEED * (1 / 60.0))
            runner_body.velocity = (new_velocity, 0)
        else:
            runner_body.velocity = (0, 0)

    # Update physics
    space.step(1 / 60.0)

    # Draw everything
    screen.fill((255, 255, 255))  # White background

    # Draw the ball
    pos = ball_body.position
    draw_options = pymunk.pygame_util.DrawOptions(screen)
    space.debug_draw(draw_options)
    # # Draw the ground
    # pygame.draw.line(screen, (0, 0, 0), (50, BAR_LEFT_Y), (WIDTH - 50, BAR_RIGHT_Y), 5)

    # pygame.draw.rect(
    #     screen,
    #     (0, 255, 0),
    #     pygame.Rect(
    #         int(runner_body.position.x - 0.5 * RUNNER_WIDTH),
    #         int(runner_body.position.y - 0.5 * RUNNER_HEIGHT),
    #         RUNNER_WIDTH,
    #         RUNNER_HEIGHT,
    #     ),
    # )
    pygame.display.flip()
    clock.tick(60)
