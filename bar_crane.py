import pygame
import pymunk
from pymunk import Vec2d
import pymunk.pygame_util
import sys
import math
from abc import ABC

SAMPLE_TIME = 1 / 60.0


class VisualObject:
    def __init__(self, position, color=(150, 150, 150)):
        self.position = position
        self.color = color

    def draw(self, screen):
        pass


class StaticLine(VisualObject):
    def __init__(self, start_pos, end_pos, color=(150, 150, 150), thickness=2):
        super().__init__(start_pos, color)
        self.end_pos = end_pos
        self.thickness = thickness

    def draw(self, screen):
        pygame.draw.line(
            screen, self.color, self.position, self.end_pos, self.thickness
        )


class GameObject:
    def __init__(self, space):
        self.space = space
        self.body = None
        self.shape = None


class Runner(GameObject):
    def __init__(self, space, position, width=100, height=20):
        super().__init__(space)
        self.width = width
        self.height = height

        # Create kinematic body
        self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.body.position = position

        # Create rectangular shape
        self.shape = pymunk.Poly(
            self.body,
            vertices=[
                (0, 0),
                (0, height),
                (width, height),
                (width, 0),
            ],
            transform=pymunk.Transform(tx=-0.5 * width, ty=-0.5 * height),
            radius=1,
        )
        self.shape.color = (0, 255, 0, 255)
        space.add(self.body, self.shape)


class Ball(GameObject):
    def __init__(self, space, position, mass=90, radius=15):
        super().__init__(space)
        self.radius = radius

        # Create dynamic body
        moment = pymunk.moment_for_circle(mass, 0, radius)
        self.body = pymunk.Body(mass, moment)
        self.body.position = position

        # Create circle shape
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = 0.95
        self.shape.friction = 0.9
        space.add(self.body, self.shape)

    def reset_position(self, position):
        self.body.position = position
        self.body.velocity = (0, 0)


class Crane:
    def __init__(self, space, runner, ball):
        self.space = space
        self.runner = runner
        self.ball = ball

        # Create connection between runner and ball
        self.joint = pymunk.PinJoint(
            runner.body, ball.body, (0, runner.height / 2), (0, 0)
        )
        self.joint.collide_bodies = False
        self.all_objects = [self.runner, self.ball, self.joint]


class PlantBase(ABC):
    def __init__(self):
        self.non_physical_objects: list = []

    def step(self, time_delta):
        pass

    def set_input(self, input_data):
        pass

    def get_output(self):
        pass

    def draw(self, screen):
        pass


class PlantCrane(PlantBase):
    def __init__(self, space: pymunk.Space, window_size: tuple):
        self.space: pymunk.Space = space
        self.n_inputs: int = 1
        self.n_outputs: int = 4
        self.space.gravity = (0, 900)
        self.RUNNER_SPEED: int = 300
        self.RUNNER_MAX_SPEED: int = 600
        self.RUNNER_WIDTH: int = 100
        self.RUNNER_HEIGHT: int = 20
        self.non_physical_objects = []
        self.runner, self.ball = self._create_objects(window_size)
        # # Create connection between runner and ball
        # self.joint = pymunk.PinJoint(
        #     self.runner.body, self.ball.body, (0, self.runner.height / 2), (0, 0)
        # )

        self.crane = Crane(self.space, self.runner, self.ball)
        # for obj in self.crane.all_objects:
        #     print(self.space.shapes())
        #     print(self.space.bodies())
        #     self.space.add(obj.shape, obj.body)

    def _create_objects(self, window_size):
        # Calculate positions
        window_width = window_size[0]
        window_height = window_size[1]
        bar_left_y = 0.1 * window_height
        bar_right_y = bar_left_y
        bar_right_x = window_width - 50
        bar_left_x = 50
        center_pos = ((bar_right_x + bar_left_x) // 2, bar_left_y)

        # Create visual bar
        bar_line = StaticLine(
            (bar_left_x, bar_left_y),
            (bar_right_x, bar_right_y),
            (100, 100, 100),  # Gray color
            5,  # thickness
        )
        self.non_physical_objects.append(bar_line)

        # Create objects
        self.runner = Runner(
            self.space, center_pos, self.RUNNER_WIDTH, self.RUNNER_HEIGHT
        )
        self.ball = Ball(self.space, (window_width // 2, window_height * 0.75))
        # self.crane = Crane(self.space, self.runner, self.ball)
        return self.runner, self.ball


class Game:
    def __init__(self):
        # Initialize Pygame and Pymunk
        pygame.init()

        # Constants
        self.WIDTH = 1200
        self.HEIGHT = 800

        # Set up display
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Crane Simulation")

        # Create physics space
        self.space = pymunk.Space()
        self.plant = PlantCrane(self.space, pygame.display.get_window_size())

        # Create visual-only objects list (will be populated in setup_objects)
        self.non_physical_objects = []
        self.control_active = True

        # self.system_output_data = dict()
        # self.system_output_data["angle"] = 0
        # self.system_output_data["angular_velocity"] = 0
        # self.system_output_data["runner_position"] = 0
        # self.system_output_data["runner_velocity"] = 0

        # Clock for frame rate
        self.clock = pygame.time.Clock()

        # Drawing options
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)

        self.recent_outputs = dict()

        self.simulation_time = 0.0

    def update_runner_velocity(self, velocity):
        """Update runner's velocity with limits applied.

        Args:
            velocity: Vec2d or tuple representing the new velocity
        """
        # Convert input to Vec2d if it isn't already
        if not isinstance(velocity, Vec2d):
            velocity = Vec2d(velocity[0], velocity[1])

        # Create new velocity vector with limits applied
        new_x = velocity.x
        if abs(new_x) > self.RUNNER_MAX_SPEED:
            new_x = self.RUNNER_MAX_SPEED if new_x > 0 else -self.RUNNER_MAX_SPEED

        # Create new Vec2d with clamped x and zero y
        new_velocity = Vec2d(new_x, 0)
        self.runner.body.velocity = new_velocity

    def add_to_runner_velocity(self, delta_velocity):
        """Add a velocity vector to current velocity.

        Args:
            delta_velocity: Vec2d or tuple representing velocity change
        """
        if not isinstance(delta_velocity, Vec2d):
            delta_velocity = Vec2d(delta_velocity[0], delta_velocity[1])

        current_velocity = Vec2d(
            self.runner.body.velocity.x, self.runner.body.velocity.y
        )
        new_velocity = current_velocity + delta_velocity
        self.update_runner_velocity(new_velocity)

    def check_quit_or_ball_relocation(self):
        """Check if the application should quit.

        Returns:
            bool: True if the application should quit, False otherwise
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self.ball.reset_position(mouse_pos)
        return False

    def handle_input(self) -> Vec2d:
        """Calculate new velocity based on input and constraints

        Returns:
            Vec2d: New velocity vector (x, y)
        """
        # Get current state
        keys = pygame.key.get_pressed()
        current_velocity = Vec2d(
            self.runner.body.velocity.x, self.runner.body.velocity.y
        )
        current_position = Vec2d(
            self.runner.body.position.x, self.runner.body.position.y
        )

        # Define screen bounds
        margin = self.RUNNER_WIDTH / 2 + 10
        left_bound = margin
        right_bound = self.WIDTH - margin

        # Handle bounds checking and return bounced velocity if needed
        if current_position.x <= left_bound and current_velocity.x < 0:
            self.runner.body.position = Vec2d(left_bound, self.runner.body.position.y)
            return Vec2d(-current_velocity.x, 0)
        elif current_position.x >= right_bound and current_velocity.x > 0:
            self.runner.body.position = Vec2d(right_bound, self.runner.body.position.y)
            return Vec2d(-current_velocity.x, 0)

        if keys[pygame.K_c]:
            # toggle control
            self.control_active = not self.control_active

        # Calculate new velocity based on input
        dt = SAMPLE_TIME
        if keys[pygame.K_LEFT]:
            new_x = max(
                current_velocity.x - self.RUNNER_SPEED * dt, -self.RUNNER_MAX_SPEED
            )
        elif keys[pygame.K_RIGHT]:
            new_x = min(
                current_velocity.x + self.RUNNER_SPEED * dt, self.RUNNER_MAX_SPEED
            )
        else:
            # Apply deceleration when no input
            if abs(current_velocity.x) > 1:
                decel = self.RUNNER_SPEED * dt
                if current_velocity.x > 0:
                    new_x = max(0, current_velocity.x - decel)
                else:
                    new_x = min(0, current_velocity.x + decel)
            else:
                new_x = 0

        return Vec2d(new_x, 0)

    def update_physics(self):
        # Update physics
        self.space.step(SAMPLE_TIME)

    def _calculate_angle_radian(self, runner_position, ball_position):
        # Calculate vector from runner to ball
        dx = ball_position.x - runner_position.x
        dy = ball_position.y - runner_position.y

        # Calculate angle between this vector and vertical (0, 1)
        # pygame.math.Vector2.angle_to returns angle in degrees
        # Negative sign because pygame's y-axis is inverted
        angle = -pygame.math.Vector2(dx, dy).angle_to((0, 1))

        # Convert to radians for physics calculations
        return math.radians(angle)

    def _calculate_angle_velocity_radian_per_sec(
        self, runner_position, ball_position, ball_velocity
    ):
        # Calculate vector from runner to ball
        dx = ball_position.x - runner_position.x
        dy = ball_position.y - runner_position.y

        # Position vector
        pos_vector = pygame.math.Vector2(dx, dy)
        pos_magnitude = pos_vector.length()

        if pos_magnitude == 0:
            return 0.0

        # Unit position vector
        pos_unit_vector = pos_vector / pos_magnitude

        # Perpendicular vector to position vector
        perp_vector = pygame.math.Vector2(-pos_unit_vector.y, pos_unit_vector.x)

        # Project ball velocity onto perpendicular vector
        ball_velocity_vector = pygame.math.Vector2(ball_velocity.x, ball_velocity.y)
        tangential_velocity = ball_velocity_vector.dot(perp_vector)

        # Angular velocity = tangential velocity / radius
        angular_velocity = tangential_velocity / pos_magnitude

        return angular_velocity

    def calculate_system_output(self):
        """Return system output data in vector form."""
        system_output = dict()
        system_output["angle"] = self._calculate_angle_radian(
            self.runner.body.position, self.ball.body.position
        )
        system_output["angular_velocity"] = (
            self._calculate_angle_velocity_radian_per_sec(
                self.runner.body.position,
                self.ball.body.position,
                self.ball.body.velocity,
            )
        )
        system_output["runner_position"] = self.runner.body.position.x
        system_output["runner_velocity"] = self.runner.body.velocity.x
        return system_output

    def draw_control_arrow(self, control_signal):
        """Draw an arrow representing the control signal direction and magnitude."""
        if control_signal == (0, 0):
            return

        # Get runner's center position
        runner_pos = self.runner.body.position

        # Scale factor to make arrow visible (adjust this value to change arrow length)
        scale = 5  # Increased scale to make arrow more visible

        # Calculate arrow end point
        arrow_end = (
            runner_pos.x + control_signal[0] * scale,
            runner_pos.y + control_signal[1] * scale,
        )

        # Draw main line of arrow
        pygame.draw.line(
            self.screen,
            (255, 0, 0),  # Red color
            (runner_pos.x, runner_pos.y),
            arrow_end,
            2,  # Line thickness
        )

        # Calculate and draw arrow head
        if control_signal[0] != 0:  # Only if we have horizontal movement
            # Arrow head size
            head_size = 10
            angle = math.pi / 6  # 30 degrees for arrow head

            # Direction of the arrow
            direction = 1 if control_signal[0] > 0 else -1

            # Calculate arrow head points
            head_point1 = (
                arrow_end[0] - direction * head_size * math.cos(angle),
                arrow_end[1] - head_size * math.sin(angle),
            )
            head_point2 = (
                arrow_end[0] - direction * head_size * math.cos(angle),
                arrow_end[1] + head_size * math.sin(angle),
            )

            # Draw arrow head
            pygame.draw.line(self.screen, (255, 0, 0), arrow_end, head_point1, 2)
            pygame.draw.line(self.screen, (255, 0, 0), arrow_end, head_point2, 2)

    def update_ui(self):
        # Clear screen
        self.screen.fill((255, 255, 255))

        # Draw all objects using debug draw
        self.space.debug_draw(self.draw_options)

        # Draw all visual-only objects
        for visual_obj in self.non_physical_objects:
            visual_obj.draw(self.screen)

        # Draw control signal visualization if we have current control signal
        if hasattr(self, "current_control_signal"):
            self.draw_control_arrow(self.current_control_signal)

        # Update display
        pygame.display.flip()
        self.clock.tick(60)

    def controller_input(self, feedback) -> Vec2d:
        """Calculate control input as velocity adjustment

        Args:
            feedback: Dictionary with system state variables

        Returns:
            Vec2d: Velocity adjustment vector (x, y)
        """
        # Controller gains
        Kangle = 100.0
        Krunnervelocity = -5.0

        angle = feedback["angle"]
        angular_velocity = feedback["angular_velocity"]

        # Calculate horizontal velocity adjustment
        # Negative gains because positive angle needs negative correction
        control_signal = -Kangle * angle - Krunnervelocity * angular_velocity

        # Limit maximum control signal to prevent too aggressive movement
        max_control = 400  # Maximum velocity adjustment
        control_signal = max(min(control_signal, max_control), -max_control)

        # Return as velocity vector
        return Vec2d(control_signal, 0)

    def run(self):
        running = True

        # Initialize system output data
        self.system_output_data = self.calculate_system_output()

        while running:
            # Check for quit event
            if self.check_quit_or_ball_relocation():
                running = False
                continue

            # Get new velocity from input and control
            new_velocity = self.handle_input()
            self.update_runner_velocity(new_velocity)

            # Calculate and apply control adjustment
            control_velocity = self.controller_input(self.system_output_data)

            if self.control_active:
                self.current_control_signal = (
                    control_velocity  # Store for visualization
                )
                self.add_to_runner_velocity(control_velocity)

            # Update simulation
            self.update_physics()
            self.update_ui()
            self.system_output_data = (
                self.calculate_system_output()
            )  # Update simulation time
            self.simulation_time += SAMPLE_TIME

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
