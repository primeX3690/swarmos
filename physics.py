import random
import math
from ursina import Vec3
from config import GRAVITY, WIND_STRENGTH, SENSOR_NOISE_MAGNITUDE


class WindField:
    """Global wind — direction/strength change hoti rehti hai time ke saath."""
    def __init__(self):
        self.angle = random.uniform(0, 360)
        self.strength = random.uniform(0.3, WIND_STRENGTH)
        self.timer = 0

    def update(self, dt, change_interval):
        self.timer += dt
        if self.timer >= change_interval:
            self.timer = 0
            self.angle = random.uniform(0, 360)
            self.strength = random.uniform(0.3, WIND_STRENGTH)

    def get_force(self):
        rad = math.radians(self.angle)
        return Vec3(math.cos(rad), 0, math.sin(rad)) * self.strength


def apply_gravity_correction(drone, dt):
    """Agar drone flying state mein hai, halki gravity-pull simulate karo
    jise drone ka thrust counter karta hai — thoda natural 'bobbing' effect."""
    if drone.state == 'flying':
        drift = math.sin(drone.position.x * 0.5 + drone.position.z * 0.5) * 0.15
        drone.y += drift * dt


def apply_sensor_noise(position):
    """GPS/IMU noise simulate karta hai — position estimate mein chhota random error."""
    noise = Vec3(
        random.uniform(-SENSOR_NOISE_MAGNITUDE, SENSOR_NOISE_MAGNITUDE),
        0,
        random.uniform(-SENSOR_NOISE_MAGNITUDE, SENSOR_NOISE_MAGNITUDE),
    )
    return position + noise


def drain_battery(drone, dt, drain_rate):
    if drone.state == 'flying':
        drone.battery -= drain_rate * dt
        drone.battery = max(0, drone.battery)  # battary kabhi negative na ho