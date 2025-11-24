import pygame
import pymunk
import pymunk.pygame_util
import sys
from game_controller import CraneControllerPID
from inverted_pendulum_plant import (
    InvertedPendulumPlant,
    InvertedPendulumInput,
)
from pymunk import Vec2d
from pygame_widgets.slider import Slider
import pygame_widgets

SAMPLE_TIME = 1 / 60.0
INITIAL_KP = 3e7
INITIAL_KI = 0
INITIAL_KD = 0


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
        pygame.display.set_caption("Inverted Pendulum")

        # Create physics space
        self.space = pymunk.Space()
        self.plant = InvertedPendulumPlant(
            self.space, pygame.display.get_window_size(), SAMPLE_TIME
        )
        self.controller = CraneControllerPID(
            kp=INITIAL_KP, ki=INITIAL_KI, kd=INITIAL_KD, sample_time=SAMPLE_TIME
        )
        # Create visual-only objects list (will be populated in setup_objects)
        self.non_physical_objects = []
        self.control_active = True

        self.reference_signal = 0.0
        self.reference_signal_slider = Slider(
            self.screen,
            int(self.WIDTH * 0.2),
            int(self.HEIGHT * 0.9),
            int(self.WIDTH * 0.6),
            20,
            min=-100,
            max=100,
            step=1,
        )
        # Clock for frame rate
        self.clock = pygame.time.Clock()
        # Drawing options
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        self.recent_outputs = dict()
        self.simulation_time = 0.0

    def update_ui(self, events):
        # Clear screen
        self.screen.fill((255, 255, 255))
        self.plant.draw(self.draw_options, self.screen)

        # Update widgets and let pygame_widgets handle drawing
        pygame_widgets.update(events)

        # Update display
        pygame.display.flip()
        self.clock.tick(60)

    def main_loop(self):
        running = True
        frames_since_toggle_counter = 0
        while running:
            frames_since_toggle_counter += 1
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                    continue
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    # Only reset ball position if click is not on the slider
                    slider_rect = pygame.Rect(
                        int(self.WIDTH * 0.2),
                        int(self.HEIGHT * 0.9) - 20,
                        int(self.WIDTH * 0.6),
                        40,
                    )
                    if not slider_rect.collidepoint(mouse_pos):
                        self.plant.ball.reset_position(mouse_pos)

            # Update pygame_widgets with events (for slider interaction)
            pygame_widgets.update(events)

            keys = pygame.key.get_pressed()
            # Lock  control toggle for 10 frames to prevent rapid toggling
            if keys[pygame.K_c] and frames_since_toggle_counter > 10:
                self.control_active = not self.control_active
                frames_since_toggle_counter = 0
            if keys[pygame.K_ESCAPE]:
                running = False

            pygame_widgets.update(events)
            # Get current plant output
            plant_state = self.plant.get_state()
            control_error = self.reference_signal - plant_state.joint_angle
            # Get key related velocity change
            input_signal_from_key = self.plant.input_from_key()
            force_from_control = (
                self.controller.get_control_input(control_error)
                if self.control_active
                else 0.0
            )
            self.plant.set_input(
                InvertedPendulumInput(
                    x_force=(force_from_control + input_signal_from_key)
                )
            )
            # Update simulation
            self.plant.step(SAMPLE_TIME)
            self.update_ui(events)
            self.simulation_time += SAMPLE_TIME

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.main_loop()
