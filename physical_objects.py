import pymunk
import pygame
from collections import deque
from functools import wraps


def track_trajectory(color=(255, 255, 255), max_points=500):
    """Decorator that adds trajectory tracking to a GameObject's draw method.

    Args:
        color: RGB tuple for trajectory point color (e.g., (255, 0, 0) for red)
        max_points: Maximum number of trajectory points to keep in history
    """

    def decorator(draw_method):
        @wraps(draw_method)
        def wrapper(self, surface):
            # Initialize trajectory tracking if not already present
            if not hasattr(self, "_trajectory"):
                self._trajectory = deque(maxlen=max_points)
                self._trajectory_color = color

            # Add current position to trajectory
            if self.body is not None:
                self._trajectory.append(
                    (int(self.body.position.x), int(self.body.position.y))
                )

            # Draw trajectory points before drawing the object
            if len(self._trajectory) > 1:
                for point in self._trajectory:
                    pygame.draw.circle(surface, self._trajectory_color, point, 1)

            # Draw the object itself
            draw_method(self, surface)

        return wrapper

    return decorator


class GameObject:
    def __init__(self, space):
        self.space = space
        self.body = None
        self.shape = None


class Submarine(GameObject):
    def __init__(self, space, position, width=100, height=50):
        super().__init__(space)
        self.width = width
        self.height = height
        self.color = (200, 200, 0)
        moment = float("+inf")
        self.mass = 2000
        self.body = pymunk.Body(
            body_type=pymunk.Body.DYNAMIC,
            mass=self.mass,
            moment=moment,
        )
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
        self.shape.elasticity = 0.9
        self.shape.friction = 0.9
        space.add(self.body, self.shape)

    @track_trajectory(color=(255, 100, 0), max_points=1000)
    def draw(self, screen):
        pos_x = self.body.position.x - self.width / 2
        pos_y = self.body.position.y - self.height / 2

        # Draw the rectangle
        pygame.draw.rect(screen, self.color, (pos_x, pos_y, self.width, self.height))


class DynamicCart(GameObject):
    def __init__(self, space, position, width=100, height=20):
        super().__init__(space)
        self.width = width
        self.height = height
        self.color = (0, 100, 0)  # Green color
        self.mass = 10000
        # Create kinematic body
        self.body = pymunk.Body(
            body_type=pymunk.Body.DYNAMIC, mass=self.mass, moment=float("inf")
        )
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
        self.shape.elasticity = 0.9
        self.shape.friction = 0.9
        space.add(self.body, self.shape)

    def draw(self, surface):
        """Draw the cart using pygame directly."""
        # Calculate the rectangle position (top-left corner)
        pos_x = self.body.position.x - self.width / 2
        pos_y = self.body.position.y - self.height / 2

        # Draw the rectangle
        pygame.draw.rect(surface, self.color, (pos_x, pos_y, self.width, self.height))


class Ball(GameObject):
    def __init__(self, space, position, mass, radius=15):
        super().__init__(space)
        self.radius = radius
        self.color = (150, 0, 200)

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

    @track_trajectory(color=(200, 100, 255), max_points=800)
    def draw(self, surface):
        """Draw the ball using pygame directly."""
        # Draw the circle
        pygame.draw.circle(
            surface,
            self.color,
            (int(self.body.position.x), int(self.body.position.y)),
            self.radius,
        )


class PinJointConnection:
    """Encapsulates a pymunk.PinJoint and provides a draw method.

    The anchor points are specified in the local coordinates of each body.
    """

    def __init__(
        self,
        space: pymunk.Space,
        body_a: pymunk.Body,
        body_b: pymunk.Body,
        anchor_a,
        anchor_b,
        color=(100, 100, 100),
    ):
        self.space = space
        self.body_a = body_a
        self.body_b = body_b
        self.anchor_a = anchor_a
        self.anchor_b = anchor_b
        self.color = color

        # create the physical joint and add to space
        self.joint = pymunk.PinJoint(self.body_a, self.body_b, anchor_a, anchor_b)
        self.joint.collide_bodies = False
        self.space.add(self.joint)

    def draw(self, surface):
        # get world coordinates for each anchor
        try:
            pos_a = self.body_a.local_to_world(self.anchor_a)
        except Exception:
            # fall back to body position
            pos_a = self.body_a.position
        try:
            pos_b = self.body_b.local_to_world(self.anchor_b)
        except Exception:
            pos_b = self.body_b.position

        # draw connecting line
        pygame.draw.line(surface, self.color, (pos_a.x, pos_a.y), (pos_b.x, pos_b.y), 2)

        # draw small anchor dots
        r = 3
        pygame.draw.circle(surface, self.color, (int(pos_a.x), int(pos_a.y)), r)
        pygame.draw.circle(surface, self.color, (int(pos_b.x), int(pos_b.y)), r)
