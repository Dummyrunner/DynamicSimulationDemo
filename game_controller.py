from abc import ABC, abstractmethod
import numpy as np


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


class ControllerPID(GameControllerBase):
    def __init__(self, kp: float, ki: float, kd: float, sample_time: float):
        super().__init__()
        self._kp = kp
        self._ki = ki
        self._kd = kd
        self.integral = 0.0
        self.previous_error = 0.0
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
        derivative = (control_error - self.previous_error) / self.sample_time
        control_signal = (
            self.kp * control_error + self.ki * self.integral + self._kd * derivative
        )
        print(f"PI Control Input: {control_signal}, Integral: {self.integral}")
        return control_signal

    def visualize_control_input(self, display, control_input):
        # Visualization code for PID control input
        # print(f"PI Control Input: {control_input}, Integral: {self.integral}")
        pass


class StateFeedbackController(GameControllerBase):
    def __init__(self, gain_matrix, sample_time: float):
        super().__init__()
        self.sample_time = sample_time
        self.gain_matrix = gain_matrix

    def get_control_input(self, state_vector):
        # convert name tuple to numpy array if needed
        if not isinstance(state_vector, np.ndarray):
            state_vector = np.array(state_vector)
        control_signal = -self.gain_matrix @ state_vector
        return control_signal

    def visualize_control_input(self, control_input):
        # Visualization code for state feedback control input
        print(f"State Feedback Control Input: {control_input}")
