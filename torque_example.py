import pymunk
import pymunk.pygame_util
import pygame
import sys


def main():
    # Initialize Pygame
    pygame.init()

    # Create window
    screen = pygame.display.set_mode((600, 400))
    clock = pygame.time.Clock()

    # Create Pymunk space
    space = pymunk.Space()
    space.gravity = 0, 0

    # Create rectangular body
    body = pymunk.Body(body_type=pymunk.Body.DYNAMIC, mass=1, moment=1666)
    body.position = 300, 200

    # Create rectangular shape
    shape = pymunk.Poly.create_box(body, size=(100, 50))
    shape.elasticity = 0.95
    shape.friction = 0.9

    # Add body and shape to space
    space.add(body, shape)

    # Game loop
    while True:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit(0)

        # Apply force when left arrow key is pressed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            # Apply force at a point offset from center to create torque
            offset = (-50, 0)  # Offset from center of body
            force = (0, 50)  # Force vector
            body.apply_force_at_local_point(force, offset)
            body.apply_force_at_local_point(
                (-force[0], -force[1]), (-offset[0], -offset[1])
            )

        # Clear screen
        screen.fill((255, 255, 255))

        # Draw options for Pymunk debug drawing
        draw_options = pymunk.pygame_util.DrawOptions(screen)
        space.debug_draw(draw_options)

        # Update physics simulation
        space.step(1 / 50.0)

        # Update display
        pygame.display.flip()
        clock.tick(50)


if __name__ == "__main__":
    main()
