import pygame
import pymunk
import sys
from enum import Enum
from game_controller import StateFeedbackController
from inverted_pendulum_plant import (
    InvertedPendulumPlant,
    InvertedPendulumInput,
    DefaultModelParams,
)
from pygame_widgets.slider import Slider
import pygame_widgets
import numpy as np
import control
from inverted_pendulum_model import InvertedPendlumModel as IpModel
from state_space_control_calculations import (
    evaluate_controllability_observability,
)

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


class GameState(Enum):
    """Enumeration of possible game states."""

    READY = "READY"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    FINISHED = "FINISHED"


class Game:
    def __init__(self, plant, controller):
        # Initialize Pygame and Pymunk
        pygame.init()

        # Constants
        self.WIDTH = WINDOW_WIDTH
        self.HEIGHT = WINDOW_HEIGHT
        self.reference_signal_angle = 0.0
        self.reference_signal_position = WINDOW_WIDTH // 2
        self.game_state = GameState.PAUSED
        self.frames_since_toggle_counter = 0

        # Set up display
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Inverted Pendulum")

        # Create physics space
        self.plant = plant
        self.controller = controller
        self.control_active = True

        # Set up reference signal slider
        self.reference_signal_slider = Slider(
            self.screen,
            SLIDER_POS_X,
            SLIDER_POS_Y,
            SLIDER_WIDTH,
            SLIDER_HEIGHT,
        )
        self.slider_rect = self._create_slider_covering_rect(
            self.reference_signal_slider
        )

        # Clock for frame rate
        self.clock = pygame.time.Clock()
        self.simulation_time = 0.0

    def update_ui(self):
        # Clear screen
        self.screen.fill((255, 255, 255))
        self.plant.draw(self.screen)

        # Draw vertical red dashed line at reference position
        self._draw_reference_position_line()

        # Display current game state
        self._draw_state_indicator()

        # Update display
        pygame.display.flip()
        self.clock.tick(60)

    def _draw_reference_position_line(self):
        """Draw a vertical red dashed line at the reference position."""
        x = int(self.reference_signal_position)
        # Draw dashed line by drawing small segments
        dash_length = 10
        gap_length = 5
        y = 0
        while y < self.HEIGHT:
            pygame.draw.line(
                self.screen,
                (255, 0, 0),  # Red color
                (x, y),
                (x, min(y + dash_length, self.HEIGHT)),
                2,  # Line width
            )
            y += dash_length + gap_length

    def _draw_state_indicator(self):
        """Draw the current game state on screen."""
        font = pygame.font.Font(None, 36)
        state_text = f"State: {self.game_state.value}"
        text_surface = font.render(state_text, True, (0, 0, 0))
        self.screen.blit(text_surface, (10, 10))

        # Draw control status
        control_status = "ON" if self.control_active else "OFF"
        control_text = f"Control: {control_status}"
        control_surface = font.render(control_text, True, (0, 0, 0))
        self.screen.blit(control_surface, (10, 50))

    @staticmethod
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
        self.reference_signal_position = (
            center_x
            + 2 * (slider_value - 50) / 100.0 * (groove_right_x - groove_left_x) / 2
        )

    def main_loop(self):
        running = True

        while running:
            self.frames_since_toggle_counter += 1
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
                # Get current plant state
                plant_state = self.plant.get_state()

                # Update reference signals from slider
                self._update_reference_signal_from_slider()

                # Calculate state difference for control
                reference_state = np.array(
                    [self.reference_signal_position, 0, self.reference_signal_angle, 0]
                )
                difference_vector = -(plant_state - reference_state)

                # Get input from keyboard
                input_signal_from_key = self.plant.input_from_key()

                # Get control input from controller
                force_from_control = (
                    self.controller.get_control_input(difference_vector)
                    if self.control_active
                    else 0.0
                )

                # Combine control and keyboard inputs
                self.plant.set_input(
                    InvertedPendulumInput(
                        x_force=(force_from_control + input_signal_from_key)
                    )
                )

                # Update simulation
                self.plant.step(SAMPLE_TIME)
                self.simulation_time += SAMPLE_TIME

            self.update_ui()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    model_params = DefaultModelParams
    A, B, C, D = IpModel.state_space_model_matrices(
        mass_cart=model_params.CART_MASS,
        mass_pendulum=model_params.BALL_MASS,
        length_pendulum=model_params.PENDULUM_LENGTH,
        gravity=model_params.GRAVITY[1],
        force_scale=model_params.KEY_FORCE_SCALE,
    )
    sys_ol = control.ss(A, B, C, D)
    print("STATE SPACE SYSTEM REPRESENTATION:\n", sys_ol)

    controllable, observable = evaluate_controllability_observability(A, B, C)
    SCALE = 1
    desired_poles = [
        SCALE * (-1.6 + 1.3j),
        SCALE * (-1.6 - 1.3j),
        SCALE * (-2.0 - 10j),
        SCALE * (-2.0 + 10j),
    ]
    B_trp = B.reshape((4, 1))
    sys_ol_dsc = sys_ol.sample(SAMPLE_TIME, method="zoh")
    B_dsc_trp = sys_ol_dsc.B.reshape((4, 1))
    K_lqr_cont, P, _ = control.lqr(A, B_trp, np.diag([1, 1, 10, 1]), np.array([[0.1]]))
    K_lqr_dsc, P_dsc, _ = control.lqr(
        sys_ol_dsc.A, B_dsc_trp, np.diag([1, 1, 10, 1]), np.array([[0.1]])
    )
    print(f"Desired poles: {desired_poles}")
    K_cont = control.place(A, B, desired_poles)
    # plot_lti_poles(sys_ol, title="System Pole Locations open loop")
    B = B.reshape(4, 1)

    A_cl = A - B @ K_cont
    sys_cl_cont = control.ss(A_cl, B, C, D)
    sys_cl_cont.set_outputs(["x", "phi"], "y")
    # plot_lti_poles(
    #     sys_cl_cont,
    #     title="System Pole Locations closed Loop",
    #     figtext=f"controller gains {K_cont}",
    # )
    control.step_response(sys_cl_cont).plot()

    # Discretize
    dt = SAMPLE_TIME
    sys_cl_dsc = sys_cl_cont.sample(dt, method="zoh")
    desired_poles_dsc = np.exp(np.array(desired_poles) * dt)
    print(f"desired poles discrete: {desired_poles_dsc}")
    K_dsc = control.place(sys_cl_dsc.A, sys_cl_dsc.B, desired_poles_dsc)
    # plot_lti_poles(
    #     sys_cl_dsc,
    #     title="Discrete System Pole Locations closed Loop",
    #     figtext=f"controller gains {K_cont}",
    # )
    # control.step_response(sys_cl_dsc).plot()
    # plt.show()
    state_feedback_controller_gain_matrix = K_dsc
    plant = InvertedPendulumPlant(
        pymunk.Space(), (WINDOW_WIDTH, WINDOW_HEIGHT), SAMPLE_TIME
    )
    controller = StateFeedbackController(
        gain_matrix=state_feedback_controller_gain_matrix, sample_time=SAMPLE_TIME
    )
    game = Game(
        plant=plant,
        controller=controller,
    )
    game.main_loop()
