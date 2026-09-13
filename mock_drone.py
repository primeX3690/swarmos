"""
mock_drone.py
--------------
Ek lightweight, engine-agnostic drone stand-in — SwarmOS ke asli Drone
(drone.py) jaisa hi behave karta hai (id, position, velocity, ledger, dag,
compromised flag) lekin Ursina Entity/window ke bina bhi ban sakta hai.

Isse hum boids.py, formation.py, threat.py, obstacle.py, dag_ledger.py,
mesh_comms.py ke ASLI functions ko bina-window (headless) call kar sakte
hain — benchmark.py isi trick ka use karta hai taaki metrics 100% wahi
logic test karein jo main.py mein chalta hai, koi reimplementation nahi.
"""
import random
from ursina import Vec3
from dag_ledger import DAGLedger
from config import FLIGHT_HEIGHT_MIN, FLIGHT_HEIGHT_MAX


class MockDrone:
    def __init__(self, drone_id, spawn_range=20):
        self.id = drone_id
        # BUGFIX: pehle yahan y hamesha 0.3 (ground height) pin thi. Asli
        # drone.py mein 'flying' state ke drones target_flight_height
        # (FLIGHT_HEIGHT_MIN..MAX, matlab 2-6) pe udte hain — threat/obstacle
        # bhi usi height-band (y=3) pe hote hain. y=0.3 pin karne se drone
        # threat/obstacle se hamesha ~2.7 units 'door' dikhta tha sirf height
        # mismatch ki wajah se — XZ position bilkul sahi converge ho raha
        # tha. Isi wajah se threat_surround test ka error galat aaya tha.
        self.target_flight_height = random.uniform(FLIGHT_HEIGHT_MIN, FLIGHT_HEIGHT_MAX)
        self.position = Vec3(
            random.uniform(-spawn_range, spawn_range),
            self.target_flight_height,
            random.uniform(-spawn_range, spawn_range),
        )
        self.velocity = Vec3(0, 0, 0)
        self.compromised = False
        self.state = "flying"
        self.battery = 100.0

        # asli Drone jaisa hi ledger + DAG
        self.ledger = []
        self.mission_data = {}
        self.dag = DAGLedger()

        # adaptive_agent.py ke liye slot (lazily attach hoga)
        self.rl_agent = None
        self.decision_timer = 0

    def look_at(self, target):
        """No-op — headless benchmark ko visual orientation ki zaroorat nahi,
        lekin formation.py ka move_toward_formation() isse call karta hai."""
        pass

    def move(self, dt, wind_force=None):
        """drone.py ke Drone.move() jaisa hi simplified integrator."""
        self.position += self.velocity * dt
        if wind_force is not None:
            self.position += wind_force * dt * 0.1
        self.position.y = self.target_flight_height  # level flight AT ITS OWN flying height