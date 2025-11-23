import pygame
import pymunk
import sys
from boat_top_down_plant import BoatTopdownPlant, BoatTopdownInput, BoatTopdownState

SAMPLE_TIME = 1 / 60.0
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800


class Game:
    def __init__(self):
        # Initialize Pygame and Pymunk
        pygame.init()
        self.clock = pygame.time.Clock()
        # Constants
        self.WIDTH = 1200
        self.HEIGHT = 800
        self.reference_signal = 0.0

        # Set up display
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Top Down View Boat")

        # Create physics space
        self.space = pymunk.Space()
        self.plant = BoatTopdownPlant(
            self.space,
            window_size=(WINDOW_WIDTH, WINDOW_HEIGHT),
            sample_time=SAMPLE_TIME,
        )

    def update_ui(self):
        # Clear screen
        self.screen.fill((255, 255, 255))
        self.plant.draw(pymunk.pygame_util.DrawOptions(self.screen), self.screen)
        # Update display
        pygame.display.flip()
        self.clock.tick(60)

    def main_loop(self):
        running = True
        while running:
            # Update simulation
            self.update_ui()
            plant_output = self.plant.get_output()
            pygame.event.get()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                running = False
            torque_magnitude = abs(self.plant.force_from_key_input())
            print("INPUT TORQUE: ", torque_magnitude)
            self.plant.set_input(BoatTopdownInput(steering_torque=torque_magnitude))
            self.plant.step(SAMPLE_TIME)
            self.update_ui()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.main_loop()
