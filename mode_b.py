from ursina import Vec3
import random
import math
from config import (
    DRONE_SPEED,
    DECISION_INTERVAL_MIN,
    DECISION_INTERVAL_MAX,
)


def apply_individual_behavior(drone):
    """
    Mode B: Individual Brain.
    Har drone doosre drones ko ignore karta hai — sirf apna independent
    decision leta hai (random direction, periodically refresh).
    Ye deliberately 'dumb' aur isolated hai — Mode A ke collective
    intelligence se contrast dikhane ke liye.
    """
    drone.decision_timer -= 1

    if drone.decision_timer <= 0:
        angle = random.uniform(0, 360)
        drone.velocity = Vec3(
            math.cos(math.radians(angle)),
            0,
            math.sin(math.radians(angle)),
        ) * DRONE_SPEED

        drone.decision_timer = random.randint(
            DECISION_INTERVAL_MIN, DECISION_INTERVAL_MAX
        )



