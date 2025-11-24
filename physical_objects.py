import pymunk
import pygame


class GameObject:
    def __init__(self, space):
        self.space = space
        self.body = None
        self.shape = None


class DynamicRunner(GameObject):
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
        """Draw the runner using pygame directly."""
        # Calculate the rectangle position (top-left corner)
        pos_x = self.body.position.x - self.width / 2
        pos_y = self.body.position.y - self.height / 2

        # Draw the rectangle
        pygame.draw.rect(surface, self.color, (pos_x, pos_y, self.width, self.height))


class Ball(GameObject):
    def __init__(self, space, position, mass=90, radius=15):
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


class BoatTopDown(GameObject):
    def __init__(self, space, position, length, width):
        super().__init__(space)
        self.width = width
        self.length = length
        self.color = (0, 255, 0)  # Green color
        self.mass = 1000
        # Calculate moment of inertia for a rectangle
        moment = (1 / 12) * self.mass * (self.width**2 + self.length**2)
        # Create dynamic body with proper inertia for rotation
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
                (0, length),
                (width, length),
                (width, 0),
            ],
            transform=pymunk.Transform(tx=-0.5 * width, ty=-0.5 * length),
            radius=1,
        )
        self.shape.elasticity = 0.9
        self.shape.friction = 0.9
        space.add(self.body, self.shape)

    def draw(self, screen):
        pos_x = self.body.position.x - self.width / 2
        pos_y = self.body.position.y - self.length / 2

        # Draw the rectangle
        pygame.draw.rect(screen, self.color, (pos_x, pos_y, self.width, self.length))
