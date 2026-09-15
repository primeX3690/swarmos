from ursina import Entity, Vec3, color
import math
from config import THREAT_POSITION, THREAT_RADIUS, THREAT_SURROUND_RADIUS, THREAT_FLEE_WEIGHT, DRONE_SPEED


def create_threat():
    """Threat/target point — defense scenario ke liye (jaise dushman drone/target)."""
    return Entity(
        model='sphere',
        scale=1.2,
        color=color.rgba(255, 20, 20, 255),
        position=THREAT_POSITION,
    )


def flee_threat(drone, threat_pos):
    """Threat se door bhagne wala push force — obstacle jaisa hi kaam karta hai."""
    diff = drone.position - threat_pos
    dist = diff.length()

    if 0 < dist < THREAT_RADIUS:
        strength = (1 - dist / THREAT_RADIUS) * THREAT_FLEE_WEIGHT
        push = diff.normalized() * strength
        drone.velocity += push


def surround_threat(drone, threat_pos, index, total_count):
    """
    Threat ko circle mein surround karna — har drone ko ek specific angle
    assign hota hai (index-based), taaki equally spaced circle bane.
    """
    angle = (2 * math.pi / total_count) * index
    target = threat_pos + Vec3(
        math.cos(angle) * THREAT_SURROUND_RADIUS,
        0,
        math.sin(angle) * THREAT_SURROUND_RADIUS,
    )

    diff = target - drone.position
    dist = diff.length()

    if dist > 0.2:
        drone.velocity = diff.normalized() * DRONE_SPEED
    else:
        drone.velocity = Vec3(0, 0, 0)