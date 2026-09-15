import time
from ursina import Vec3
from px4_drone import PX4Drone
from boids import apply_boids_rules
from threat import flee_threat
from obstacle import avoid_obstacle

NUM_DRONES = 3
BASE_PORT = 14540
DT = 0.1

drones = [PX4Drone(i, BASE_PORT + i) for i in range(NUM_DRONES)]

print("Climbing...")
for d in drones:
    d.velocity = Vec3(0, 1.5, 0)
for _ in range(30):
    for d in drones:
        d.move(DT)
    time.sleep(DT)

threat_pos = Vec3(5, 3, 0)
obstacle_pos = Vec3(-5, 3, 0)

print("Fleeing threat + avoiding obstacle for 15 seconds...")
for step in range(150):
    for d in drones:
        apply_boids_rules(d, drones)
        flee_threat(d, threat_pos)
        avoid_obstacle(d, obstacle_pos)
        d.velocity.y += 1.5
    for d in drones:
        d.move(DT)
    if step % 10 == 0:
        for d in drones:
            dist_threat = (d.position - threat_pos).length()
            print(f"  D{d.id}: {d.position}  dist_from_threat={dist_threat:.2f}")
    time.sleep(DT)

print("Done.")
