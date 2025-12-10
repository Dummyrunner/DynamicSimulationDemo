import pygame
import pymunk
from pymunk import Vec2d
from typing import NamedTuple
from abc import ABC, abstractmethod
from physical_objects import PinJointConnection, Ball, DynamicRunner
import math_helpers
from dataclasses import dataclass


class InvertedPendulumOutput(NamedTuple):
    """Input type for the inverted pendulum plant containing control signals.

    Attributes:
        x_velocity: Target horizontal velocity for the runner (scalar value in units/second)
    """

    runner_position_x: float
    runner_velocity_x: float
    joint_angle: float
    joint_angular_velocity: float


class InvertedPendulumInput(NamedTuple):
    """Output type for the inverted pendulum plant containing velocity and angle information.

    Attributes:
        x_velocity: Horizontal velocity of the runner
        angle: Current angle of the pendulum in radians
        angular_velocity: Angular velocity of the pendulum in radians per second
    """

    x_force: float


class InvertedPendulumState(NamedTuple):
    """State type for the crane plant containing positions and velocities.

    Attributes:
        runner_position: Position of the runner as Vec2d
        runner_velocity: Velocity of the runner as Vec2d
        ball_position: Position of the ball as Vec2d
        ball_velocity: Velocity of the ball as Vec2d
    """

    runner_position_x: float
    runner_velocity_x: float
    joint_angle: float
    joint_angular_velocity: float


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


@dataclass
class DefaultModelParams:
    RUNNER_MAX_SPEED: int = 1200
    RUNNER_WIDTH: int = 100
    RUNNER_HEIGHT: int = 20
    RUNNER_MASS: float = 10000
    BALL_MASS: float = 90
    FORCE_SCALE: float = 1e7
    GRAVITY: Vec2d = Vec2d(0, 981)
    PENDULUM_LENGTH: float = 280


class InvertedPendulumPlant(PlantBase):
    def __init__(
        self,
        space: pymunk.Space,
        window_size: tuple,
        sample_time: float,
        model_params=DefaultModelParams,
    ):
        super().__init__(sample_time=sample_time)
        self.space: pymunk.Space = space
        self.n_inputs: int = 1
        self.n_outputs: int = 4
        self.model_params = model_params
        self.space.gravity = self.model_params.GRAVITY
        self.non_physical_objects = []
        self.control_active = True
        self._create_objects(window_size, space)
        self.input = InvertedPendulumInput(0.0)
        self.output = InvertedPendulumOutput(0.0, 0.0, 0.0, 0.0)
        self.state = InvertedPendulumState(
            runner_position_x=0.0,
            runner_velocity_x=0.0,
            joint_angle=0.0,
            joint_angular_velocity=0.0,
        )

    def step(self, time_delta):
        # Adjustments according to input (runner velocity)
        self.runner.body.apply_force_at_local_point((self.input.x_force, 0), (0, 0))
        self.space.step(time_delta)

    def get_state(self) -> "InvertedPendulumState":
        angle = self._calculate_angle_radian(
            self.runner.body.position, self.ball.body.position
        )
        angular_velocity = self._calculate_angle_velocity_radian_per_sec(
            self.runner.body.position,
            self.ball.body.position,
            self.ball.body.velocity,
        )
        return InvertedPendulumState(
            runner_position_x=float(self.runner.body.position.x),
            runner_velocity_x=float(self.runner.body.velocity.x),
            joint_angle=angle,
            joint_angular_velocity=angular_velocity,
        )

    def get_output(self) -> "InvertedPendulumOutput":
        state = self.get_state()
        return InvertedPendulumOutput(
            runner_position_x=state.runner_position_x,
            runner_velocity_x=state.runner_velocity_x,
            joint_angle=state.joint_angle,
            joint_angular_velocity=state.joint_angular_velocity,
        )

    def set_input(self, input_data) -> None:
        self.input = input_data

    def draw(self, options, screen):
        # Draw game objects with their custom draw methods
        self.runner.draw(screen)
        self.ball.draw(screen)
        self.pin_joint.draw(screen)
        self.rail.draw(screen)

    def input_from_key(self) -> Vec2d:
        """Calculate new velocity based on input and constraints

        Returns:
            Vec2d: New velocity vector (x, y)
        """
        # Get current state
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            return -self.model_params.FORCE_SCALE
        elif keys[pygame.K_RIGHT]:
            return self.model_params.FORCE_SCALE
        else:
            return 0.0

    def _create_objects(self, window_size, space):
        # Calculate positions
        window_width = window_size[0]
        window_height = window_size[1]
        bar_left_y = 0.7 * window_height
        bar_right_y = bar_left_y
        bar_right_x = window_width - 50
        bar_left_x = 50
        center_pos = ((bar_right_x + bar_left_x) // 2, bar_left_y)

        # Create visual bar
        rail = StaticLine(
            self.space,
            (bar_left_x, bar_left_y),
            (bar_right_x, bar_right_y),
            color=(100, 100, 100),
            thickness=5,
        )
        self.rail = rail

        # Create objects
        self.runner = DynamicRunner(
            self.space,
            center_pos,
            self.model_params.RUNNER_WIDTH,
            self.model_params.RUNNER_HEIGHT,
        )
        pendulum_length = self.model_params.PENDULUM_LENGTH
        self.ball = Ball(
            self.space,
            (center_pos[0], center_pos[1] - pendulum_length),
            self.model_params.BALL_MASS,
        )

        # Create pin joint connection (bottom center of runner to center of ball)
        runner_anchor = (
            0,
            -self.model_params.RUNNER_HEIGHT / 2,
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
        vertical_up = Vec2d(0, -1)
        return math_helpers.angle_between_vectors_radian(rope_vec, vertical_up)

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
