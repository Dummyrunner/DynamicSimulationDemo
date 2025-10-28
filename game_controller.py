from abc import ABC, abstractmethod


class GameControllerBase(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def controller_input(self, plant):
        # Process system output and return control input
        pass

    @abstractmethod
    def visualize_control_input(self, control_input):
        # Visualization code for control input
        pass


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

    def controller_input(self, control_error):
        self.integral += control_error * self.sample_time
        control_signal = self.kp * control_error + self.ki * self.integral
        return control_signal

    def visualize_control_input(self, control_input):
        # Visualization code for PID control input
        print(f"PID Control Input: {control_input}")
