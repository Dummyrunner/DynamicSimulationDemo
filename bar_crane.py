import pygame
import pymunk
from pymunk import Vec2d
import pymunk.pygame_util
import sys
import math
from abc import ABC, abstractmethod
from collections import namedtuple
from game_controller import CraneControllerPI

SAMPLE_TIME = 1 / 60.0


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
        self.color = (0, 255, 0)  # Green color

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
        space.add(self.body, self.shape)

    def draw(self, surface):
        """Draw the runner using pygame directly."""
        # Calculate the rectangle position (top-left corner)
        pos_x = self.body.position.x - self.width / 2
        pos_y = self.body.position.y - self.height / 2

        # Draw the rectangle
        pygame.draw.rect(surface, self.color, (pos_x, pos_y, self.width, self.height))


class Ball(GameObject):
    def __init__(self, space, position, mass=90, radius=15):
        super().__init__(space)
        self.radius = radius
        self.color = (255, 0, 0)

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

    def draw(self, surface):
        """Draw the ball using pygame directly."""
        # Draw the circle
        pygame.draw.circle(
            surface,
            self.color,
            (int(self.body.position.x), int(self.body.position.y)),
            self.radius,
        )


class PinJointConnection:
    """Encapsulates a pymunk.PinJoint and provides a draw method.

    The anchor points are specified in the local coordinates of each body.
    """

    def __init__(
        self,
        space: pymunk.Space,
        body_a: pymunk.Body,
        body_b: pymunk.Body,
        anchor_a,
        anchor_b,
        color=(100, 100, 100),
    ):
        self.space = space
        self.body_a = body_a
        self.body_b = body_b
        self.anchor_a = anchor_a
        self.anchor_b = anchor_b
        self.color = color

        # create the physical joint and add to space
        self.joint = pymunk.PinJoint(self.body_a, self.body_b, anchor_a, anchor_b)
        self.joint.collide_bodies = False
        self.space.add(self.joint)

    def draw(self, surface):
        # get world coordinates for each anchor
        try:
            pos_a = self.body_a.local_to_world(self.anchor_a)
        except Exception:
            # fall back to body position
            pos_a = self.body_a.position
        try:
            pos_b = self.body_b.local_to_world(self.anchor_b)
        except Exception:
            pos_b = self.body_b.position

        # draw connecting line
        pygame.draw.line(surface, self.color, (pos_a.x, pos_a.y), (pos_b.x, pos_b.y), 2)

        # draw small anchor dots
        r = 3
        pygame.draw.circle(surface, self.color, (int(pos_a.x), int(pos_a.y)), r)
        pygame.draw.circle(surface, self.color, (int(pos_b.x), int(pos_b.y)), r)


class PlantBase(ABC):
    def __init__(self):
        self.non_physical_objects: list = []
        self.all_physical_objects: list = []
        self.n_inputs: int = 0
        self.n_outputs: int = 0

    @abstractmethod
    def step(self, time_delta):
        pass

    def set_input(self, input_data):
        pass

    @abstractmethod
    def get_output(self):
        pass


class PlantCrane(PlantBase):
    # Define the output type as a class attribute using a nested class
    class Output(
        namedtuple("PlantCraneOutput", ["x_velocity", "angle", "angular_velocity"])
    ):
        """Output type for the crane plant containing velocity and angle information.

        Attributes:
            x_velocity: Horizontal velocity of the runner
            angle: Current angle of the pendulum in radians
            angular_velocity: Angular velocity of the pendulum in radians per second
        """

        pass

    def __init__(self, space: pymunk.Space, window_size: tuple):
        self.space: pymunk.Space = space
        self.n_inputs: int = 1
        self.n_outputs: int = 4
        self.space.gravity = (0, 900)
        self.RUNNER_SPEED: int = 300
        self.RUNNER_MAX_SPEED: int = 600
        self.RUNNER_WIDTH: int = 100
        self.RUNNER_HEIGHT: int = 20
        self.non_physical_objects = []
        self._create_objects(window_size)

    def step(self, time_delta):
        self.space.step(time_delta)

    def get_output(self) -> "PlantCrane.Output":
        angle = self._calculate_angle_radian(
            self.runner.body.position, self.ball.body.position
        )
        angular_velocity = self._calculate_angle_velocity_radian_per_sec(
            self.runner.body.position,
            self.ball.body.position,
            self.ball.body.velocity,
        )
        x_velocity = self.runner.body.velocity.x
        return self.Output(
            x_velocity=x_velocity, angle=angle, angular_velocity=angular_velocity
        )

    def set_input(self, input_data):
        self.add_to_runner_velocity(Vec2d(input_data, 0))

    def draw(self, options):
        # Draw non-physical objects first (background elements)
        for obj in self.non_physical_objects:
            obj.draw(options.surface)

        # Draw the pin joint connection (if present)
        if hasattr(self, "pin_joint") and self.pin_joint is not None:
            self.pin_joint.draw(options.surface)

        # Draw game objects with their custom draw methods
        self.runner.draw(options.surface)
        self.ball.draw(options.surface)

    def _calculate_new_velocity(self) -> Vec2d:
        """Calculate new velocity based on input and constraints

        Returns:
            Vec2d: New velocity vector (x, y)
        """
        # Get current state
        keys = pygame.key.get_pressed()
        current_velocity = Vec2d(
            self.runner.body.velocity.x, self.runner.body.velocity.y
        )
        current_position = Vec2d(
            self.runner.body.position.x, self.runner.body.position.y
        )

        # Define screen bounds
        margin = self.RUNNER_WIDTH / 2 + 10
        left_bound = margin
        right_bound = self.WIDTH - margin

        # Handle bounds checking and return bounced velocity if needed
        if current_position.x <= left_bound and current_velocity.x < 0:
            self.runner.body.position = Vec2d(left_bound, self.runner.body.position.y)
            return Vec2d(-current_velocity.x, 0)
        elif current_position.x >= right_bound and current_velocity.x > 0:
            self.runner.body.position = Vec2d(right_bound, self.runner.body.position.y)
            return Vec2d(-current_velocity.x, 0)

        if keys[pygame.K_c]:
            # toggle control
            self.control_active = not self.control_active

        # Calculate new velocity based on input
        dt = SAMPLE_TIME
        if keys[pygame.K_LEFT]:
            new_x = max(
                current_velocity.x - self.RUNNER_SPEED * dt, -self.RUNNER_MAX_SPEED
            )
        elif keys[pygame.K_RIGHT]:
            new_x = min(
                current_velocity.x + self.RUNNER_SPEED * dt, self.RUNNER_MAX_SPEED
            )
        else:
            # Apply deceleration when no input
            if abs(current_velocity.x) > 1:
                decel = self.RUNNER_SPEED * dt
                if current_velocity.x > 0:
                    new_x = max(0, current_velocity.x - decel)
                else:
                    new_x = min(0, current_velocity.x + decel)
            else:
                new_x = 0

        return Vec2d(new_x, 0)

    def update_runner_velocity(self, velocity):
        """Update runner's velocity with limits applied.

        Args:
            velocity: Vec2d or tuple representing the new velocity
        """
        # Convert input to Vec2d if it isn't already
        if not isinstance(velocity, Vec2d):
            velocity = Vec2d(velocity[0], velocity[1])

        # Create new velocity vector with limits applied
        new_x = velocity.x
        if abs(new_x) > self.RUNNER_MAX_SPEED:
            new_x = self.RUNNER_MAX_SPEED if new_x > 0 else -self.RUNNER_MAX_SPEED
        # Get the current velocity vector from the body
        self.runner.body.velocity = (new_x, 0)

    def handle_input(self) -> Vec2d:
        """Calculate new velocity based on input and constraints

        Returns:
            Vec2d: New velocity vector (x, y)
        """
        # Get current state
        keys = pygame.key.get_pressed()
        current_velocity = Vec2d(
            self.runner.body.velocity.x, self.runner.body.velocity.y
        )
        current_position = Vec2d(
            self.runner.body.position.x, self.runner.body.position.y
        )

        # Define screen bounds
        margin = self.RUNNER_WIDTH / 2 + 10
        left_bound = margin
        right_bound = self.WIDTH - margin

        # Handle bounds checking and return bounced velocity if needed
        if current_position.x <= left_bound and current_velocity.x < 0:
            self.runner.body.position = Vec2d(left_bound, self.runner.body.position.y)
            return Vec2d(-current_velocity.x, 0)
        elif current_position.x >= right_bound and current_velocity.x > 0:
            self.runner.body.position = Vec2d(right_bound, self.runner.body.position.y)
            return Vec2d(-current_velocity.x, 0)

        if keys[pygame.K_c]:
            # toggle control
            self.control_active = not self.control_active

        # Calculate new velocity based on input
        dt = SAMPLE_TIME
        if keys[pygame.K_LEFT]:
            new_x = max(
                current_velocity.x - self.RUNNER_SPEED * dt, -self.RUNNER_MAX_SPEED
            )
        elif keys[pygame.K_RIGHT]:
            new_x = min(
                current_velocity.x + self.RUNNER_SPEED * dt, self.RUNNER_MAX_SPEED
            )
        else:
            # Apply deceleration when no input
            if abs(current_velocity.x) > 1:
                decel = self.RUNNER_SPEED * dt
                if current_velocity.x > 0:
                    new_x = max(0, current_velocity.x - decel)
                else:
                    new_x = min(0, current_velocity.x + decel)
            else:
                new_x = 0

        return Vec2d(new_x, 0)

    def _create_objects(self, window_size):
        # Calculate positions
        window_width = window_size[0]
        window_height = window_size[1]
        bar_left_y = 0.1 * window_height
        bar_right_y = bar_left_y
        bar_right_x = window_width - 50
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
        self.ball = Ball(self.space, (window_width // 2, window_height * 0.75))

        # Create pin joint connection (bottom center of runner to center of ball)
        runner_anchor = (0, self.RUNNER_HEIGHT / 2)  # Relative to runner's center
        ball_anchor = (0, 0)  # Center of the ball
        self.pin_joint = PinJointConnection(
            self.space, self.runner.body, self.ball.body, runner_anchor, ball_anchor
        )

        # Keep physical objects (include connection for drawing)
        self.all_physical_objects = [self.runner, self.ball, self.pin_joint]

    def add_to_runner_velocity(self, delta_velocity: Vec2d):
        """Add a velocity vector to current velocity.

        Args:
            delta_velocity: Vec2d or tuple representing velocity change
        """
        if not isinstance(delta_velocity, Vec2d):
            delta_velocity = Vec2d(delta_velocity[0], delta_velocity[1])

        current_velocity = Vec2d(
            self.runner.body.velocity.x, self.runner.body.velocity.y
        )
        new_velocity = current_velocity + delta_velocity
        self.update_runner_velocity(new_velocity)

    def _calculate_angle_radian(self, runner_position, ball_position):
        # Calculate vector from runner to ball
        dx = ball_position.x - runner_position.x
        dy = ball_position.y - runner_position.y

        # Calculate angle between this vector and vertical (0, 1)
        # pygame.math.Vector2.angle_to returns angle in degrees
        # Negative sign because pygame's y-axis is inverted
        angle = -pygame.math.Vector2(dx, dy).angle_to((0, 1))

        # Convert to radians for physics calculations
        return math.radians(angle)

    def _calculate_angle_velocity_radian_per_sec(
        self, runner_position, ball_position, ball_velocity
    ):
        # Calculate vector from runner to ball
        dx = ball_position.x - runner_position.x
        dy = ball_position.y - runner_position.y

        # Position vector
        pos_vector = pygame.math.Vector2(dx, dy)
        pos_magnitude = pos_vector.length()

        if pos_magnitude == 0:
            return 0.0

        # Unit position vector
        pos_unit_vector = pos_vector / pos_magnitude

        # Perpendicular vector to position vector
        perp_vector = pygame.math.Vector2(-pos_unit_vector.y, pos_unit_vector.x)

        # Project ball velocity onto perpendicular vector
        ball_velocity_vector = pygame.math.Vector2(ball_velocity.x, ball_velocity.y)
        tangential_velocity = ball_velocity_vector.dot(perp_vector)

        # Angular velocity = tangential velocity / radius
        angular_velocity = tangential_velocity / pos_magnitude

        return angular_velocity


class Game:
    def __init__(self):
        # Initialize Pygame and Pymunk
        pygame.init()

        # Constants
        self.WIDTH = 1200
        self.HEIGHT = 800
        self.reference_signal = 0.0
        # Set up display
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Crane Simulation")

        # Create physics space
        self.space = pymunk.Space()
        self.plant = PlantCrane(self.space, pygame.display.get_window_size())
        INITIAL_KP = 500.0
        INITIAL_KI = 50.0
        self.controller = CraneControllerPI(
            kp=INITIAL_KP, ki=INITIAL_KI, sample_time=SAMPLE_TIME
        )
        # Create visual-only objects list (will be populated in setup_objects)
        self.non_physical_objects = []
        self.control_active = True
        # Clock for frame rate
        self.clock = pygame.time.Clock()
        # Drawing options
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        self.recent_outputs = dict()
        self.simulation_time = 0.0

    def check_quit_or_ball_relocation(self):
        """Check if the application should quit.

        Returns:
            bool: True if the application should quit, False otherwise
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self.ball.reset_position(mouse_pos)
        return False

    def draw_control_arrow(self, control_signal):
        """Draw an arrow representing the control signal direction and magnitude."""
        if control_signal == (0, 0):
            return

        # Get runner's center position
        runner_pos = self.runner.body.position

        # Scale factor to make arrow visible (adjust this value to change arrow length)
        scale = 5  # Increased scale to make arrow more visible

        # Calculate arrow end point
        arrow_end = (
            runner_pos.x + control_signal[0] * scale,
            runner_pos.y + control_signal[1] * scale,
        )

        # Draw main line of arrow
        pygame.draw.line(
            self.screen,
            (255, 0, 0),  # Red color
            (runner_pos.x, runner_pos.y),
            arrow_end,
            2,  # Line thickness
        )

        # Calculate and draw arrow head
        if control_signal[0] != 0:  # Only if we have horizontal movement
            # Arrow head size
            head_size = 10
            angle = math.pi / 6  # 30 degrees for arrow head

            # Direction of the arrow
            direction = 1 if control_signal[0] > 0 else -1

            # Calculate arrow head points
            head_point1 = (
                arrow_end[0] - direction * head_size * math.cos(angle),
                arrow_end[1] - head_size * math.sin(angle),
            )
            head_point2 = (
                arrow_end[0] - direction * head_size * math.cos(angle),
                arrow_end[1] + head_size * math.sin(angle),
            )

            # Draw arrow head
            pygame.draw.line(self.screen, (255, 0, 0), arrow_end, head_point1, 2)
            pygame.draw.line(self.screen, (255, 0, 0), arrow_end, head_point2, 2)

    def update_ui(self):
        # Clear screen
        self.screen.fill((255, 255, 255))

        # Draw all objects using debug draw
        # self.plant.space.debug_draw(self.draw_options)
        for obj in self.plant.all_physical_objects:
            obj.draw(self.screen)

        # Draw all visual-only objects
        for visual_obj in self.plant.non_physical_objects:
            visual_obj.draw(self.screen)

        # Draw control signal visualization if we have current control signal
        if hasattr(self, "current_control_signal"):
            self.draw_control_arrow(self.current_control_signal)

        # Update display
        pygame.display.flip()
        self.clock.tick(60)

    def run(self):
        running = True
        while running:
            # Check for quit event
            if self.check_quit_or_ball_relocation():
                running = False
                continue

            self.plant.step(SAMPLE_TIME)
            # Get current plant output
            plant_output = self.plant.get_output()
            control_error = self.reference_signal - plant_output.angle
            # Get control input from controller
            control_signal = self.controller.get_control_input(control_error)
            self.plant.set_input(control_signal)

            # Update simulation
            self.plant.step(SAMPLE_TIME)
            self.update_ui()
            self.simulation_time += SAMPLE_TIME

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
