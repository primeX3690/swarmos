# SwarmOS — Decentralized AI Swarm Drone System (Blockchain/DAG-Secured)

**A decentralized swarm AI drone platform demonstrating collective and individual on-device intelligence, blockchain/DAG-inspired tamper-evident mesh networking, and mission resilience — built for both military and civilian dual-use deployment.**

---

## Key Advantages

- **Fully decentralized** — no ground station, cloud server, or single lead drone is required for the swarm to coordinate; every unit can independently continue the mission
- **Two interchangeable AI modes** — Collective (Boids-based emergent flocking) and Individual (independent rule-based agents) — letting the same platform switch coordination strategy based on mission needs or communication conditions
- **Blockchain/DAG-inspired data integrity** — mission events are hash-chained and replicated across the mesh, so data cannot be silently altered and does not depend on any single drone surviving
- **Lightweight by design** — the blockchain/DAG layer only secures mission-critical events, not continuous telemetry, keeping it viable for real flight hardware rather than a heavy, impractical full-blockchain implementation
- **Dual-use from the ground up** — the same coordination engine serves both defense (reconnaissance, contested-environment resilience) and civilian (agriculture, disaster response, infrastructure inspection) missions

---

## Problem

Real-world drone swarms — whether used for defense reconnaissance, disaster response, or agricultural monitoring — depend on coordination that must survive failure. Most existing systems rely on centralized control, which creates a single point of failure: if the control node or a critical unit is lost, the mission can collapse.

SwarmOS explores an alternative: a swarm that coordinates collectively, shares mission data across a mesh network, and continues its mission even when individual units are destroyed or disconnected.

## What This Project Demonstrates

SwarmOS is a real-time 3D simulation (Python + Ursina Engine) built entirely solo, without any external funding or team, on consumer-grade hardware. It models eleven distinct capabilities relevant to real swarm deployment:

1. **Autonomous takeoff & landing sequencing** — staggered, realistic launch and recovery
2. **Collective Intelligence (Mode A)** — emergent flocking behavior via the Boids algorithm (separation, alignment, cohesion) — no central controller
3. **Individual Intelligence (Mode B)** — independent, rule-based decision-making per unit, for direct behavioral contrast
4. **Dynamic Formation Flying** — Grid, Circle, and V formations, maintained while patrolling a moving path
5. **Real-time Obstacle Avoidance** — swarm reroutes around static obstacles without breaking coordination
6. **Threat Response** — two configurable behaviors: *flee* (evasion) and *surround* (containment)
7. **Fault Tolerance / Resilience** — when a unit is destroyed, the swarm automatically re-forms without manual intervention
8. **Mesh-Networked Data Sharing** — units within communication range replicate mission data to each other in real time (visualized as live connection links)
9. **Hash-Linked Mission Ledger** — every mission event (launch, threat detected, unit lost) is recorded in a tamper-evident, hash-chained ledger per unit — inspired by blockchain/DAG principles, ensuring mission data cannot be silently altered
10. **Data Survivability** — before a unit is lost, its ledger is force-synced to the nearest surviving unit, so mission history is never dependent on any single node
11. **Area Coverage Tracking** — a real-time visual record of which zones the swarm has covered, relevant to both reconnaissance verification and field monitoring

## Dual-Use Design: Defense + Civilian

SwarmOS was deliberately designed around **two operating intelligence modes** that map directly onto two use-case families:

| Mode | Behavior | Defense / Security Application | Civilian Application |
|---|---|---|---|
| **Mode A — Collective Brain** | Emergent, self-organizing group behavior (Boids) | Coordinated reconnaissance, saturation coverage, group maneuvering under threat | Coordinated field surveying, synchronized agricultural spraying/monitoring |
| **Mode B — Individual Brain** | Independent, decentralized decision-making | Resilient operation when communications are degraded or jammed | Distributed sensor coverage where units operate autonomously across a wide area |

The same underlying engine — formation flying, obstacle avoidance, threat response, mesh data-sharing, and the tamper-evident ledger — supports both a **tactical defense scenario** (area denial, reconnaissance, threat interception) and a **civilian scenario** (disaster search-and-rescue, crop monitoring, infrastructure inspection). This is intentional: the coordination and resilience problem is identical across both domains — only the payload and mission objective change.

## Why This Matters

Most swarm demos show flocking. Few demonstrate what happens when the mission is attacked, a unit is destroyed, or the network is under threat — and fewer still show how mission-critical data survives that failure. SwarmOS was built to prove the coordination and resilience layer first, before investing in mission-specific payloads or hardware.

## Tech Stack

- **Language:** Python
- **Engine:** Ursina (built on Panda3D) for real-time 3D rendering
- **Core Algorithms:** Boids flocking, rule-based individual agents, formation-offset geometry with patrol-path rotation, SHA-256 hash-chaining for the mission ledger
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
| `1` / `2` / `3` | Grid / Circle / V formation (patrolling) |
| `O` | Toggle obstacle + avoidance |
| `T` | Toggle threat — flee behavior |
| `Y` | Toggle threat — surround behavior |
| `K` | Destroy a random unit (test resilience) |
| `H` | Toggle area-coverage heatmap |
| `L` | Initiate landing sequence |

## Observed Results (Manual Testing)

These are direct observations from running the simulation locally — not a formal automated benchmark suite, but a transparent record of what the current build demonstrates:

| Metric | Observation |
|---|---|
| Swarm size tested | Up to 25 units, stable in real time on consumer hardware (Ryzen 3, 8GB RAM, integrated graphics) |
| Formation accuracy | Grid, Circle, and V formations reliably converge and hold shape while patrolling a moving path |
| Collision avoidance | No inter-unit collisions observed during flocking (Boids separation rule) across repeated test runs |
| Obstacle avoidance | Swarm consistently reroutes around a static obstacle without breaking formation cohesion |
| Recovery after unit loss | Formation re-computes and re-stabilizes within a few seconds of a unit being destroyed, with no manual intervention |
| Data survivability | Mission ledger is force-synced to the nearest surviving unit before a unit is removed — zero mission-data loss observed across repeated failure tests |
| Mesh sync range | Units within configurable communication radius (default 10 units) reliably replicate ledger state in real time |

*A fully instrumented benchmark mode (automated success-rate, collision-rate, and latency logging across many runs) is planned — see Roadmap.*

## Vision: Where SwarmOS Is Going

What's in this repository is a **proof-of-concept**, deliberately kept lightweight so it could be built and tested solo, without funding, on a basic laptop. It is the first step toward a much larger system: a **fully decentralized AI drone swarm secured by blockchain/DAG principles**, designed from day one to serve both military and civilian missions on the same underlying platform.

### The full system this is building toward

**1. Decentralized AI, not scripted rules.**
Today, coordination runs on two intentionally simple, transparent models — Boids-based collective flocking (Mode A) and independent rule-based agents (Mode B) — chosen specifically so the *coordination architecture* could be proven first, without hiding it behind a black-box model. The target system keeps this same two-mode architecture, but replaces the decision logic in each mode with onboard, adaptive intelligence per drone — so every unit reasons about its environment and mission state rather than following a fixed formula, while still requiring no central controller. Both modes stay decentralized by design: no single drone, ground station, or cloud server is required for the swarm to keep functioning.

**2. Blockchain and DAG — used only where they earn their cost.**
A full blockchain on every drone would be too heavy for real flight hardware, so the design is deliberately **lightweight and selective**: a hash-linked ledger (proven here with SHA-256 block-chaining) records only mission-critical events — launch, threat detection, unit loss, data handoff — not continuous telemetry. The target architecture extends this into a proper **DAG-based consensus layer** (in the spirit of IOTA's Tangle) specifically for the mesh-replication problem: letting nearby units validate and propagate each other's mission data in parallel, without a central authority, and without the overhead of full blockchain mining. Blockchain/DAG is used here as a **data-integrity and survivability layer**, not as a buzzword — it exists specifically so mission data cannot be silently altered or lost when units are damaged, jammed, or captured in contested environments.

**3. Why this matters now.**
Drone swarms are being adopted rapidly in both domains at once — militaries need coordination that survives jamming, GPS-denial, and unit losses in contested environments; civilian operators (agriculture, disaster response, infrastructure inspection) need the same resilience against far more mundane failures (weather, battery loss, hardware faults). Both domains are converging on the same unsolved problem: **coordination and data integrity that don't depend on a single point of control.** SwarmOS is built so the same core engine — decentralized coordination, tamper-evident mesh data, adaptive coverage — serves both, with only the mission payload and objective changing between a defense deployment and a civilian one.

### Path to deployment

```
1. Software simulation (this repository)
   → Prove the coordination, resilience, and mesh-ledger logic in a
     controlled, fast-iterating environment. COMPLETE.

2. Emulation
   → Add physics-realistic flight dynamics (aerodynamics, wind, battery
     drain, sensor noise) and replace the current rule-based intelligence
     with real onboard adaptive models and a working DAG consensus layer,
     still fully in software.

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

- Physics-realistic flight dynamics (aerodynamics, wind resistance, battery constraints)
- Hardware-in-the-loop testing on real flight controllers (PX4/Pixhawk), migrating the real-time control layer to C++
- Adaptive coverage redirection — units automatically retask toward under-covered zones based on live heatmap data
- Multi-swarm coordination (swarm-of-swarms)
- ML-based adaptive formation and threat-response selection

## About the Builder

Built solo by [Raghavendra Pratap Singh] — a self-taught, India-based developer exploring autonomous systems and swarm intelligence, without a formal CS degree or company backing. This project is part of a broader portfolio aimed at advancing autonomous robotics research toward long-term goals in space exploration and distributed robotic systems.
