import pygame
import pymunk
import sys

# Initialize Pygame and Pymunk
pygame.init()
WIDTH = 600
HEIGHT = 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball Simulation")

# Create a pymunk space
space = pymunk.Space()
space.gravity = (0, 900)  # Set gravity (y is positive downwards)

# Create the ball
mass = 1
radius = 15
moment = pymunk.moment_for_circle(mass, 0, radius)
ball_body = pymunk.Body(mass, moment)
ball_body.position = (WIDTH // 2, HEIGHT // 4)  # Start position
ball_shape = pymunk.Circle(ball_body, radius)
ball_shape.elasticity = 0.95  # Make it bouncy
ball_shape.friction = 0.9
space.add(ball_body, ball_shape)

# Create the ground (static line)
ground_body = pymunk.Body(body_type=pymunk.Body.STATIC)
ground_shape = pymunk.Segment(ground_body, (50, HEIGHT - 50), (WIDTH - 50, HEIGHT - 50), 5)
ground_shape.elasticity = 0.95
ground_shape.friction = 0.9
space.add(ground_body, ground_shape)

# Game loop
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Reset ball position on mouse click
            ball_body.position = (WIDTH // 2, HEIGHT // 4)
            ball_body.velocity = (0, 0)

    # Update physics
    space.step(1/60.0)
    
    # Draw everything
    screen.fill((255, 255, 255))  # White background
    
    # Draw the ball
    pos = ball_body.position
    pygame.draw.circle(screen, (255, 0, 0), (int(pos.x), int(pos.y)), radius)
    
    # Draw the ground
    pygame.draw.line(screen, (0, 0, 0), (50, HEIGHT - 50), (WIDTH - 50, HEIGHT - 50), 5)
    
    pygame.display.flip()
    clock.tick(60)
