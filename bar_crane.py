import pygame
import pymunk
import pymunk.pygame_util
import sys


class VisualObject:
    def __init__(self, position, color=(150, 150, 150)):
        self.position = position
        self.color = color

    def draw(self, screen):
        pass


class StaticLine(VisualObject):
    def __init__(self, start_pos, end_pos, color=(150, 150, 150), thickness=2):
        super().__init__(start_pos, color)
        self.end_pos = end_pos
        self.thickness = thickness

    def draw(self, screen):
        pygame.draw.line(
            screen, self.color, self.position, self.end_pos, self.thickness
        )


class GameObject:
    def __init__(self, space):
        self.space = space
        self.body = None
        self.shape = None


class Runner(GameObject):
    def __init__(self, space, position, width=100, height=20):
        super().__init__(space)
        self.width = width
        self.height = height

        # Create kinematic body
        self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.body.position = position

        # Create rectangular shape
        self.shape = pymunk.Poly(
            self.body,
            vertices=[
                (0, 0),
                (0, height),
                (width, height),
                (width, 0),
            ],
            transform=pymunk.Transform(tx=-0.5 * width, ty=-0.5 * height),
            radius=1,
        )
        self.shape.color = (0, 255, 0, 255)
        space.add(self.body, self.shape)

    def update_velocity(self, velocity):
        self.body.velocity = velocity


class Ball(GameObject):
    def __init__(self, space, position, mass=90, radius=15):
        super().__init__(space)
        self.radius = radius

        # Create dynamic body
        moment = pymunk.moment_for_circle(mass, 0, radius)
        self.body = pymunk.Body(mass, moment)
        self.body.position = position

        # Create circle shape
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = 0.95
        self.shape.friction = 0.9
        space.add(self.body, self.shape)

    def reset_position(self, position):
        self.body.position = position
        self.body.velocity = (0, 0)


class Arm(GameObject):
    def __init__(self, space, runner_body, length=20):
        super().__init__(space)
        self.length = length

        # Create kinematic body
        self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.body.position = runner_body.position

        # Create segment shape
        self.shape = pymunk.Segment(
            self.body,
            (0, 0),
            (0, length),
            4,  # thickness
        )
        self.shape.color = (100, 100, 100, 255)
        space.add(self.body, self.shape)

    def update_position(self, runner_position, runner_height):
        self.body.position = runner_position + (0, runner_height / 2)


class Crane:
    def __init__(self, space, runner, ball):
        self.space = space
        self.runner = runner
        self.ball = ball

        # Create connection between runner and ball
        self.joint = pymunk.PinJoint(
            runner.body, ball.body, (0, runner.height / 2), (0, 0)
        )
        self.joint.collide_bodies = False
        space.add(self.joint)


class Game:
    def __init__(self):
        # Initialize Pygame and Pymunk
        pygame.init()

        # Constants
        self.WIDTH = 1200
        self.HEIGHT = 800
        self.RUNNER_SPEED = 300
        self.RUNNER_MAX_SPEED = 600
        self.RUNNER_WIDTH = 100
        self.RUNNER_HEIGHT = 20

        # Set up display
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Crane Simulation")

        # Create physics space
        self.space = pymunk.Space()
        self.space.gravity = (0, 900)

        # Create visual-only objects list (will be populated in setup_objects)
        self.non_physical_objects = []

        # Create game objects
        self.setup_objects()

        # Clock for frame rate
        self.clock = pygame.time.Clock()

        # Drawing options
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)

    def setup_objects(self):
        # Calculate positions
        bar_left_y = 0.1 * self.HEIGHT
        bar_right_y = bar_left_y
        bar_right_x = self.WIDTH - 50
        bar_left_x = 50
        center_pos = ((bar_right_x + bar_left_x) // 2, bar_left_y)

        # Create visual bar
        bar_line = StaticLine(
            (bar_left_x, bar_left_y),
            (bar_right_x, bar_right_y),
            (100, 100, 100),  # Gray color
            5,  # thickness
        )
        self.non_physical_objects.append(bar_line)

        # Create objects
        self.runner = Runner(
            self.space, center_pos, self.RUNNER_WIDTH, self.RUNNER_HEIGHT
        )
        self.ball = Ball(self.space, (self.WIDTH // 2, self.HEIGHT * 0.75))
        self.crane = Crane(self.space, self.runner, self.ball)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self.ball.reset_position(mouse_pos)

        # Handle continuous keyboard input
        keys = pygame.key.get_pressed()
        current_velocity_x = self.runner.body.velocity.x
        current_position_x = self.runner.body.position.x

        # Define screen bounds
        margin = self.RUNNER_WIDTH / 2 + 10
        left_bound = margin
        right_bound = self.WIDTH - margin

        # Handle bounds checking
        if current_position_x <= left_bound and current_velocity_x < 0:
            self.runner.update_velocity((-current_velocity_x, 0))
            self.runner.body.position = (left_bound, self.runner.body.position.y)
        elif current_position_x >= right_bound and current_velocity_x > 0:
            self.runner.update_velocity((-current_velocity_x, 0))
            self.runner.body.position = (right_bound, self.runner.body.position.y)

        # Movement handling
        new_velocity = (0, 0)
        if keys[pygame.K_LEFT]:
            new_velocity = (
                max(
                    current_velocity_x - self.RUNNER_SPEED * (1 / 60.0),
                    -self.RUNNER_MAX_SPEED,
                ),
                0,
            )
        elif keys[pygame.K_RIGHT]:
            new_velocity = (
                min(
                    current_velocity_x + self.RUNNER_SPEED * (1 / 60.0),
                    self.RUNNER_MAX_SPEED,
                ),
                0,
            )
        else:
            if abs(current_velocity_x) > 1:
                decel = self.RUNNER_SPEED * (1 / 60.0)
                if current_velocity_x > 0:
                    new_velocity = (max(0, current_velocity_x - decel), 0)
                else:
                    new_velocity = (min(0, current_velocity_x + decel), 0)

        self.runner.update_velocity(new_velocity)
        return True

    def update(self):
        # Update physics
        self.space.step(1 / 60.0)

    def draw(self):
        # Clear screen
        self.screen.fill((255, 255, 255))

        # Draw all objects using debug draw
        self.space.debug_draw(self.draw_options)

        # Draw all visual-only objects
        for visual_obj in self.non_physical_objects:
            visual_obj.draw(self.screen)

        # Update display
        pygame.display.flip()
        self.clock.tick(60)

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
