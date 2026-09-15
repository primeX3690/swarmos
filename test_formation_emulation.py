import time
from ursina import Vec3
from px4_drone import PX4Drone
from formation import get_formation_offsets, rotate_offset, move_toward_formation

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

offsets = get_formation_offsets('v', NUM_DRONES)
anchor = Vec3(0, 3, 0)
heading = 0.0

print("Moving into V formation for 15 seconds...")
for step in range(150):
    for i, d in enumerate(drones):
        rx, rz = rotate_offset(offsets[i], heading)
        target = anchor + Vec3(rx, 3, rz)
        move_toward_formation(d, target, DT)
    for d in drones:
        d.move(DT)
    if step % 10 == 0:
        for d in drones:
            print(f"  D{d.id}: {d.position}  target_offset={offsets[d.id]}")
    time.sleep(DT)

print("Done.")
