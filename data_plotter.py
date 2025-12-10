import matplotlib.pyplot as plt
from collections import deque
from typing import NamedTuple
import numpy as np


class PlotData(NamedTuple):
    """Container for data to be plotted."""

    time: list
    control_error: list
    cart_position_x: list
    cart_velocity_x: list
    joint_angle: list
    joint_angular_velocity: list


class DataPlotter:
    """Logs and plots simulation data in real-time using Matplotlib."""

    def __init__(self, max_points: int = 1000, update_interval: int = 50):
        """
        Initialize the data plotter.

        Args:
            max_points: Maximum number of data points to keep in history
            update_interval: Number of frames between plot updates (default: 50 frames)
        """
        self.max_points = max_points
        self.update_interval = update_interval
        self.time_buffer = deque(maxlen=max_points)
        self.control_error_buffer = deque(maxlen=max_points)
        self.cart_position_x_buffer = deque(maxlen=max_points)
        self.cart_velocity_x_buffer = deque(maxlen=max_points)
        self.joint_angle_buffer = deque(maxlen=max_points)
        self.joint_angular_velocity_buffer = deque(maxlen=max_points)
        self.simulation_time = 0.0

        self.figure = None
        self.axes = {}
        self.lines = {}
        self.frame_counter = 0
        self.update_frequency = update_interval  # Use the interval directly
        self.live_update_active = True

    def log_data(
        self,
        control_error: float,
        cart_position_x: float,
        cart_velocity_x: float,
        joint_angle: float,
        joint_angular_velocity: float,
        time_delta: float,
    ):
        """
        Log a data point from the simulation.

        Args:
            control_error: Error between reference and actual angle
            cart_position_x: X position of the cart
            cart_velocity_x: X velocity of the cart
            joint_angle: Angle of the joint in radians
            joint_angular_velocity: Angular velocity of the joint in rad/s
            time_delta: Time step delta
        """
        self.simulation_time += time_delta
        self.time_buffer.append(self.simulation_time)
        self.control_error_buffer.append(control_error)
        self.cart_position_x_buffer.append(cart_position_x)
        self.cart_velocity_x_buffer.append(cart_velocity_x)
        self.joint_angle_buffer.append(joint_angle)
        self.joint_angular_velocity_buffer.append(joint_angular_velocity)

    def get_plot_data(self) -> PlotData:
        """
        Get all logged data as lists.

        Returns:
            PlotData: Named tuple containing all logged data
        """
        return PlotData(
            time=list(self.time_buffer),
            control_error=list(self.control_error_buffer),
            cart_position_x=list(self.cart_position_x_buffer),
            cart_velocity_x=list(self.cart_velocity_x_buffer),
            joint_angle=list(self.joint_angle_buffer),
            joint_angular_velocity=list(self.joint_angular_velocity_buffer),
        )

    def show_live(self):
        """
        Display the plot in a separate native window with live updates.
        """
        plt.ion()  # Interactive mode (non-blocking)

        # Create figure with 6 subplots (3 rows, 2 columns)
        self.figure, axes_flat = plt.subplots(3, 2, figsize=(14, 10), tight_layout=True)
        axes_flat = axes_flat.flatten()
        self.figure.suptitle("Inverted Pendulum Simulation - Real-time Data")

        # Configure subplots
        titles = [
            "Control Error",
            "Joint Angle",
            "cart Position X",
            "cart Velocity X",
            "Joint Angular Velocity",
            "All States (Normalized)",
        ]
        ylabels = [
            "Error (rad)",
            "Angle (rad)",
            "Position (px)",
            "Velocity (px/s)",
            "Angular Vel (rad/s)",
            "Normalized Value",
        ]

        for idx, (ax, title, ylabel) in enumerate(zip(axes_flat, titles, ylabels)):
            ax.set_title(title)
            ax.set_xlabel("Time (s)")
            ax.set_ylabel(ylabel)
            ax.grid(True, alpha=0.3)
            self.axes[title] = ax

            # Create line objects for each plot
            if idx < 5:
                (line,) = ax.plot([], [], lw=2)
                self.lines[title] = [line]
            else:
                # Combined plot has 3 lines
                colors = ["red", "blue", "green"]
                labels = ["Control Error", "Joint Angle", "cart Position"]
                lines = []
                for color, label in zip(colors, labels):
                    (line,) = ax.plot([], [], lw=1.5, color=color, label=label)
                    lines.append(line)
                self.lines[title] = lines
                ax.legend(loc="upper left")

        self.figure.canvas.draw()
        updates_per_sec = 60.0 / self.update_frequency
        print(
            "Plot window opened. Updates every {} frames (~{:.1f} updates/sec at 60 FPS).".format(
                self.update_frequency, updates_per_sec
            )
        )

    def update_plot(self):
        """
        Update the live plot with new data. Call this every frame during simulation.
        Only actually updates display based on update_interval (default every 50 frames).
        """
        if self.live_update_active is False:
            return

        if self.figure is None:
            return

        self.frame_counter += 1

        # Only update display every N frames
        if self.frame_counter % self.update_frequency != 0:
            return

        data = self.get_plot_data()

        if len(data.time) == 0:
            return

        time_array = np.array(data.time)

        # Update individual plots
        plot_configs = [
            ("Control Error", [data.control_error]),
            ("Joint Angle", [data.joint_angle]),
            ("cart Position X", [data.cart_position_x]),
            ("cart Velocity X", [data.cart_velocity_x]),
            ("Joint Angular Velocity", [data.joint_angular_velocity]),
        ]

        for title, data_list in plot_configs:
            ax = self.axes[title]
            line = self.lines[title][0]
            line.set_data(time_array, np.array(data_list[0]))

            # Auto-scale axes
            ax.relim()
            ax.autoscale_view()

        # Update combined normalized plot
        def normalize(values):
            if not values:
                return np.array([])
            values_array = np.array(values)
            min_val = np.min(values_array)
            max_val = np.max(values_array)
            if max_val == min_val:
                return np.full_like(values_array, 0.5)
            return (values_array - min_val) / (max_val - min_val)

        combined_data = [
            normalize(data.control_error),
            normalize(data.joint_angle),
            normalize(data.cart_position_x),
        ]

        ax = self.axes["All States (Normalized)"]
        for line, data_array in zip(
            self.lines["All States (Normalized)"], combined_data
        ):
            line.set_data(time_array, data_array)

        ax.relim()
        ax.autoscale_view()

        # Draw updates
        self.figure.canvas.draw_idle()
        plt.pause(0.001)  # Brief pause to allow UI updates

    def toggle_live_update(self):
        """Toggle live plot updating on/off."""
        self.live_update_active = not self.live_update_active

    def save(self, filename: str):
        """
        Save the current plot to a file (PNG or PDF).

        Args:
            filename: Output filename (e.g., 'plot.png' or 'plot.pdf')
        """
        if self.figure is not None:
            self.figure.savefig(filename, dpi=150, bbox_inches="tight")
            print(f"Plot saved to {filename}")

    def clear(self):
        """Clear all logged data."""
        self.time_buffer.clear()
        self.control_error_buffer.clear()
        self.cart_position_x_buffer.clear()
        self.cart_velocity_x_buffer.clear()
        self.joint_angle_buffer.clear()
        self.joint_angular_velocity_buffer.clear()
        self.simulation_time = 0.0
        self.frame_counter = 0
