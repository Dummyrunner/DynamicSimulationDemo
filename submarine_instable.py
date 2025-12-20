from submarine import (
    SubmarinePlant,
    Game,
    ReferenceSignal,
    _create_constant_reference_mapping as create_mapping,
)
from game_controller import ControllerPID
import pymunk

SAMPLE_TIME = 1 / 60.0
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

KP_DEFAULT = -6000
KI_DEFAULT = -0
KD_DEFAULT = -0

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
        ReferenceSignal(create_mapping(window_height=WINDOW_HEIGHT)),
    )
    game.main_loop()
