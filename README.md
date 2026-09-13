# SwarmOS — Decentralized AI Swarm Drone System (Blockchain/DAG-Secured)

**A decentralized swarm AI drone platform demonstrating collective and individual on-device intelligence, blockchain/DAG-inspired tamper-evident mesh networking, and mission resilience — built for both military and civilian dual-use deployment.**

---

## Key Advantages

- **Fully decentralized** — no ground station, cloud server, or single lead drone is required for the swarm to coordinate; every unit can independently continue the mission
- **Two interchangeable AI modes** — Collective (Boids-based emergent flocking) and Individual (adaptive, federated-learning agents) — letting the same platform switch coordination strategy based on mission needs or communication conditions
- **Blockchain/DAG-inspired data integrity, hardened at the ingestion point** — mission events are hash-chained and replicated across the mesh; tampered data is rejected the moment it's offered by a peer, not just flagged after the fact, and repeat offenders are automatically quarantined
- **Lightweight by design** — the blockchain/DAG layer only secures mission-critical events, not continuous telemetry, keeping it viable for real flight hardware rather than a heavy, impractical full-blockchain implementation
- **Validated by an automated benchmark suite** — every core capability (formation accuracy, collision avoidance, threat response, fault tolerance, mesh consensus, tamper detection) is measured across N=20 seeded, repeatable runs — not just manually observed
- **Dual-use from the ground up** — the same coordination engine serves both defense (reconnaissance, contested-environment resilience) and civilian (agriculture, disaster response, infrastructure inspection) missions

---

## Problem

Real-world drone swarms — whether used for defense reconnaissance, disaster response, or agricultural monitoring — depend on coordination that must survive failure. Most existing systems rely on centralized control, which creates a single point of failure: if the control node or a critical unit is lost, the mission can collapse.

SwarmOS explores an alternative: a swarm that coordinates collectively, shares mission data across a mesh network, and continues its mission even when individual units are destroyed or disconnected.

## What This Project Demonstrates

SwarmOS is a real-time 3D simulation (Python + Ursina Engine) built entirely solo, without any external funding or team, on consumer-grade hardware. It models eleven distinct capabilities relevant to real swarm deployment:

1. **Autonomous takeoff & landing sequencing** — staggered, realistic launch and recovery
2. **Collective Intelligence (Mode A)** — emergent flocking behavior via the Boids algorithm (separation, alignment, cohesion) — no central controller
3. **Individual Intelligence (Mode B)** — per-unit adaptive agents that learn from experience and share learned knowledge with nearby units over the mesh (see *Federated Learning* below)
4. **Dynamic Formation Flying** — Grid, Circle, V, and Expanding-Square formations, maintained while patrolling a moving path
5. **Real-time Obstacle Avoidance** — swarm reroutes around static obstacles without breaking coordination
6. **Threat Response** — two configurable behaviors: *flee* (evasion) and *surround* (containment)
7. **Fault Tolerance / Resilience** — when a unit is destroyed, the swarm automatically re-forms without manual intervention
8. **Mesh-Networked Data Sharing** — units within communication range replicate mission data to each other in real time (visualized as live connection links)
9. **Hardened, Hash-Linked Mission Ledger** — every mission event (launch, threat detected, unit lost) is recorded in a tamper-evident, hash-chained DAG ledger per unit; incoming data from a peer is validated *before* it's accepted, so a tampered node can never enter the ledger or propagate further
10. **Data Survivability** — before a unit is lost, its ledger is force-synced to the nearest surviving unit, so mission history is never dependent on any single node
11. **Area Coverage Tracking** — a real-time visual record of which zones the swarm has covered, relevant to both reconnaissance verification and field monitoring

## Dual-Use Design: Defense + Civilian

SwarmOS was deliberately designed around **two operating intelligence modes** that map directly onto two use-case families:

| Mode | Behavior | Defense / Security Application | Civilian Application |
|---|---|---|---|
| **Mode A — Collective Brain** | Emergent, self-organizing group behavior (Boids) | Coordinated reconnaissance, saturation coverage, group maneuvering under threat | Coordinated field surveying, synchronized agricultural spraying/monitoring |
| **Mode B — Individual Brain** | Independent, adaptive decision-making, federated across the mesh | Resilient operation when communications are degraded or jammed | Distributed sensor coverage where units operate autonomously across a wide area |

The same underlying engine — formation flying, obstacle avoidance, threat response, mesh data-sharing, and the hardened tamper-evident ledger — supports both a **tactical defense scenario** (area denial, reconnaissance, threat interception) and a **civilian scenario** (disaster search-and-rescue, crop monitoring, infrastructure inspection). This is intentional: the coordination and resilience problem is identical across both domains — only the payload and mission objective change.

## Why This Matters

Most swarm demos show flocking. Few demonstrate what happens when the mission is attacked, a unit is destroyed, or the network is under threat — and fewer still show how mission-critical data survives that failure, or prove it with repeatable numbers rather than a one-off demo. SwarmOS was built to prove the coordination and resilience layer first — and now to prove it automatically, on every run — before investing in mission-specific payloads or hardware.

## Tech Stack

- **Language:** Python
- **Engine:** Ursina (built on Panda3D) for real-time 3D rendering
- **Core Algorithms:** Boids flocking, federated Q-learning agents, formation-offset geometry with patrol-path rotation, SHA-256 hash-chained DAG ledger with ingestion-time validation
- **Testing:** headless automated benchmark suite (`benchmark.py`) that exercises the real simulation modules directly — no separate reimplementation
- Built and tested on consumer hardware (Ryzen 3, 8GB RAM) — no GPU or cloud compute required


## Run It Yourself

```bash
git clone [repo link]
cd swarm_ursina
python -m venv venv
venv\Scripts\activate        # Windows
pip install ursina
python main.py
```

## Controls

| Key | Action |
|---|---|
| `M` | Toggle Mode A (Collective) ↔ Mode B (Individual) |
| `1` / `2` / `3` / `4` | Grid / Circle / V / Expanding-Square formation (patrolling) |
| `O` | Toggle obstacle + avoidance |
| `T` | Toggle threat — flee behavior |
| `Y` | Toggle threat — surround behavior |
| `K` | Destroy a random unit (test resilience) |
| `H` | Toggle area-coverage heatmap |
| `J` | Toggle jammer zone (electronic warfare / signal degradation) |
| `L` | Initiate landing sequence |

## Automated Benchmark Results

Every number below comes from `benchmark.py` — a headless test harness that calls the **exact same functions** the live simulation uses (`boids.py`, `formation.py`, `threat.py`, `obstacle.py`, `dag_ledger.py`, `mesh_comms.py`), run **20 times with different random seeds**, not a single manual observation. Full raw output: `benchmark_report.json` (regenerate anytime with `python benchmark.py --runs 20`).

| Metric | Result (N=20 runs) |
|---|---|
| Swarm size tested | 15 units per run, real-time capable on consumer hardware (Ryzen 3, 8GB RAM) |
| Collision events (Mode A, Boids) | Mean 1.4 per run (min 0, max 7) — minimum pairwise distance stayed above 0.11 units in the worst case |
| Formation convergence error — Grid / Circle / V / Expanding-Square | Mean position error 0.075–0.084 units across all four shapes — deterministic convergence regardless of spawn position |
| Obstacle avoidance | Mean 1.6 boundary penetrations per run; swarm maintained a mean minimum distance of 3.48 units from the obstacle |
| Threat — flee response | **100% escape rate** — all 15/15 drones cleared the threat radius in every run |
| Threat — surround response | Mean 13.45/15 drones converged within tight ring tolerance (0.6 units); mean ring error 0.20 units |
| Fault tolerance (unit loss) | **Zero mission-data loss** — nearest surviving unit's ledger fully absorbed the lost unit's mission history before removal, every run |
| DAG tamper detection (baseline validation) | **100% detection rate** — every unit that received tampered data flagged it via full-ledger validation |
| Mesh sync convergence | Full swarm consensus (all units holding an identical ledger) reached in **2 sync rounds**, consistently |

### Security: Consensus Hardening (`dag_consensus.py`)

The baseline DAG ledger above detects tampering *after* accepting it — good enough to know something is wrong, but the bad data has already entered the mesh. `dag_consensus.py` closes that gap: incoming data is validated **before** it's accepted into a unit's ledger.

Demonstrated result from the module's self-test:
- Baseline `merge()`: tampered node **is accepted** into the ledger; only a manual `validate_full_dag()` scan catches it afterward
- Hardened `merge()`: tampered node is **rejected at the door** (`{'accepted': 2, 'rejected': 1}`) — the ledger never goes invalid in the first place
- After repeated bad data from the same source, that source is automatically **quarantined** and all further data from it is rejected without inspection — tying directly into the existing `drone.compromised` flag already used by the Boids separation logic

### Federated Learning (`adaptive_agent.py`)

Mode B's decision-making has moved from a 2-boolean rule table to a richer, persistent, **mesh-shared** learning agent:

- State space now includes threat/obstacle distance (near/mid/far), local crowd density, and battery level — not just binary flags
- **Federation**: when two units are within mesh range, they don't just sync mission data — they blend their learned Q-tables. Demonstrated result: a "rookie" agent that has *never itself encountered a threat* correctly learns the veteran's evasive action purely through federation
- Q-tables persist to disk between sessions (`save_q_table()` / `load_q_table()`), so the swarm doesn't relearn from zero on every run

*A fully instrumented benchmark mode (automated success-rate, collision-rate, and latency logging across many runs) was the top open item in the previous version of this README — it's what `benchmark.py` above now provides.*

## Vision: Where SwarmOS Is Going

What's in this repository is a **proof-of-concept**, deliberately kept lightweight so it could be built and tested solo, without funding, on a basic laptop. It is the first step toward a much larger system: a **fully decentralized AI drone swarm secured by blockchain/DAG principles**, designed from day one to serve both military and civilian missions on the same underlying platform.

### The full system this is building toward

**1. Decentralized AI, not scripted rules.**
Coordination started on two intentionally simple, transparent models — Boids-based collective flocking (Mode A) and independent rule-based agents (Mode B) — chosen specifically so the *coordination architecture* could be proven first, without hiding it behind a black-box model. Mode B has since taken its first real step past that baseline: a federated, persistent learning agent (above) replaces the fixed rule table, so units reason from experience — their own and their neighbors' — rather than a fixed formula, while still requiring no central controller. Both modes stay decentralized by design: no single drone, ground station, or cloud server is required for the swarm to keep functioning.

**2. Blockchain and DAG — used only where they earn their cost.**
A full blockchain on every drone would be too heavy for real flight hardware, so the design is deliberately **lightweight and selective**: a hash-linked DAG ledger records only mission-critical events — launch, threat detection, unit loss, data handoff — not continuous telemetry, and now validates data at ingestion rather than after the fact (above). The target architecture extends this further into a proper multi-unit **DAG-based consensus layer** (in the spirit of IOTA's Tangle) with reputation-weighted confirmation across the whole mesh, not just pairwise merges. Blockchain/DAG is used here as a **data-integrity and survivability layer**, not as a buzzword — it exists specifically so mission data cannot be silently altered or lost when units are damaged, jammed, or captured in contested environments.

**3. Why this matters now.**
Drone swarms are being adopted rapidly in both domains at once — militaries need coordination that survives jamming, GPS-denial, and unit losses in contested environments; civilian operators (agriculture, disaster response, infrastructure inspection) need the same resilience against far more mundane failures (weather, battery loss, hardware faults). Both domains are converging on the same unsolved problem: **coordination and data integrity that don't depend on a single point of control.** SwarmOS is built so the same core engine — decentralized coordination, tamper-evident mesh data, adaptive coverage — serves both, with only the mission payload and objective changing between a defense deployment and a civilian one.

### Path to deployment

```
1. Software simulation (this repository)
   → Prove the coordination, resilience, and mesh-ledger logic in a
     controlled, fast-iterating environment, backed by an automated
     benchmark suite. COMPLETE.

2. Emulation
   → Add physics-realistic flight dynamics (aerodynamics, wind, battery
     drain, sensor noise — partially modeled already) and extend the
     current federated adaptive agents and ingestion-time-hardened DAG
     merge into a full multi-unit consensus layer, still fully in
     software. IN PROGRESS.

3. Hardware prototype (MVP)
   → Port the proven coordination logic onto real flight controllers
     (PX4/Pixhawk), migrating the real-time control layer to C++, and test
     the software on a small fleet of existing commercial drones first —
     validating that the coordination logic holds up outside simulation
     before committing to custom hardware.

4. Dedicated hardware + mass-scale deployment
   → Once the software is validated on existing hardware, design
     purpose-built drone hardware around SwarmOS specifically — optimized
     for the mesh communication range, onboard compute needs, and
     dual-use payload requirements the software demands — and scale to
     multi-swarm, mass deployment across both defense and civilian
     missions.
```

This order is deliberate: **software first, on hardware that already exists, before any custom hardware is designed.** It's the cheapest and fastest way to validate whether the coordination and consensus design actually holds up in the real world before scaling capital, time, and hardware risk.

### Hardware-agnostic by design

A core design goal for SwarmOS is that the coordination software itself should not be tied to any specific drone or airframe. The intent is for the same software layer to run on **existing commercial and industrial drones regardless of size, weight class, or manufacturer** — from small quadcopters up through heavy-lift platforms (50kg+ payload-class drones included) — by targeting the coordination and communication layer independently of flight-controller hardware, rather than requiring a proprietary airframe from day one. This is what makes the "existing hardware first" step in the roadmap above realistic: the same SwarmOS coordination logic should be portable across whatever drones are already available, with only a thin integration layer needed per flight-controller/hardware combination. Purpose-built dedicated hardware, described in stage 4 above, comes later — designed around the software once it's proven, not as a prerequisite for the software to work.

## Roadmap

- Physics-realistic flight dynamics (aerodynamics, wind resistance, battery constraints — partially modeled)
- Hardware-in-the-loop testing on real flight controllers (PX4/Pixhawk), migrating the real-time control layer to C++
- Adaptive coverage redirection — units automatically retask toward under-covered zones based on live heatmap data
- Multi-swarm coordination (swarm-of-swarms)
- Full mesh-wide DAG consensus (beyond pairwise hardened merge) with reputation-weighted confirmation

## About the Builder

Built solo by [Raghavendra Pratap Singh] — a self-taught, India-based developer exploring autonomous systems and swarm intelligence, without a formal CS degree or company backing. This project is part of a broader portfolio aimed at advancing autonomous robotics research toward long-term goals in space exploration and distributed robotic systems.
