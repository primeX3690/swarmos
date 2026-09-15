from ursina import Vec3
from px4_drone import PX4Drone
import time

drone = PX4Drone(drone_id=0, port=14540)

print("Climbing to ~3m altitude first...")
drone.velocity = Vec3(0, 1.5, 0)  # Ursina y = upward
for i in range(30):
    drone.move(dt=0.1)
    print(f"[climb] drone.position = {drone.position}")
    time.sleep(0.1)

print("Now flying forward (north, 2 m/s) for 5 seconds...")
drone.velocity = Vec3(2, 1.5, 0)  # hold altitude + go forward
for i in range(50):
    drone.move(dt=0.1)
    print(f"[forward] drone.position = {drone.position}")
    time.sleep(0.1)

drone.velocity = Vec3(0, 1.5, 0)
drone.move(dt=0.1)
print("Done — hovering")
