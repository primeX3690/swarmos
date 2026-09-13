
from ursina import Entity, Vec3, color, Text
import random
import math
from config import (
    GROUND_SIZE,
    FLIGHT_HEIGHT_MIN,
    FLIGHT_HEIGHT_MAX,
    DRONE_SPEED,
    MODE_A_COLOR,
    TAKEOFF_SPEED,
    LANDING_SPEED,
    GNSS_DRIFT_RATE,
)


class Drone(Entity):
    def __init__(self, drone_id ):
        spawn_x = random.uniform(-GROUND_SIZE / 2, GROUND_SIZE / 2)
        spawn_z = random.uniform(-GROUND_SIZE / 2, GROUND_SIZE / 2)

        super().__init__(
            model='cube',
            scale=(0.4, 0.15, 0.6),
            color=color.rgba(*MODE_A_COLOR),
            position=(spawn_x, 0.3, spawn_z),
        )

        self.id = drone_id
        self.ledger  = []

        self.gnss_denied = False
        self.target_flight_height = random.uniform(FLIGHT_HEIGHT_MIN, FLIGHT_HEIGHT_MAX)
        self.estimated_position = Vec3(spawn_x, self.target_flight_height, spawn_z)



        angle = random.uniform(0, 360)
        self.velocity = Vec3(
            math.cos(math.radians(angle)),
            0,
            math.sin(math.radians(angle)),
        ) * DRONE_SPEED

        self.decision_timer = random.randint(0, 60)
        self.battery = 100.0

        self.target_flight_height = random.uniform(FLIGHT_HEIGHT_MIN, FLIGHT_HEIGHT_MAX)
        self.state = 'grounded'   # grounded -> takeoff -> flying -> landing -> landed
        self.takeoff_delay = random.uniform(0, 2.0)
        self.landing_delay = random.uniform(0, 1.0)

        # from mesh_comms import create_genesis_block
        # self.ledger = [create_genesis_block()]
        # self.mission_data = {'target': None, 'status': 'active'}

        # new added 
        from dag_consensus import ConsensusDAGLedger
        self.dag = ConsensusDAGLedger(owner_id=self.id)
        self.mission_data = {'target': None, 'status' :'active' }
        
        
        self.signal_strength = 100
        self.current_frequency = random.choice([1, 2, 3, 4, 5])
        self.jam_hop_timer = 1.0
        self.home_position = Vec3(spawn_x, self.target_flight_height, spawn_z)

        self.compromised = False

        self.label = Text(
            text=f"D{self.id}",
            parent=self,
            position=(0, 0.6, 0),
            scale=40,
            billboard=True,
            color=color.white,
        )

    def start_landing(self):
        if self.state == 'flying':
            self.state = 'landing'


    def reactivate(self):
        if self.state in ('landed' , 'landing'):
            self.state = 'takeoff'


    def start_rth(self):
        if self.state == 'flying':
            self.state = 'rth'



    # def move(self, dt):
    def move(self, dt , wind_force=None):

        # --- Grounded: waiting for takeoff ---
        if self.state == 'grounded':
            self.takeoff_delay -= dt
            if self.takeoff_delay <= 0:
                self.state = 'takeoff'
            self.label.text = f"D{self.id} | GROUND"
            return



        if self.state == 'rth':
            direction = self.home_position - self.position
            dist = direction.length()
            self.label.text = f"D{self.id} | RTH (sig:{int(self.signal_strength)}%)"
            if dist > 0.3:
                direction = direction.normalized()
                self.position += direction * DRONE_SPEED * dt
                self.look_at(self.position + direction)
            else:
                self.state = 'landed'
                self.signal_strength = 100
            return





        # --- Takeoff: rise smoothly to flight height ---
        if self.state == 'takeoff':
            self.y += TAKEOFF_SPEED * dt
            self.label.text = f"D{self.id} | TAKEOFF"
            if self.y >= self.target_flight_height:
                self.y = self.target_flight_height
                self.state = 'flying'
            return

        # --- Landing: descend smoothly to ground ---
        if self.state == 'landing':
            self.landing_delay -= dt
            if self.landing_delay > 0:
                self.label.text = f"D{self.id} | HOLD"
                return

            self.velocity *= 0.9
            self.y -= LANDING_SPEED * dt
            self.label.text = f"D{self.id} | LANDING"

            if self.y <= 0.3:
                self.y = 0.3
                self.velocity = Vec3(0, 0, 0)
                self.state = 'landed'
            return

        # --- Landed: stay still until reactivated ---
        if self.state == 'landed':
            self.label.text = f"D{self.id} | LANDED"
            return


        if self.gnss_denied:
            wobble = Vec3(
                random.uniform(-0.4, 0.4),
                0,
                random.uniform(-0.4, 0.4),
            )
            self.velocity += wobble





        # --- Flying: normal behavior ---

        if wind_force is not None:
            self.velocity += wind_force * dt
        self.position += self.velocity * dt


        half = GROUND_SIZE / 2
        if abs(self.x) > half:
            self.velocity.x *= -1
        if abs(self.z) > half:
            self.velocity.z *= -1

        if self.velocity.length() > 0.01:
            self.look_at(self.position + self.velocity)

        # if self.velocity.length() > 0.01:
        #     from ursina import lerp
        #     target_rotation_y = math.degrees(math.atan2(self.velocity.x, self.velocity.z))
        #     self.rotation_y = lerp(self.rotation_y, target_rotation_y, 6 * dt)



        if self.gnss_denied:
            drift = Vec3(
                random.uniform(-GNSS_DRIFT_RATE, GNSS_DRIFT_RATE),
                0,
                random.uniform(-GNSS_DRIFT_RATE, GNSS_DRIFT_RATE),
            )
            self.estimated_position += self.velocity * dt + drift
        else:
            self.estimated_position = self.position






        
        


        self.label.text = f"D{self.id} | {len(self.ledger)}blk | Bat:{int(self.battery)}%"



    