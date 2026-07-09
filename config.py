# ============================================
# CONFIG — SwarmOS global settings
# ============================================

# --- World ---
GROUND_SIZE = 40          # ground plane ki width/depth
FLIGHT_HEIGHT_MIN = 2     # drones is height ke neeche nahi jayenge
FLIGHT_HEIGHT_MAX = 6     # drones is height ke upar nahi jayenge

# --- Swarm ---
SWARM_SIZE = 15
DRONE_SPEED = 4.0

# --- Mode A: Boids (Collective Brain) ---
SEPARATION_RADIUS = 2.0
ALIGNMENT_RADIUS = 5.0
COHESION_RADIUS = 6.0

SEPARATION_WEIGHT = 1.8
ALIGNMENT_WEIGHT = 1.0
COHESION_WEIGHT = 0.8

STEER_SMOOTHING = 0.05    # kitni jaldi velocity naye direction mein badle

# --- Mode B: Individual Brain ---
DECISION_INTERVAL_MIN = 60   # frames — naya random decision lene se pehle minimum wait
DECISION_INTERVAL_MAX = 150  # frames — maximum wait

# --- Colors ---
MODE_A_COLOR = (0.1, 0.8, 1.0, 1)   # cyan = collective
MODE_B_COLOR = (1.0, 0.5, 0.1, 1)   # orange = individual


# --- Obstacle ---
OBSTACLE_POSITION = (0, 3, 0)
OBSTACLE_RADIUS = 3.0
OBSTACLE_AVOID_WEIGHT = 5.0

# --- Threat ---
THREAT_POSITION = (10, 3, 10)
THREAT_RADIUS = 6.0
THREAT_FLEE_WEIGHT = 3.0
THREAT_SURROUND_RADIUS = 5.0


ENABLE_HEATMAP = False   # H key se toggle hoga   
TAKEOFF_SPEED = 0.5    # takeoff ke speed 
LANDING_SPEED = 0.5

FORMATION_SPEED = 9.0  # formation follow krte time speed - patrol se tej honi chahiye


COMMS_RADIUS = 8.0      # kitni door tak drones data share kar sakte hain
SYNC_INTERVAL = 20      # kitne frames baad sync check ho (performance ke liye)


JAMMER_POSITION = (-12, 3, -12)
JAMMER_RADIUS = 7.0
FREQUENCIES = [1, 2, 3, 4, 5]
SIGNAL_DROP_RATE = 35      # per second jab jammer zone ke andar ho
SIGNAL_RECOVERY_RATE = 25  # per second jab bahar ho
HOP_SUCCESS_CHANCE = 0.6   # frequency hop ka chance safe channel milne ka
