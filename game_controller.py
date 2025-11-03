from abc import ABC, abstractmethod


class GameControllerBase(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_control_input(self, plant):
        # Process system output and return control input
        pass

    @abstractmethod
    def visualize_control_input(self, control_input):
        # Visualization code for control input
        pass

        # Visualization code for PID control input
        print(f"PID Control Input: {control_input}")


class CraneControllerPI(GameControllerBase):
    def __init__(self, kp: float, ki: float, sample_time: float):
        super().__init__()
        self._kp = kp
        self._ki = ki
        self.integral = 0.0
        self.sample_time = sample_time

    @property
    def kp(self) -> float:
        return self._kp

    @kp.setter
    def kp(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("kp must be a number")
        self._kp = float(value)

    @property
    def ki(self) -> float:
        return self._ki

    @ki.setter
    def ki(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("ki must be a number")
        self._ki = float(value)

    def get_control_input(self, control_error):
        self.integral += control_error * self.sample_time
        control_signal = self.kp * control_error + self.ki * self.integral
        print(f"PI Control Input: {control_signal}, Integral: {self.integral}")
        return control_signal

    def visualize_control_input(self, display, control_input):
        # Visualization code for PID control input
        print(f"PI Control Input: {control_input}, Integral: {self.integral}")


# def draw_control_arrow(self, control_signal):
#     """Draw an arrow representing the control signal direction and magnitude."""
#     if control_signal == (0, 0):
#         return

#     # Get runner's center position
#     runner_pos = self.runner.body.position

#     # Scale factor to make arrow visible (adjust this value to change arrow length)
#     scale = 5  # Increased scale to make arrow more visible

#     # Calculate arrow end point
#     arrow_end = (
#         runner_pos.x + control_signal[0] * scale,
#         runner_pos.y + control_signal[1] * scale,
#     )

#     # Draw main line of arrow
#     pygame.draw.line(
#         self.screen,
#         (255, 0, 0),  # Red color
#         (runner_pos.x, runner_pos.y),
#         arrow_end,
#         2,  # Line thickness
#     )

#     # Calculate and draw arrow head
#     if control_signal[0] != 0:  # Only if we have horizontal movement
#         # Arrow head size
#         head_size = 10
#         angle = math.pi / 6  # 30 degrees for arrow head

#         # Direction of the arrow
#         direction = 1 if control_signal[0] > 0 else -1

#         # Calculate arrow head points
#         head_point1 = (
#             arrow_end[0] - direction * head_size * math.cos(angle),
#             arrow_end[1] - head_size * math.sin(angle),
#         )
#         head_point2 = (
#             arrow_end[0] - direction * head_size * math.cos(angle),
#             arrow_end[1] + head_size * math.sin(angle),
#         )

#         # Draw arrow head
#         pygame.draw.line(self.screen, (255, 0, 0), arrow_end, head_point1, 2)
#         pygame.draw.line(self.screen, (255, 0, 0), arrow_end, head_point2, 2)
