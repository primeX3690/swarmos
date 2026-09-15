from ursina import Entity, color
from config import OBSTACLE_POSITION, OBSTACLE_RADIUS, OBSTACLE_AVOID_WEIGHT


def create_obstacle():
    """Static obstacle — building/tree jaisa kuch, jisse drones bachte hain."""
    return Entity(
        model='sphere',
        scale=OBSTACLE_RADIUS * 2,
        color=color.rgba(180, 60, 60, 220),
        position=OBSTACLE_POSITION,
    )


def avoid_obstacle(drone, obstacle_pos):
    """
    Agar drone obstacle ke bahut paas hai, to usse door push karta hai.
    Ye velocity mein ek extra 'push' add karta hai — poora replace nahi karta,
    isliye drone ka normal behavior (boids/individual) bhi saath chalta rehta hai.
    """
    diff = drone.position - obstacle_pos
    dist = diff.length()
    safe_dist = OBSTACLE_RADIUS + 1.5

    if 0 < dist < safe_dist:
        strength = (1 - dist / safe_dist) * OBSTACLE_AVOID_WEIGHT
        push = diff.normalized() * strength
        drone.velocity += push