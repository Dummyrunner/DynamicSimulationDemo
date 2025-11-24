import pygame
import pymunk
import pymunk.pygame_util
import sys
from game_controller import CraneControllerPID
from bar_crane_plant import PlantCrane, PlantCraneInput

SAMPLE_TIME = 1 / 60.0


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
        self.plant = PlantCrane(
            self.space, pygame.display.get_window_size(), SAMPLE_TIME
        )
        INITIAL_KP = -2e7
        INITIAL_KI = 0
        INITIAL_KD = 0
        self.controller = CraneControllerPID(
            kp=INITIAL_KP, ki=INITIAL_KI, kd=INITIAL_KD, sample_time=SAMPLE_TIME
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

    def update_ui(self):
        # Clear screen
        self.screen.fill((255, 255, 255))

        # Draw all objects using debug draw
        for obj in self.plant.all_physical_objects:
            obj.draw(self.screen)

        # Draw all visual-only objects
        for visual_obj in self.plant.non_physical_objects:
            visual_obj.draw(self.screen)

        # Update display
        pygame.display.flip()
        self.clock.tick(60)

    def main_loop(self):
        running = True
        frames_since_toggle_counter = 0
        while running:
            frames_since_toggle_counter += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    continue
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    self.plant.ball.reset_position(mouse_pos)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    self.plant.ball.reset_position(mouse_pos)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_c] and frames_since_toggle_counter > 10:
                # toggle control
                self.control_active = not self.control_active
                frames_since_toggle_counter = 0

            # Get current plant output
            plant_output = self.plant.get_output()
            control_error = self.reference_signal - plant_output.angle
            # Get key related velocity change
            force_from_key_input = self.plant.force_from_key_input()
            # Bound velocity change to not exceed max speed and bar limits

            force_from_control = (
                self.controller.get_control_input(control_error)
                if self.control_active
                else 0.0
            )
            self.plant.set_input(
                PlantCraneInput(x_force=(force_from_control + force_from_key_input.x))
            )
            # Update simulation
            self.plant.step(SAMPLE_TIME)
            self.update_ui()
            self.simulation_time += SAMPLE_TIME

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.main_loop()
