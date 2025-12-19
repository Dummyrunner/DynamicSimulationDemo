from abc import ABC, abstractmethod
import pygame


class PlantBase(ABC):
    """Abstract base class for physics simulation plants.

    Defines the common interface for all plant simulations with physics,
    state management, and control input handling.
    """

    def __init__(self, sample_time: float):
        """Initialize the plant base.

        Args:
            sample_time: Simulation sample time in seconds
        """
        self.sample_time: float = sample_time
        self.non_physical_objects: list = []
        self.all_physical_objects: list = []
        self.n_inputs: int = 0
        self.n_outputs: int = 0
        self.input = None
        self.output = None
        self.state = None

    @abstractmethod
    def step(self, time_delta: float) -> None:
        """Advance the physics simulation by one time step.

        Args:
            time_delta: Time delta for this simulation step in seconds
        """
        pass

    @abstractmethod
    def get_state(self):
        """Get the current state of the plant.

        Returns:
            NamedTuple: Current state with domain-specific fields
        """
        pass

    @abstractmethod
    def get_output(self):
        """Get the current output of the plant.

        Returns:
            NamedTuple: Current output (may differ from state if mapping is applied)
        """
        pass

    def set_input(self, input_data) -> None:
        """Set the control input for the plant.

        Args:
            input_data: NamedTuple with domain-specific input fields
        """
        self.input = input_data

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        """Render the plant to the screen.

        Args:
            screen: pygame Surface to draw on
        """
        pass

    @abstractmethod
    def input_from_key(self):
        """Get input from keyboard state.

        Returns:
            Domain-specific keyboard input (scalar or vector)
        """
        pass
