import time
from ursina import Vec3
from px4_drone import PX4Drone
from boids import apply_boids_rules
from dag_consensus import sync_dags_hardened as sync_dags

NUM_DRONES = 3
BASE_PORT = 14540
DT = 0.1
COMMS_RADIUS = 8.0

drones = [PX4Drone(i, BASE_PORT + i) for i in range(NUM_DRONES)]

print("Climbing...")
for d in drones:
    d.velocity = Vec3(0, 1.5, 0)
for _ in range(30):
    for d in drones:
        d.move(DT)
    time.sleep(DT)

# Har drone ko apna alag mission data do (jaise real mission mein hota)
for d in drones:
    d.dag.add_event(f"WAYPOINT_REACHED_D{d.id}")

print("Flocking + syncing DAGs for 15 seconds...")
for step in range(150):
    for d in drones:
        apply_boids_rules(d, drones)
        d.velocity.y += 1.5
    for d in drones:
        d.move(DT)

    for i in range(len(drones)):
        for j in range(i + 1, len(drones)):
            dist = (drones[i].position - drones[j].position).length()
            if dist < COMMS_RADIUS:
                sync_dags(drones[i], drones[j])

    if step % 20 == 0:
        sizes = [d.dag.size() for d in drones]
        print(f"  step {step}: DAG sizes = {sizes}")
    time.sleep(DT)

print(f"Final DAG sizes: {[d.dag.size() for d in drones]}")
print(f"All synced: {len(set(d.dag.size() for d in drones)) == 1}")
