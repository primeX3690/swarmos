from ursina import Vec3
import random
import math
from config import (
    SEPARATION_RADIUS,
    ALIGNMENT_RADIUS,
    COHESION_RADIUS,
    SEPARATION_WEIGHT,
    ALIGNMENT_WEIGHT,
    COHESION_WEIGHT,
    STEER_SMOOTHING,
    DRONE_SPEED,
)


def apply_boids_rules(drone, all_drones):
    """
    Mode A: Collective Brain.
    Har drone apne aas-paas ke drones dekh kar 3 rules follow karta hai:
      1. Separation — bahut paas ke drone se door bhaago (collision avoid)
      2. Alignment  — nearby drones ki average direction follow karo
      3. Cohesion   — nearby group ke center ki taraf khichav mehsoos karo
    Result: emergent flocking — koi central controller nahi, phir bhi group
    ek saath organized tareeke se move karta hai.
    """
    separation = Vec3(0, 0, 0)
    alignment = Vec3(0, 0, 0)
    cohesion = Vec3(0, 0, 0)

    sep_count = 0
    align_count = 0
    coh_count = 0

    for other in all_drones:
        if other.id == drone.id or other.compromised:
            continue

        dist = (drone.position - other.position).length()

        if dist < SEPARATION_RADIUS and dist > 0:
            push_away = (drone.position - other.position).normalized()
            separation += push_away / dist
            sep_count += 1

        if dist < ALIGNMENT_RADIUS:
            alignment += other.velocity
            align_count += 1

        if dist < COHESION_RADIUS:
            cohesion += other.position
            coh_count += 1

    steer = Vec3(0, 0, 0)

    if sep_count > 0:
        separation /= sep_count
        steer += separation * SEPARATION_WEIGHT

    if align_count > 0:
        alignment /= align_count
        if alignment.length() > 0:
            alignment = alignment.normalized() * DRONE_SPEED
        steer += (alignment - drone.velocity) * ALIGNMENT_WEIGHT

    if coh_count > 0:
        cohesion /= coh_count
        desired = (cohesion - drone.position)
        if desired.length() > 0:
            desired = desired.normalized() * DRONE_SPEED
        steer += (desired - drone.velocity) * COHESION_WEIGHT

    drone.velocity += steer * STEER_SMOOTHING
    drone.velocity.y = 0  # roughly level flight

    if drone.velocity.length() > 0:
        drone.velocity = drone.velocity.normalized() * DRONE_SPEED





def apply_stigmergy_avoidance(drone, heatmap_visits, cell_size, grid_resolution):
    """
    Real swarm intelligence: drone un cells se halka door bhaagta hai jo
    zyada visit ho chuke hain — isse swarm apne aap naye area explore
    karta hai bina kisi ko explicitly bataye 'wahan jao'. Yehi stigmergy
    hai — indirect coordination environment ke through, jaisa chींटियाँ
    pheromone trail se karti hain.
    """
    import math
    col = int((drone.position.x / cell_size) + grid_resolution / 2)
    row = int((drone.position.z / cell_size) + grid_resolution / 2)

    visits = heatmap_visits.get((row, col), 0)
    if visits > 15:
        angle = random.uniform(0, 2 * math.pi)
        nudge = Vec3(math.cos(angle), 0, math.sin(angle)) * 0.3
        drone.velocity += nudge   





