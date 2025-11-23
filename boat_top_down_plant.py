import pymunk
import pymunk.pygame_util
import math_helpers
from pymunk import Vec2d
from typing import NamedTuple
from abc import ABC, abstractmethod
from physical_objects import BoatTopDown
import pygame

BOAT_SPEED = 20
STEERING_TORQUE = 1e7
BOAT_LENGTH = 100
BOAT_WIDTH = 10


# Define input/output types as class attributes using nested classes
class BoatTopdownOutput(NamedTuple):
    x_distance: float
    x_velocity: float
    angle: float


class BoatTopdownInput(NamedTuple):
    steering_torque: float


class BoatTopdownState(NamedTuple):
    x_distance: float
    x_velocity: float
    angle: float
    angular_velocity: float


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


class BoatTopdownPlant(PlantBase):
    def __init__(self, space: pymunk.Space, window_size: tuple, sample_time: float):
        super().__init__(sample_time=sample_time)
        self.space: pymunk.Space = space
        self.n_inputs: int = 1
        self.n_outputs: int = 4
        self.control_active = True
        self._create_objects(window_size, space)
        self.input = BoatTopdownInput(0)
        self.output = BoatTopdownOutput(0, 0, 0)
        self.state = BoatTopdownState(0, 0, 0, 0)
        self.window_with = window_size[0]

    def step(self, time_delta):
        # Apply counter-rotating forces at opposite offsets to create pure torque
        offset = (0, BOAT_LENGTH)  # Offset along boat length
        force_magnitude = self.input.steering_torque
        force = (force_magnitude, 0)  # Horizontal force at vertical offset = rotation
        # Apply force perpendicular to offset (to create torque, not translation)
        self.boat.body.apply_force_at_local_point(force, offset)
        # Apply equal and opposite forces to prevent translation
        self.boat.body.apply_force_at_local_point(
            (-force[0], -force[1]), (-offset[0], -offset[1])
        )
        self.space.step(time_delta)

    def get_state(self) -> "BoatTopdownState":
        boat_body = self.boat.body
        angle = self._calculate_angle_radian()
        angular_velocity = boat_body.angular_velocity
        x_center = self.window_with / 2
        x_distance = boat_body.position - x_center
        x_velocity = boat_body.velocity.x
        return BoatTopdownState(
            x_distance=x_distance,
            x_velocity=x_velocity,
            angle=angle,
            angular_velocity=angular_velocity,
        )

    def get_output(self) -> "BoatTopdownOutput":
        state = self.state
        return BoatTopdownOutput(
            x_distance=state.x_distance, x_velocity=state.x_velocity, angle=state.angle
        )

    def set_input(self, input_data) -> None:
        self.input = input_data

    def draw(self, options, screen):
        # Draw all objects using debug draw
        for obj in self.all_physical_objects:
            obj.draw(screen)

        # Draw all visual-only objects
        for visual_obj in self.non_physical_objects:
            visual_obj.draw(self.screen)

    def force_from_key_input(self) -> Vec2d:
        """
        Returns:
            Vec2d: New velocity vector (x, y)
        """
        keys = pygame.key.get_pressed()
        print(keys[pygame.K_LEFT])
        print("key?")
        if keys[pygame.K_LEFT]:
            return Vec2d(-STEERING_TORQUE, 0)
        elif keys[pygame.K_RIGHT]:
            return Vec2d(STEERING_TORQUE, 0)
        else:
            return Vec2d(0, 0)

    def _create_objects(self, window_size, space):
        pos_x = window_size[0] // 2
        pos_y = window_size[1] * 0.8
        self.boat = BoatTopDown(
            space, position=(pos_x, pos_y), length=BOAT_LENGTH, width=BOAT_WIDTH
        )
        self.all_physical_objects.append(self.boat)
        # self.boat.body.velocity = Vec2d(0, -BOAT_SPEED)
        self.boat.body.velocity = Vec2d(0, -0)

    def _calculate_angle_radian(self):
        # Calculate vector from runner to ball
        boat_angle = self.boat.body.angle
        vertical_up = Vec2d(0, -1)
        return math_helpers.angle_between_vectors_radian(boat_angle, vertical_up)
