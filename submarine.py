import pygame
import pymunk
import sys
import numpy as np
from enum import Enum
from typing import NamedTuple
from dataclasses import dataclass
from pymunk import Vec2d
from physical_objects import Submarine
from game_controller import ControllerPID
from plant_base import PlantBase


SAMPLE_TIME = 1 / 60.0
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

KP_DEFAULT = -2800
KI_DEFAULT = -100
KD_DEFAULT = -3800


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
    SUBMARINE_HORIZONTAL_SPEED: float = 100
    KEY_FORCE_SCALE: float = 1e6


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


class ReferenceSignal:
    """Reference Signal class that allows to define a reference Signal for the submarine setup,
    where the can be defined for each horizontal position."""

    def __init__(self, mapping):
        self.mapping = mapping

    def evaluate(self, x_position: int) -> float:
        return self.mapping(x_position)

    def draw(
        self, screen: pygame.Surface, window_width: int, window_height: int
    ) -> None:
        """Draw the reference signal trajectory across the screen.

        For each x coordinate from 0 to window_width, marks the point
        (x, reference_value(x)) with a colored pixel to visualize the reference trajectory.

        Args:
            screen: pygame Surface to draw on
            window_width: Width of the window in pixels
            window_height: Height of the window in pixels
        """
        for x in range(window_width):
            y = self.evaluate(x)
            y_clamped = max(0, min(int(y), window_height - 1))
            pygame.draw.circle(
                screen,
                (150, 0, 0),
                (x, y_clamped),
                radius=1,
            )


def _create_constant_reference_mapping(window_height: int):
    """Create a constant reference mapping function to configure reference signal.

    Args:
        window_height: Height of the window in pixels
    """
    return lambda x_position: window_height / 2


def _create_step_reference_mapping(
    window_height: int, step_height: float, step_position: float
):
    """Create a step reference mapping function configure reference signal.

    Args:
        window_height: Height of the window in pixels
        step_height: Height of the step in pixels
        step_position: Horizontal position where the step occurs
    """

    return (
        lambda x_position: window_height / 2
        if x_position < step_position
        else window_height / 2 + step_height
    )


def _create_sine_reference_mapping(
    amplitude: float, frequency: float, phase: float, offset: float
):
    return (
        lambda x_position: amplitude * np.sin(frequency * x_position + phase) + offset
    )


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
        self.window_height = window_size[1]
        self.window_width = window_size[0]

        self._create_objects(window_size)
        self.input = SubmarineInput(0)
        self.output = SubmarineOutput(0)
        self.state = SubmarineState(0, 0)
        self.window_with = window_size[0]

    def step(self, time_delta):
        # Apply thrust with saturation
        thrust = self.input.vertical_thrust
        input_bound = self.model_params.KEY_FORCE_SCALE
        lower_bound = -input_bound
        upper_bound = input_bound
        saturated_thrust = np.clip(lower_bound, upper_bound, thrust)
        self.submarine.body.apply_force_at_local_point((0, saturated_thrust), (0, 0))
        self.space.step(time_delta)

    def get_output(self):
        return self.output

    def get_state(self):
        return self.state

    def set_input(self, input_data) -> None:
        self.input = input_data

    def draw(self, screen):
        self.submarine.draw(screen)

    def input_from_key(self):
        keys = pygame.key.get_pressed()
        vertical_thrust = 0.0
        if keys[pygame.K_UP]:
            vertical_thrust -= self.model_params.KEY_FORCE_SCALE
        if keys[pygame.K_DOWN]:
            vertical_thrust += self.model_params.KEY_FORCE_SCALE
        return vertical_thrust

    def _create_objects(self, window_size):
        window_height = window_size[1]

        # Create submarine
        self.submarine = Submarine(
            self.space, position=(10, window_height * 0.75), width=50, height=20
        )
        self.submarine.body.velocity = Vec2d(
            self.model_params.SUBMARINE_HORIZONTAL_SPEED, 0
        )


class Game:
    def __init__(
        self,
        plant: SubmarinePlant,
        controller: ControllerPID,
        reference_signal_object: ReferenceSignal,
    ):
        # Initialize Pygame and Pymunk
        pygame.init()
        self.clock = pygame.time.Clock()
        # Constants
        self.WIDTH = WINDOW_WIDTH
        self.HEIGHT = WINDOW_HEIGHT
        self.game_state = GameState.PAUSED
        self.frames_since_toggle_counter = 0

        # Control force arrow visualization parameters
        self.arrow_scale = 0.0001  # Pixels per Newton
        self.arrow_max_length = 150  # Maximum arrow length in pixels

        # Set up display
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Submarine Simulation")
        # Create physics space
        self.space = pymunk.Space()
        self.plant = plant
        self.controller = controller
        self.reference_signal_object = reference_signal_object
        self.reference_signal = reference_signal_object.evaluate(
            self.plant.submarine.body.position.x
        )
        self.control_active = False

    def update_ui(self):
        # Clear screen
        self.screen.fill((150, 200, 255))
        self.plant.draw(self.screen)
        # Draw reference signal
        self.reference_signal_object.draw(self.screen, self.WIDTH, self.HEIGHT)
        # Draw control force arrow
        if self.control_active:
            self._draw_control_force_arrow(
                self.plant.submarine.body.position,
                -self.plant.input.vertical_thrust,
                self.arrow_scale,
                self.arrow_max_length,
            )

        # Display current game state
        self._draw_state_indicator()

        # Update display
        pygame.display.flip()
        self.clock.tick(60)

    def _draw_state_indicator(self):
        """Draw the current game state on screen."""
        font = pygame.font.Font(None, 36)
        state_text = f"State: {self.game_state.value}"
        text_surface = font.render(state_text, True, (255, 255, 255))
        self.screen.blit(text_surface, (10, 10))

        # Draw control status
        control_status = "ON" if self.control_active else "OFF"
        control_text = f"Control: {control_status}"
        control_surface = font.render(control_text, True, (255, 255, 255))
        self.screen.blit(control_surface, (10, 50))

    def _display_least_squares_score(self, score):
        font = pygame.font.Font(None, 48)
        score_text = f"Least Squares Score: {score:.2f}"
        text_surface = font.render(score_text, True, (255, 255, 255))
        # Blit score text to center of screen
        text_rect = text_surface.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
        self.screen.blit(text_surface, text_rect)
        pygame.display.flip()
        # Pause for a few seconds to display the score
        pygame.time.delay(3000)

    def _draw_control_force_arrow(
        self, sub_pos, force, arrow_scale, arrow_max_length=150
    ):
        """Draw an arrow showing the control force magnitude and direction.

        Parameters
        ----------
        sub_pos : pymunk.Vec2d
            Submarine center position
        force : float
            Vertical thrust force in Newtons
        arrow_scale : float
            Scaling factor (pixels per Newton)
        arrow_max_length : float, optional
            Maximum arrow length in pixels (default: 150)
        """
        center_x = int(sub_pos.x)
        center_y = int(sub_pos.y)

        # Calculate arrow length with scaling and clamping
        arrow_length = min(abs(force) * arrow_scale, arrow_max_length)

        # Determine direction (up for positive, down for negative)
        if force > 0:
            end_x = center_x
            end_y = center_y - int(arrow_length)  # Up
            arrow_color = (0, 255, 0)  # Green for thrust up
        elif force < 0:
            end_x = center_x
            end_y = center_y + int(arrow_length)  # Down
            arrow_color = (255, 0, 0)  # Red for thrust down
        else:
            return  # No force, don't draw

        # Clamp arrow endpoints to window boundaries
        end_y = max(0, min(end_y, self.HEIGHT))

        # Draw main arrow line
        pygame.draw.line(
            self.screen,
            arrow_color,
            (center_x, center_y),
            (end_x, end_y),
            3,  # Line width
        )

        # Draw arrowhead
        if arrow_length > 10:  # Only draw arrowhead if arrow is long enough
            arrow_size = 10
            if force > 0:  # Pointing up
                pygame.draw.polygon(
                    self.screen,
                    arrow_color,
                    [
                        (end_x, end_y),
                        (end_x - arrow_size // 2, end_y + arrow_size),
                        (end_x + arrow_size // 2, end_y + arrow_size),
                    ],
                )
            else:  # Pointing down
                pygame.draw.polygon(
                    self.screen,
                    arrow_color,
                    [
                        (end_x, end_y),
                        (end_x - arrow_size // 2, end_y - arrow_size),
                        (end_x + arrow_size // 2, end_y - arrow_size),
                    ],
                )

    def main_loop(self):
        running = True
        least_squares_score = 0.0

        while running:
            if self.plant.submarine.body.position.x > self.WIDTH:
                self.game_state = GameState.FINISHED
                self._display_least_squares_score(least_squares_score)
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

            # Toggle control with C key (lock for 10 frames)
            if keys[pygame.K_c] and self.frames_since_toggle_counter > 10:
                self.control_active = not self.control_active
                self.frames_since_toggle_counter = 0

            if keys[pygame.K_ESCAPE]:
                running = False

            # Only perform simulation steps when in RUNNING state
            if self.game_state == GameState.RUNNING:
                input_from_key = (
                    self.plant.input_from_key() if not self.control_active else 0.0
                )
                self.reference_signal = self.reference_signal_object.evaluate(
                    self.plant.submarine.body.position.x
                )
                control_error = (
                    self.plant.submarine.body.position.y - self.reference_signal
                )
                input_from_controller = (
                    self.controller.get_control_input(control_error)
                    if self.control_active
                    else 0.0
                )
                self.plant.set_input(
                    SubmarineInput(
                        vertical_thrust=input_from_key + input_from_controller
                    )
                )
                least_squares_score += control_error**2
                self.plant.step(SAMPLE_TIME)
            self.update_ui()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    plant = SubmarinePlant(
        pymunk.Space(),
        window_size=(WINDOW_WIDTH, WINDOW_HEIGHT),
        sample_time=SAMPLE_TIME,
    )
    controller = ControllerPID(
        kp=KP_DEFAULT, ki=KI_DEFAULT, kd=KD_DEFAULT, sample_time=SAMPLE_TIME
    )
    game = Game(
        plant,
        controller,
        ReferenceSignal(
            _create_step_reference_mapping(
                window_height=WINDOW_HEIGHT,
                step_height=-WINDOW_HEIGHT // 4,
                step_position=WINDOW_WIDTH // 2,
            )
        ),
    )
    game.main_loop()
