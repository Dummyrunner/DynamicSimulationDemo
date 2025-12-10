import pygame
import pymunk
import pymunk.pygame_util
import sys
from game_controller import CraneControllerPID, StateFeedbackController
from inverted_pendulum_plant import (
    InvertedPendulumPlant,
    InvertedPendulumInput,
)
from data_plotter import DataPlotter
from pygame_widgets.slider import Slider
import pygame_widgets
import numpy as np

SAMPLE_TIME = 1 / 60.0
INITIAL_KP = 3e7
INITIAL_KI = 0
INITIAL_KD = 0

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

SLIDER_POS_X = int(WINDOW_WIDTH * 0.2)
SLIDER_POS_Y = int(WINDOW_HEIGHT * 0.9)
SLIDER_WIDTH = int(WINDOW_WIDTH * 0.6)
SLIDER_HEIGHT = 20


class Game:
    def __init__(self):
        # Initialize Pygame and Pymunk
        pygame.init()

        # Constants
        self.WIDTH = WINDOW_WIDTH
        self.HEIGHT = WINDOW_HEIGHT
        self.reference_signal_angle = 0.0
        self.reference_signal_position = 0.0
        # Set up display
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Inverted Pendulum")

        # Create physics space
        self.space = pymunk.Space()
        self.plant = InvertedPendulumPlant(
            self.space, pygame.display.get_window_size(), SAMPLE_TIME
        )
        self.controller = StateFeedbackController(
            gain_matrix=np.array([1, 1, 1, 1]), sample_time=SAMPLE_TIME
        )
        # Create visual-only objects list (will be populated in setup_objects)
        self.non_physical_objects = []
        self.control_active = True

        # Initialize data plotter
        self.data_plotter = DataPlotter(max_points=10000, update_interval=20)
        self.data_plotter.live_update_active = False

        self.reference_signal_angle = 0.0
        self.reference_signal_slider = Slider(
            self.screen,
            SLIDER_POS_X,
            SLIDER_POS_Y,
            SLIDER_WIDTH,
            SLIDER_HEIGHT,
        )
        self.slider_rect = Game._create_slider_covering_rect(
            self.reference_signal_slider
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

    def _create_slider_covering_rect(slider: Slider):
        slider_rect = pygame.Rect(
            slider.getX(),
            slider.getY() - slider.getHeight() // 2,
            slider.getWidth(),
            slider.getHeight() * 8,
        )
        return slider_rect

    def _update_reference_signal_from_slider(self):
        """Update reference_signal_position based on slider value and groove joint bounds."""
        # Extract groove joint boundaries - they are stored as anchor points
        groove_a = self.plant.groove_joint.groove_a  # First anchor point in world space
        groove_b = (
            self.plant.groove_joint.groove_b
        )  # Second anchor point in world space
        groove_left_x = min(groove_a.x, groove_b.x)
        groove_right_x = max(groove_a.x, groove_b.x)

        # Slider range: -100 to 100 (centered at 0)
        slider_value = self.reference_signal_slider.getValue()
        # Map slider value to position: -100 -> groove_left_x, 0 -> center, 100 -> groove_right_x
        center_x = (groove_left_x + groove_right_x) / 2.0
        left_offset = center_x - groove_left_x
        right_offset = groove_right_x - center_x
        max_offset = max(left_offset, right_offset)
        self.reference_signal_position = center_x + (slider_value / 100.0) * max_offset

    def main_loop(self):
        running = True
        frames_since_toggle_counter = 0

        # Start displaying the live plot
        self.data_plotter.show_live()

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
                    if not self.slider_rect.collidepoint(mouse_pos):
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

            # Update reference signals from slider
            self._update_reference_signal_from_slider()

            # control_error = self.reference_signal_angle - plant_state.joint_angle
            currents_state = self.plant.get_state()
            # Get key related velocity change
            input_signal_from_key = self.plant.input_from_key()
            force_from_control = (
                self.controller.get_control_input(currents_state)
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

            # Log data for plotting
            self.data_plotter.log_data(
                control_error=0,
                cart_position_x=plant_state.cart_position_x,
                cart_velocity_x=plant_state.cart_velocity_x,
                joint_angle=plant_state.joint_angle,
                joint_angular_velocity=plant_state.joint_angular_velocity,
                time_delta=SAMPLE_TIME,
            )

            # Update plot display periodically
            self.data_plotter.update_plot()

            self.update_ui(events)
            self.simulation_time += SAMPLE_TIME

        # Save final plot to file
        if self.data_plotter.live_update_active:
            self.data_plotter.save("inverted_pendulum_simulation_final.png")
            print(
                "Simulation ended. Final plot saved to inverted_pendulum_simulation_final.png"
            )

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.main_loop()
