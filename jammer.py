from ursina import Entity, Vec3, color
import random
from config import (
    JAMMER_POSITION, JAMMER_RADIUS, FREQUENCIES,
    SIGNAL_DROP_RATE, SIGNAL_RECOVERY_RATE, HOP_SUCCESS_CHANCE,
)


def create_jammer_zone():
    """Enemy jammer tower — red pulsing sphere jo signal degrade karta hai."""
    return Entity(
        model='sphere',
        scale=JAMMER_RADIUS * 2,
        color=color.rgba(255, 0, 0, 60),
        position=JAMMER_POSITION,
    )


def update_signal(drone, dt):
    """
    Har frame drone ka signal update karta hai. Jammer zone ke andar signal
    girta hai; agar drone frequency-hop kar leta hai to bach jaata hai,
    warna signal 0 pe pahunchte hi RTH trigger hota hai.
    """
    dist = (drone.position - Vec3(*JAMMER_POSITION)).length()

    if dist < JAMMER_RADIUS:
        drone.jam_hop_timer -= dt
        if drone.jam_hop_timer <= 0:
            drone.jam_hop_timer = 1.0  # har second ek hop attempt
            new_freq = random.choice(FREQUENCIES)
            if random.random() < HOP_SUCCESS_CHANCE:
                drone.current_frequency = new_freq
                drone.signal_strength = min(100, drone.signal_strength + 10)
            else:
                drone.signal_strength -= SIGNAL_DROP_RATE * dt
        else:
            drone.signal_strength -= SIGNAL_DROP_RATE * dt
    else:
        drone.signal_strength = min(100, drone.signal_strength + SIGNAL_RECOVERY_RATE * dt)

    drone.signal_strength = max(0, drone.signal_strength)

    if drone.signal_strength <= 0 and drone.state == 'flying':
        drone.start_rth()