import pygame
import pymunk
import sys
from enum import Enum
from boat_top_down_plant import BoatTopdownPlant, BoatTopdownInput
from abc import ABC, abstractmethod
from typing import NamedTuple
from dataclasses import dataclass
from pymunk import Vec2d
from physical_objects import Submarine

SAMPLE_TIME = 1 / 60.0
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800


class GameState(Enum):
    """Enumeration of possible game states."""

    READY = "READY"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    FINISHED = "FINISHED"


@dataclass
class DefaultSubmarineModelParams:
    SUBMARINE_WIDTH: int = 50
    SUBMARINE_HEIGHT: float = 20
    SUMBARINE_MASS: float = 9
    KEY_FORCE_SCALE: float = 5e6


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


class SubmarineOutput(NamedTuple):
    depth: float


class SubmarineInput(NamedTuple):
    vertical_thrust: float


class SubmarineState(NamedTuple):
    depth: float
    vertical_velocity: float


class SubmarinePlant(PlantBase):
    def __init__(
        self,
        space: pymunk.Space,
        window_size: tuple,
        sample_time: float,
        model_params=DefaultSubmarineModelParams,
    ):
        super().__init__(sample_time=sample_time)
        self.space: pymunk.Space = space
        self.model_params = model_params
        self.n_inputs: int = 1
        self.n_outputs: int = 1
        self.control_active = True
        self._create_objects(window_size, space)
        self.input = SubmarineInput(0)
        self.output = SubmarineOutput(0)
        self.state = SubmarineState(0, 0)
        self.window_with = window_size[0]

    def step(self, time_delta):
        self.submarine.body.apply_force_at_local_point(
            (0, self.input.vertical_thrust), (0, 0)
        )
        self.space.step(time_delta)

    def get_output(self):
        return self.output

    def get_state(self):
        return self.state

    def set_input(self, input_data) -> None:
        self.input = input_data

    def draw(self, screen):
        self.submarine.draw(screen)
        self.reference_visu.draw(screen)

    def input_from_key(self):
        keys = pygame.key.get_pressed()
        vertical_thrust = 0.0
        if keys[pygame.K_UP]:
            vertical_thrust += self.model_params.KEY_FORCE_SCALE
        if keys[pygame.K_DOWN]:
            vertical_thrust -= self.model_params.KEY_FORCE_SCALE
        return vertical_thrust

    def _create_objects(self, window_size, space):
        window_width = window_size[0]
        window_height = window_size[1]
        y_center = window_height / 2
        self.reference_visu = StaticLine(
            self.space,
            (0, y_center),
            (window_width, y_center),
            color=(150, 0, 0),
            thickness=1,
        )
        self.submarine = Submarine(
            self.space, position=(window_width / 4, y_center), width=50, height=20
        )
        # space.add(self.boat.body)


class Game:
    def __init__(self):
        # Initialize Pygame and Pymunk
        pygame.init()
        self.clock = pygame.time.Clock()
        # Constants
        self.WIDTH = WINDOW_WIDTH
        self.HEIGHT = WINDOW_HEIGHT
        self.reference_signal = 0.0
        self.game_state = GameState.PAUSED
        self.frames_since_toggle_counter = 0

        # Set up display
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Submarine Simulation")
        # Create physics space
        self.space = pymunk.Space()
        self.plant = SubmarinePlant(
            self.space,
            window_size=(WINDOW_WIDTH, WINDOW_HEIGHT),
            sample_time=SAMPLE_TIME,
        )

    def update_ui(self):
        # Clear screen
        self.screen.fill((150, 200, 255))
        self.plant.draw(self.screen)

        # Display current game state
        self._draw_state_indicator()

        # Update display
        pygame.display.flip()
        self.clock.tick(60)

    def _draw_state_indicator(self):
        """Draw the current game state on screen."""
        font = pygame.font.Font(None, 36)
        state_text = f"State: {self.game_state.value}"
        text_surface = font.render(state_text, True, (0, 0, 0))
        self.screen.blit(text_surface, (10, 10))

    def main_loop(self):
        running = True

        while running:
            self.frames_since_toggle_counter += 1
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                    continue

            # Handle keyboard input
            keys = pygame.key.get_pressed()

            # Toggle between RUNNING and PAUSED with P key (lock for 10 frames)
            if keys[pygame.K_p] and self.frames_since_toggle_counter > 10:
                if self.game_state == GameState.RUNNING:
                    self.game_state = GameState.PAUSED
                elif self.game_state == GameState.PAUSED:
                    self.game_state = GameState.RUNNING
                self.frames_since_toggle_counter = 0

            if keys[pygame.K_ESCAPE]:
                running = False

            # Only perform simulation steps when in RUNNING state
            if self.game_state == GameState.RUNNING:
                input_from_key = self.plant.input_from_key()
                self.plant.set_input(SubmarineInput(vertical_thrust=input_from_key))
                self.plant.step(SAMPLE_TIME)

            self.update_ui()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.main_loop()
