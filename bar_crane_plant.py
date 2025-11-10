import pygame
import pymunk
import pymunk.pygame_util
from pymunk import Vec2d
from typing import NamedTuple
from abc import ABC, abstractmethod
from physical_objects import PinJointConnection, Ball, DynamicRunner
import math_helpers


# Define input/output types as class attributes using nested classes
class PlantCraneOutput(NamedTuple):
    """Input type for the crane plant containing control signals.

    Attributes:
        x_velocity: Target horizontal velocity for the runner (scalar value in units/second)
    """

    x_velocity: float
    angle: float
    angular_velocity: float


class PlantCraneInput(NamedTuple):
    """Output type for the crane plant containing velocity and angle information.

    Attributes:
        x_velocity: Horizontal velocity of the runner
        angle: Current angle of the pendulum in radians
        angular_velocity: Angular velocity of the pendulum in radians per second
    """

    x_force: float


class PlantCraneState(NamedTuple):
    """State type for the crane plant containing positions and velocities.

    Attributes:
        runner_position: Position of the runner as Vec2d
        runner_velocity: Velocity of the runner as Vec2d
        ball_position: Position of the ball as Vec2d
        ball_velocity: Velocity of the ball as Vec2d
    """

    runner_position: Vec2d
    runner_velocity: Vec2d
    ball_position: Vec2d
    ball_velocity: Vec2d


class VisualObject:
    def __init__(self, position, color=(150, 150, 150)):
        self.position = position
        self.color = color

    def draw(self, screen):
        pass


class StaticLine(VisualObject):
    def __init__(self, space, start_pos, end_pos, color=(150, 150, 150), thickness=2):
        super().__init__(start_pos, color)
        self.end_pos = end_pos
        self.thickness = thickness
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = (
            (end_pos[0] - start_pos[0]) / 2,
            (end_pos[1] - start_pos[1]) / 2,
        )
        space.add(self.body)

    def draw(self, screen):
        pygame.draw.line(
            screen, self.color, self.position, self.end_pos, self.thickness
        )


class PlantBase(ABC):
    def __init__(self, sample_time):
        self.sample_time: float = sample_time
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
    class Constants:
        RUNNER_SPEED: int = 300
        RUNNER_MAX_SPEED: int = 600
        RUNNER_WIDTH: int = 100
        RUNNER_HEIGHT: int = 20
        RUNNER_MASS: float = 10000
        FORCE_SCALE: float = 1e6
        GRAVITY: Vec2d = Vec2d(0, 900)

    def __init__(self, space: pymunk.Space, window_size: tuple, sample_time: float):
        super().__init__(sample_time=sample_time)
        self.space: pymunk.Space = space
        self.n_inputs: int = 1
        self.n_outputs: int = 4
        self.space.gravity = PlantCrane.Constants.GRAVITY
        self.non_physical_objects = []
        self.control_active = True
        self._create_objects(window_size, space)
        self.input = PlantCraneInput(0.0)
        self.output = PlantCraneOutput(0.0, 0.0, 0.0)
        self.state = PlantCraneState(
            runner_position=Vec2d(0, 0),
            runner_velocity=Vec2d(0, 0),
            ball_position=Vec2d(0, 0),
            ball_velocity=Vec2d(0, 0),
        )

    def step(self, time_delta):
        # Adjustments according to input (runner velocity)
        # self.update_runner_velocity(Vec2d(self.input.x_force, 0))
        self.runner.body.apply_force_at_local_point((self.input.x_force, 0), (0, 0))
        self.space.step(time_delta)

    def get_state(self) -> "PlantCraneState":
        return PlantCraneState(
            runner_position=self.runner.body.position,
            runner_velocity=self.runner.body.velocity,
            ball_position=self.ball.body.position,
            ball_velocity=self.ball.body.velocity,
        )

    def get_output(self) -> "PlantCraneOutput":
        angle = self._calculate_angle_radian(
            self.runner.body.position, self.ball.body.position
        )
        angular_velocity = self._calculate_angle_velocity_radian_per_sec(
            self.runner.body.position,
            self.ball.body.position,
            self.ball.body.velocity,
        )

        state = self.get_state()
        return PlantCraneOutput(
            x_velocity=state.runner_velocity.x,
            angle=angle,
            angular_velocity=angular_velocity,
        )

    def set_input(self, input_data) -> None:
        self.input = input_data

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

    def update_runner_velocity(self, velocity: Vec2d):
        """Update runner's velocity with limits applied.

        Args:
            velocity: Vec2d or tuple representing the new velocity
        """
        # Convert input to Vec2d if it isn't already
        if not isinstance(velocity, Vec2d):
            raise TypeError("velocity must be a Vec2d instance")
        # Create new velocity vector with limits applied
        new_x = velocity.x
        if abs(new_x) > PlantCrane.Constants.RUNNER_MAX_SPEED:
            new_x = (
                PlantCrane.Constants.RUNNER_MAX_SPEED
                if new_x > 0
                else -PlantCrane.Constants.RUNNER_MAX_SPEED
            )
        new_velocity = Vec2d(new_x, 0)

        # Get the current velocity vector from the body
        self.runner.body.velocity = new_velocity

    def force_from_key_input(self) -> Vec2d:
        """Calculate new velocity based on input and constraints

        Returns:
            Vec2d: New velocity vector (x, y)
        """
        # Get current state
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            return -PlantCrane.Constants.FORCE_SCALE * Vec2d(1, 0)
        elif keys[pygame.K_RIGHT]:
            return PlantCrane.Constants.FORCE_SCALE * Vec2d(1, 0)
        else:
            return Vec2d(0, 0)

    def _create_objects(self, window_size, space):
        # Calculate positions
        window_width = window_size[0]
        window_height = window_size[1]
        bar_left_y = 0.1 * window_height
        bar_right_y = bar_left_y
        bar_right_x = window_width - 50
        bar_left_x = 50
        center_pos = ((bar_right_x + bar_left_x) // 2, bar_left_y)

        # Create visual bar
        rail = StaticLine(
            self.space,
            (bar_left_x, bar_left_y),
            (bar_right_x, bar_right_y),
            (100, 100, 100),  # Gray color
            5,  # thickness
        )
        self.rail = rail

        # Create objects
        self.runner = DynamicRunner(
            self.space,
            center_pos,
            PlantCrane.Constants.RUNNER_WIDTH,
            PlantCrane.Constants.RUNNER_HEIGHT,
        )
        self.ball = Ball(self.space, (window_width // 2, window_height * 0.75))

        # Create pin joint connection (bottom center of runner to center of ball)
        runner_anchor = (
            0,
            PlantCrane.Constants.RUNNER_HEIGHT / 2,
        )  # Relative to runner's center
        ball_anchor = (0, 0)  # Center of the ball
        self.pin_joint = PinJointConnection(
            space, self.runner.body, self.ball.body, runner_anchor, ball_anchor
        )

        # Constraint runner movement between bar ends by inducing a groove joint
        groove_left = (bar_left_x, bar_left_y)
        groove_right = (bar_right_x, bar_right_y)

        self.groove_joint = pymunk.GrooveJoint(
            space.static_body, self.runner.body, groove_left, groove_right, (0, 0)
        )
        # Keep physical objects (include connection for drawing)
        self.all_physical_objects = [self.runner, self.ball, self.pin_joint, self.rail]
        space.add(self.groove_joint)

    def _calculate_angle_radian(self, runner_position, ball_position):
        # Calculate vector from runner to ball
        rope_vec = ball_position - runner_position
        vertical_down = Vec2d(0, 1)
        return math_helpers.angle_between_vectors_radian(rope_vec, vertical_down)

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
