import pymunk
import pymunk.pygame_util
from pymunk import Vec2d
from typing import NamedTuple
from abc import ABC, abstractmethod
from physical_objects import BoatTopDown

BOAT_SPEED = 20


# Define input/output types as class attributes using nested classes
class BoatTopdownOutput(NamedTuple):
    pass


class BoatTopdownInput(NamedTuple):
    pass


class BoatTopdownState(NamedTuple):
    pass


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
        self.input = BoatTopdownInput()
        self.output = BoatTopdownOutput()
        self.state = BoatTopdownState()

    def step(self, time_delta):
        self.space.step(time_delta)

    def get_state(self) -> "BoatTopdownState":
        return BoatTopdownState(0)

    def get_output(self) -> "BoatTopdownOutput":
        pass

    def set_input(self, input_data) -> None:
        self.input = input_data

    def draw(self, options):
        pass

    def force_from_key_input(self) -> Vec2d:
        """Calculate new velocity based on input and constraints

        Returns:
            Vec2d: New velocity vector (x, y)
        """
        pass

    def _create_objects(self, window_size, space):
        pos_x = window_size[0] // 2
        pos_y = window_size[1] * 0.8
        self.boat = BoatTopDown(space, position=(pos_x, pos_y), length=25, width=10)
        self.all_physical_objects.append(self.boat)
        self.boat.body.velocity = Vec2d(0, -BOAT_SPEED)
