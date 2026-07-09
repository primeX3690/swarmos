from ursina import (
    Ursina, Entity, EditorCamera, DirectionalLight, AmbientLight,
    Text, color, camera, window, time, Vec3, destroy,
)
from heatmap import create_heatmap_grid, update_heatmap
from mesh_comms import sync_chains, add_block
from config import COMMS_RADIUS, SYNC_INTERVAL
from ursina import Entity

from ursina import Mesh
import time as pytime


import math
import random

from config import SWARM_SIZE, GROUND_SIZE, MODE_A_COLOR, MODE_B_COLOR, OBSTACLE_POSITION, THREAT_POSITION
from drone import Drone
from boids import apply_boids_rules
from mode_b import apply_individual_behavior
from formation import get_formation_offsets, rotate_offset, move_toward_formation
from obstacle import create_obstacle, avoid_obstacle
from threat import create_threat, flee_threat, surround_threat

from mesh_comms import validate_chain, hacker_inject_fake_command
from jammer import create_jammer_zone, update_signal


jammer_entity = create_jammer_zone()


def show_notification(message):
    notification_label.text = message
    notification_label.color = color.red
    invoke(clear_notification, delay=2.5)


def clear_notification():
    notification_label.text = ""


from ursina import invoke






app = Ursina(vsync=False)
window.color = color.rgb32(10,12,20)




window.title = "SwarmOS — Collective vs Individual Intelligence"
window.color = color.rgb(10, 12, 20)
window.fps_counter.enabled = True













ground = Entity(
    model='plane',
    scale=(GROUND_SIZE, 1, GROUND_SIZE),
    color=color.rgb32(18, 22, 32),
    unlit=True,
)

EditorCamera()
camera.position = (0, 28, -18)
camera.rotation_x = 55
camera.fov = 80


heatmap_cells, heatmap_visits, heatmap_cell_size = create_heatmap_grid()
heatmap_on = False

obstacle_entity = create_obstacle()
threat_entity = create_threat()
obstacle_entity.enabled = False
threat_entity.enabled = False

# ------------------------------------------------
# Swarm spawn
# ------------------------------------------------
drones = [Drone(i) for i in range(SWARM_SIZE)]
mission_start_time = pytime.time()
last_known_elapsed = 0

# ------------------------------------------------
# State
# ------------------------------------------------
current_mode = 'A'           # 'A' = collective, 'B' = individual
formation_mode = False
current_formation = 'grid'
formation_offsets = []

patrol_angle = 0.0
patrol_radius = 12
patrol_speed = 0.4

obstacle_on = False
threat_state = 'off'         # 'off', 'flee', 'surround'

mode_label = Text(
    text="MODE A — Collective Brain (Boids)",
    position=(-0.85, 0.45),
    scale=1.3,
    color=color.cyan,
)

info_label = Text(
    text="M=Mode  1/2/3=Formation  O=Obstacle  T=Flee  Y=Surround  K=Kill Drone",
    position=(-0.85, 0.40),
    scale=0.8,
    color=color.white,
)


info_label = Text(
    text="M=Mode 1/2/3=Formation O=Obstacle T=Flee Y=Surround K=Kill H=Heatmap",
    position=(-0.85, 0.40),
    scale=0.7,
    color=color.white,
)



count_label = Text(
    text=f"Active Drones: {len(drones)}",
    position=(-0.85, 0.36),
    scale=0.8,
    color=color.light_gray,
)


status_label = Text(
    text="Obstacle: OFF | Threat: OFF",
    position=(-0.85, 0.32),
    scale=0.8,
    color=color.orange,
)

sync_timer = 0

comm_lines = [] # visual lines jo dikhayengi ki kaun sa drone data share kar rhe hain
ledger_label = Text(
    text="Mesh Ledger: syncing...",
    position=(-0.85, 0.28),
    scale=0.75,
    color=color.lime,
)



notification_label = Text(
    text="",
    position=(0, -0.3, 0),
    origin=(0, 0),
    scale=1.4,
    color=color.yellow,
    background=True,
)


threat_alert = Text(
    text="",
    position=(-0.15, 0.48),
    scale=1.5,
    color=color.red,
    origin=(0, 0),
)

# ------------------------------------------------
# Main update loop
# ------------------------------------------------
def update():
    global formation_offsets, patrol_angle
    global sync_timer, comm_lines, mission_start_time , heatmap_on, last_known_elapsed

# Threat alert — pulsing effect using sin wave
    if threat_state != 'off':
        pulse = abs(math.sin(time.dt * 5 + patrol_angle * 3))
        threat_alert.text = f" !! THREAT DETECTED — Mode: {threat_state.upper()}"
        threat_alert.color = color.rgba(255, 30, 30, int(150 + pulse * 100))
        threat_entity.scale = 1.2 + pulse * 0.4   # threat sphere bhi pulse karega
    else:
        threat_alert.text = ""

    

    if formation_mode:
        if not formation_offsets or len(formation_offsets) != len(drones):
            formation_offsets = get_formation_offsets(current_formation, len(drones))

        patrol_angle += patrol_speed * time.dt
        anchor_x = math.cos(patrol_angle) * patrol_radius
        anchor_z = math.sin(patrol_angle) * patrol_radius
        anchor_pos = Vec3(anchor_x, 4, anchor_z)
        heading = patrol_angle + math.pi / 2

        

        for i, d in enumerate(drones):
            if d.state != 'flying':
                d.move(time.dt)
                continue

            rx, rz = rotate_offset(formation_offsets[i], heading)
            target = anchor_pos + Vec3(rx, 0, rz)
            move_toward_formation(d, target, time.dt)
            if obstacle_on:
                avoid_obstacle(d, Vec3(*OBSTACLE_POSITION))
                d.position += d.velocity * time.dt * 0.3

                

    else:
        

        for d in drones:
            if d.state != 'flying':
                d.move(time.dt)
                continue

            if current_mode == 'A':
                apply_boids_rules(d, drones)
                d.color = color.rgba(*MODE_A_COLOR)
            else:
                apply_individual_behavior(d)
                d.color = color.rgba(*MODE_B_COLOR)

            if obstacle_on:
                avoid_obstacle(d, Vec3(*OBSTACLE_POSITION))
            if threat_state == 'flee':
                flee_threat(d, Vec3(*THREAT_POSITION))
            elif threat_state == 'surround':
                surround_threat(d, Vec3(*THREAT_POSITION), drones.index(d), len(drones))

            d.move(time.dt)


 # --- Mesh sync: paas-paas ke drones apna mission ledger replicate karte hain ---
    global sync_timer, comm_lines

    # Purani comm lines hata do (har frame refresh)
    for line in comm_lines:
        destroy(line)
    comm_lines = []

    sync_timer += 1
    if sync_timer >= SYNC_INTERVAL:
        sync_timer = 0
        for i in range(len(drones)):
            for j in range(i + 1, len(drones)):
                dist = (drones[i].position - drones[j].position).length()
                if dist < COMMS_RADIUS:
                    sync_chains(drones[i], drones[j])

    # Live visual: jo drones paas hain (COMMS_RADIUS ke andar), unke beech line dikhao
    for i in range(len(drones)):
        for j in range(i + 1, len(drones)):
            dist = (drones[i].position - drones[j].position).length()
            if dist < COMMS_RADIUS:
                line = Entity(
                    model=Mesh(
                        vertices=[drones[i].position, drones[j].position],
                        mode='line',
                        thickness=2,
                    ),
                    color=color.rgba(0, 255, 100, 120),
                )
                comm_lines.append(line)




    for d in drones:
        if d.state == 'flying':
            update_signal(d, time.dt)

        if not d.compromised and not validate_chain(d.ledger):
            d.compromised = True
            d.color = color.rgba(255, 0, 0, 255)
            d.label.text = f"D{d.id} | COMPROMISED - ISOLATED"

                

    if drones:
        # longest = max(drones, key=lambda d: len(d.ledger))
        # last_hash = longest.ledger[-1]['hash']
        # elapsed = round(pytime.time() - mission_start_time, 1)
        # ledger_label.text = f"Mesh Ledger: {len(longest.ledger)} blocks | Hash: {last_hash} | T+{elapsed}s" 
        # 
          longest = max(drones, key=lambda d: len(d.ledger))
          last_hash = longest.ledger[-1]['hash']
          any_flying = any(d.state == 'flying' for d in drones)
        #   elapsed = 0
          if any_flying:
              last_known_elapsed = round(pytime.time()-mission_start_time,1)
          elapsed = last_known_elapsed
            # elapsed = round(pytime.time() - mission_start_time, 1)
          ledger_label.text = f"Mesh Ledger: {len(longest.ledger)} blocks | Hash: {last_hash} | T+{elapsed}s"  
         




if heatmap_on:
        for d in drones:
            update_heatmap(d.position, heatmap_cells, heatmap_visits, heatmap_cell_size)




def input(key):
    global current_mode, formation_mode, current_formation, formation_offsets
    global obstacle_on, threat_state, heatmap_on


    if key in ('m', '1', '2', '3', 'o', 't', 'y'):
        reactivated_count = 0
        for d in drones:
            if d.state in ('landed', 'landing'):
                d.reactivate()
                reactivated_count += 1
        if reactivated_count > 0:
            show_notification(f"Reactivating {reactivated_count} drones")




    if key == 'm':
        formation_mode = False
        if current_mode == 'A':
            current_mode = 'B'
            mode_label.text = "MODE B — Individual Brain (Independent)"
            mode_label.color = color.orange
            show_notification("M — Switched to Individual Mode")
        else:
            current_mode = 'A'
            mode_label.text = "MODE A — Collective Brain (Boids)"
            mode_label.color = color.cyan
            show_notification("M — Switched to Collective Mode")

    if key == '1':
        formation_mode = True
        current_formation = 'grid'
        formation_offsets = []
        mode_label.text = "FORMATION — Grid (Patrolling)"
        mode_label.color = color.yellow
        show_notification("1 — Grid Formation Engaged")

    if key == '2':
        formation_mode = True
        current_formation = 'circle'
        formation_offsets = []
        mode_label.text = "FORMATION — Circle (Patrolling)"
        mode_label.color = color.yellow
        show_notification("2 — Circle Formation Engaged")

    if key == '3':
        formation_mode = True
        current_formation = 'v'
        formation_offsets = []
        mode_label.text = "FORMATION — V Shape (Patrolling)"
        mode_label.color = color.yellow
        show_notification("3 — V-Formation Engaged")

    if key == 'o':
        obstacle_on = not obstacle_on
        obstacle_entity.enabled = obstacle_on
        status_label.text = f"Obstacle: {'ON' if obstacle_on else 'OFF'} | Threat: {threat_state.upper()}"
        show_notification("O — Obstacle Avoidance " + ("Activated" if obstacle_on else "Deactivated"))

    if key == 't':
        threat_state = 'off' if threat_state == 'flee' else 'flee'
        threat_entity.enabled = (threat_state != 'off')
        status_label.text = f"Obstacle: {'ON' if obstacle_on else 'OFF'} | Threat: {threat_state.upper()}"
        show_notification("T — Threat FLEE Mode " + ("Activated" if threat_state == 'flee' else "Deactivated"))

    if key == 'y':
        threat_state = 'off' if threat_state == 'surround' else 'surround'
        threat_entity.enabled = (threat_state != 'off')
        status_label.text = f"Obstacle: {'ON' if obstacle_on else 'OFF'} | Threat: {threat_state.upper()}"
        show_notification("Y — Threat SURROUND Mode " + ("Activated" if threat_state == 'surround' else "Deactivated"))

    if key == 'k':
        if len(drones) > 1:
            victim = random.choice(drones)
            add_block(victim.ledger, 'DRONE_LOST')
            nearest = min(
                (d for d in drones if d.id != victim.id),
                key=lambda d: (d.position - victim.position).length()
            )
            sync_chains(victim, nearest)
            drones.remove(victim)
            destroy(victim)
            formation_offsets = []
            count_label.text = f"Active Drones: {len(drones)}"
            show_notification("K — Drone Lost: Data Replicated to Swarm")

    if key == 'h':
        heatmap_on = not heatmap_on
        if not heatmap_on:
            for row in heatmap_cells:
                for cell in row:
                    cell.color = color.rgba(0, 0, 0, 0)
        show_notification("H — Coverage Heatmap " + ("Enabled" if heatmap_on else "Disabled"))

    if key == 'l':
        for d in drones:
            d.start_landing()
        show_notification("L — Landing Sequence Initiated")




    if key == 'j':
        flying_drones = [d for d in drones if d.state == 'flying' and not d.compromised]
        if flying_drones:
            victim = random.choice(flying_drones)
            hacker_inject_fake_command(victim)
            show_notification(f"J — Simulated Hack on D{victim.id}")  

              
app.run()