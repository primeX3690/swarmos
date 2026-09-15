"""
benchmark.py — SwarmOS Automated Benchmark Suite
==================================================
README mein likha tha: "A fully instrumented benchmark mode ... is
planned — see Roadmap." Yeh wahi hai.

Ab tak sab metrics README mein "Observed Results (Manual Testing)" ke
neeche the — ek insaan simulation dekh ke likh raha tha. Fellowship
reviewers ke liye woh weak evidence hai. Yeh script un exact cheezon ko
automated, repeatable, seeded runs mein measure karta hai — bina Ursina
window ke, CI mein bhi chal sakta hai (`python benchmark.py`).

IMPORTANT: Yeh koi naya "simulation" reimplement nahi karta — mock_drone.py
ke through wahi boids.py / formation.py / threat.py / obstacle.py /
dag_ledger.py / mesh_comms.py functions call karta hai jo main.py real-time
mein use karta hai. Isse benchmark numbers asli codebase ko reflect karte
hain, kisi separate "toy model" ko nahi.

Run:
    cd swarmos/           # apne actual repo root mein copy karke
    python benchmark.py --runs 20 --out benchmark_report.json

Output: printed summary table + JSON report (aggregated mean/std per metric).
"""
import argparse
import json
import random
import statistics as stats
import sys
import time

from ursina import Vec3

sys.path.insert(0, ".")  # taaki repo root ke modules import ho sakein

from mock_drone import MockDrone
from boids import apply_boids_rules
from formation import get_formation_offsets, rotate_offset, move_toward_formation
from threat import flee_threat, surround_threat
from obstacle import avoid_obstacle
from mesh_comms import sync_dags, hacker_inject_fake_dag_node

DT = 0.05
COLLISION_DIST = 0.5          # isse kam distance = collision maana jayega
COMMS_RADIUS = 8.0


def make_swarm(n, spawn_range=15):
    return [MockDrone(i, spawn_range=spawn_range) for i in range(n)]


# ---------------------------------------------------------------------
# 1. Collision avoidance (Mode A — Boids)
# ---------------------------------------------------------------------
def run_collision_test(n=15, steps=300, seed=0):
    """Collision = ek NAYA event jab do drones COLLISION_DIST se paas aate hain
    (frame-by-frame 'still touching' ko baar-baar count nahi karte — sirf
    onset, jaisa real crash-count hota)."""
    random.seed(seed)
    drones = make_swarm(n)
    currently_colliding = set()
    collision_events = 0
    min_dist_seen = float("inf")

    for _ in range(steps):
        for d in drones:
            apply_boids_rules(d, drones)
        for d in drones:
            d.move(DT)
        for i in range(len(drones)):
            for j in range(i + 1, len(drones)):
                pair = (i, j)
                dist = (drones[i].position - drones[j].position).length()
                min_dist_seen = min(min_dist_seen, dist)
                if dist < COLLISION_DIST:
                    if pair not in currently_colliding:
                        collision_events += 1
                        currently_colliding.add(pair)
                else:
                    currently_colliding.discard(pair)

    return {"collision_events": collision_events, "min_pairwise_distance": round(min_dist_seen, 3)}


# ---------------------------------------------------------------------
# 2. Formation convergence accuracy
# ---------------------------------------------------------------------
def run_formation_test(shape, n=15, steps=250, seed=0):
    random.seed(seed)
    drones = make_swarm(n, spawn_range=10)
    offsets = get_formation_offsets(shape, n)
    anchor = Vec3(0, 0, 0)
    heading = 0.0

    for _ in range(steps):
        for i, d in enumerate(drones):
            rx, rz = rotate_offset(offsets[i], heading)
            target = anchor + Vec3(rx, 0, rz)
            move_toward_formation(d, target, DT)
        anchor += Vec3(0.05, 0, 0.03) * DT * 20  # patrol drift, jaisa main.py mein
        heading += 0.01

    errors = []
    for i, d in enumerate(drones):
        rx, rz = rotate_offset(offsets[i], heading)
        target = anchor + Vec3(rx, 0, rz)
        errors.append((d.position - target).length())

    return {
        "shape": shape,
        "mean_position_error": round(stats.mean(errors), 4),
        "max_position_error": round(max(errors), 4),
    }


# ---------------------------------------------------------------------
# 3. Obstacle avoidance
# ---------------------------------------------------------------------
def run_obstacle_test(n=15, steps=300, seed=0):
    random.seed(seed)
    drones = make_swarm(n)
    obstacle_pos = Vec3(0, 3, 0)
    obstacle_radius = 3.0
    penetrations = 0
    min_dist = float("inf")

    for _ in range(steps):
        for d in drones:
            apply_boids_rules(d, drones)
            avoid_obstacle(d, obstacle_pos)
        for d in drones:
            d.move(DT)
            dist = (d.position - obstacle_pos).length()
            min_dist = min(min_dist, dist)
            if dist < obstacle_radius:
                penetrations += 1

    return {"obstacle_penetrations": penetrations, "min_distance_to_obstacle": round(min_dist, 3)}


# ---------------------------------------------------------------------
# 4. Threat response — flee & surround
# ---------------------------------------------------------------------
def run_threat_flee_test(n=15, steps=250, seed=0):
    random.seed(seed)
    drones = make_swarm(n, spawn_range=6)
    threat_pos = Vec3(0, 3, 0)
    threat_radius = 6.0

    for _ in range(steps):
        for d in drones:
            apply_boids_rules(d, drones)
            flee_threat(d, threat_pos)
        for d in drones:
            d.move(DT)

    outside = sum(1 for d in drones if (d.position - threat_pos).length() >= threat_radius)
    return {"drones_escaped": outside, "total": n, "escape_rate": round(outside / n, 3)}


def run_threat_surround_test(n=15, steps=250, seed=0):
    random.seed(seed)
    drones = make_swarm(n, spawn_range=10)
    threat_pos = Vec3(0, 3, 0)
    surround_radius = 5.0
    tolerance = 0.6

    for _ in range(steps):
        for i, d in enumerate(drones):
            surround_threat(d, threat_pos, i, n)
        for d in drones:
            d.move(DT)

    ring_errors = [abs((d.position - threat_pos).length() - surround_radius) for d in drones]
    converged = sum(1 for e in ring_errors if e <= tolerance)
    return {
        "drones_in_ring_tolerance": converged,
        "total": n,
        "mean_ring_error": round(stats.mean(ring_errors), 3),
    }


# ---------------------------------------------------------------------
# 5. Fault tolerance — unit loss + forced ledger sync (data survivability)
# ---------------------------------------------------------------------
def run_fault_tolerance_test(n=15, seed=0):
    random.seed(seed)
    drones = make_swarm(n)

    # thoda mission history har drone ko de do
    for step in range(5):
        for d in drones:
            d.dag.add_event(f"WAYPOINT_{step}_{d.id}")

    victim = random.choice(drones)
    nearest = min(
        (d for d in drones if d.id != victim.id),
        key=lambda d: (d.position - victim.position).length(),
    )

    events_before = victim.dag.size()
    sync_dags(victim, nearest)   # asli main.py jaisa hi force-sync-before-loss
    events_after_sync = nearest.dag.size()

    data_loss = max(0, events_before - events_after_sync)
    return {
        "victim_events_before_loss": events_before,
        "nearest_survivor_events_after_sync": events_after_sync,
        "mission_data_loss": data_loss,
    }


# ---------------------------------------------------------------------
# 6. DAG mesh — tamper detection (Sybil / hacker injection)
# ---------------------------------------------------------------------
def run_dag_tamper_detection_test(n=8, seed=0):
    random.seed(seed)
    drones = make_swarm(n)

    for d in drones:
        d.dag.add_event(f"LAUNCH_{d.id}")

    attacker = drones[0]
    hacker_inject_fake_dag_node(attacker)

    # mesh sync — tampered node poore swarm mein propagate hota hai
    for i in range(1, n):
        sync_dags(attacker, drones[i])

    detections = sum(1 for d in drones if not d.dag.validate_full_dag())
    return {
        "nodes_that_received_tampered_data": n,
        "nodes_that_detected_tamper": detections,
        "detection_rate": round(detections / n, 3),
    }


# ---------------------------------------------------------------------
# 7. Mesh sync convergence speed (comms-radius limited)
# ---------------------------------------------------------------------
def run_mesh_convergence_test(n=15, seed=0, max_rounds=30):
    random.seed(seed)
    drones = make_swarm(n, spawn_range=6)  # sab COMMS_RADIUS ke andar spawn

    for d in drones:
        d.dag.add_event(f"LOCAL_EVENT_{d.id}")

    total_expected = sum(d.dag.size() for d in drones) - (n - 1)  # genesis overlap adjust

    for round_num in range(1, max_rounds + 1):
        for i in range(n):
            for j in range(i + 1, n):
                if (drones[i].position - drones[j].position).length() <= COMMS_RADIUS:
                    sync_dags(drones[i], drones[j])
        sizes = {d.dag.size() for d in drones}
        if len(sizes) == 1:
            return {"rounds_to_full_consensus": round_num, "final_ledger_size": sizes.pop()}

    return {"rounds_to_full_consensus": None, "note": "did not converge within max_rounds"}


# ---------------------------------------------------------------------
# Aggregation + report
# ---------------------------------------------------------------------
TESTS = {
    "collision_avoidance": lambda seed: run_collision_test(seed=seed),
    "formation_grid": lambda seed: run_formation_test("grid", seed=seed),
    "formation_circle": lambda seed: run_formation_test("circle", seed=seed),
    "formation_v": lambda seed: run_formation_test("v", seed=seed),
    "formation_expanding_square": lambda seed: run_formation_test("expanding_square", seed=seed),
    "obstacle_avoidance": lambda seed: run_obstacle_test(seed=seed),
    "threat_flee": lambda seed: run_threat_flee_test(seed=seed),
    "threat_surround": lambda seed: run_threat_surround_test(seed=seed),
    "fault_tolerance": lambda seed: run_fault_tolerance_test(seed=seed),
    "dag_tamper_detection": lambda seed: run_dag_tamper_detection_test(seed=seed),
    "mesh_sync_convergence": lambda seed: run_mesh_convergence_test(seed=seed),
}


def aggregate(results_per_run):
    """List of dicts (same keys) -> {key: {mean, stdev, min, max}} for numeric fields."""
    keys = results_per_run[0].keys()
    agg = {}
    for k in keys:
        vals = [r[k] for r in results_per_run if isinstance(r.get(k), (int, float))]
        if vals:
            agg[k] = {
                "mean": round(stats.mean(vals), 4),
                "stdev": round(stats.stdev(vals), 4) if len(vals) > 1 else 0.0,
                "min": min(vals),
                "max": max(vals),
            }
        else:
            agg[k] = [r.get(k) for r in results_per_run]
    return agg


def main():
    parser = argparse.ArgumentParser(description="SwarmOS automated benchmark suite")
    parser.add_argument("--runs", type=int, default=10, help="trials per test")
    parser.add_argument("--out", type=str, default="benchmark_report.json")
    args = parser.parse_args()

    report = {"generated_at": time.strftime("%Y-%m-%d %H:%M:%S"), "runs_per_test": args.runs, "results": {}}

    print(f"\nSwarmOS Automated Benchmark — {args.runs} runs per test\n" + "=" * 55)

    for name, fn in TESTS.items():
        run_results = [fn(seed) for seed in range(args.runs)]
        agg = aggregate(run_results)
        report["results"][name] = agg

        print(f"\n[{name}]")
        for k, v in agg.items():
            if isinstance(v, dict):
                print(f"  {k:35s} mean={v['mean']:<10} stdev={v['stdev']:<8} "
                      f"min={v['min']:<8} max={v['max']}")
            else:
                print(f"  {k:35s} {v}")

    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nFull report saved to {args.out}\n")


if __name__ == "__main__":
    main()