# from ursina import Entity, Vec3, color
# import random
# import math
# from config import (
#     GROUND_SIZE,
#     FLIGHT_HEIGHT_MIN,
#     FLIGHT_HEIGHT_MAX,
#     DRONE_SPEED,
#     MODE_A_COLOR,
# )


# class Drone(Entity):
#     """
#     Ek single drone unit. Dono modes (A/B) isi class ko use karte hain —
#     sirf velocity update karne ka logic alag files (boids.py / mode_b.py) mein hai.
#     """

#     def __init__(self, drone_id):
#         spawn_x = random.uniform(-GROUND_SIZE / 2, GROUND_SIZE / 2)
#         spawn_y = random.uniform(FLIGHT_HEIGHT_MIN, FLIGHT_HEIGHT_MAX)
#         spawn_z = random.uniform(-GROUND_SIZE / 2, GROUND_SIZE / 2)

#         super().__init__(
#             model='cube',
#             scale=(0.5, 0.12, 0.7),
#             color=color.rgba(*MODE_A_COLOR),
#             position=(spawn_x, spawn_y, spawn_z),
#         )

#         self.id = drone_id

#         # random starting direction
#         angle = random.uniform(0, 360)
#         self.velocity = Vec3(
#             math.cos(math.radians(angle)),
#             0,
#             math.sin(math.radians(angle)),
#         ) * DRONE_SPEED

#         # Mode B ke liye — kab tak current direction pe chalna hai
#         self.decision_timer = random.randint(0, 60)

#         from mesh_comms import create_genesis_block
#         self.ledger = [create_genesis_block()]
#         self.mission_data = {'target': None, 'status': 'active'}

#         from ursina import Text
#         self.label = Text(
#             text=f"D{self.id}",
#             parent=self,
#             position=(0, 0.6, 0),
#             scale=40,
#             billboard=True,
#             color=color.white,
#         )
        

#     def move(self, dt):
#         """Position update + boundary bounce + orientation."""
#         self.position += self.velocity * dt

#         half = GROUND_SIZE / 2
#         if abs(self.x) > half:
#             self.velocity.x *= -1
#         if abs(self.z) > half:
#             self.velocity.z *= -1

#         # drone ko apni direction ki taraf face karwana (visual realism)
#         if self.velocity.length() > 0.01:
#             self.look_at(self.position + self.velocity)

#             self.label.text = f"D{self.id} | {len(self.ledger)}blk"




# from ursina import Entity, Vec3, color, Text
# import random
# import math
# from config import (
#     GROUND_SIZE,
#     FLIGHT_HEIGHT_MIN,
#     FLIGHT_HEIGHT_MAX,
#     DRONE_SPEED,
#     MODE_A_COLOR,
#     TAKEOFF_SPEED,
# )


# class Drone(Entity):
#     def __init__(self, drone_id):
#         spawn_x = random.uniform(-GROUND_SIZE / 2, GROUND_SIZE / 2)
#         spawn_z = random.uniform(-GROUND_SIZE / 2, GROUND_SIZE / 2)

#         super().__init__(
#             model='cube',
#             scale=(0.4, 0.15, 0.6),
#             color=color.rgba(*MODE_A_COLOR),
#             position=(spawn_x, 0.3, spawn_z),   # ground level se shuru
#         )

#         self.id = drone_id

#         angle = random.uniform(0, 360)
#         self.velocity = Vec3(
#             math.cos(math.radians(angle)),
#             0,
#             math.sin(math.radians(angle)),
#         ) * DRONE_SPEED

#         self.decision_timer = random.randint(0, 60)

#         self.target_flight_height = random.uniform(FLIGHT_HEIGHT_MIN, FLIGHT_HEIGHT_MAX)
#         self.state = 'grounded'  # 'grounded' -> 'takeoff' -> 'flying'
#         self.takeoff_delay = random.uniform(0, 2.0)  # har drone thoda alag time pe uthega

#         from mesh_comms import create_genesis_block
#         self.ledger = [create_genesis_block()]
#         self.mission_data = {'target': None, 'status': 'active'}

#         self.label = Text(
#             text=f"D{self.id}",
#             parent=self,
#             position=(0, 0.6, 0),
#             scale=40,
#             billboard=True,
#             color=color.white,
#         )

#     def move(self, dt):
#         # --- Takeoff sequencing ---
#         if self.state == 'grounded':
#             self.takeoff_delay -= dt
#             if self.takeoff_delay <= 0:
#                 self.state = 'takeoff'
#             self.label.text = f"D{self.id} | GROUND"
#             return  # abhi move nahi karega, bas wait kar raha hai

#         if self.state == 'takeoff':
#             self.y += TAKEOFF_SPEED * dt
#             self.label.text = f"D{self.id} | TAKEOFF"
#             if self.y >= self.target_flight_height:
#                 self.y = self.target_flight_height
#                 self.state = 'flying'
#             return  # takeoff ke dauran horizontal movement nahi

#         # --- Normal flying behavior (jo pehle tha) ---
#         self.position += self.velocity * dt

#         half = GROUND_SIZE / 2
#         if abs(self.x) > half:
#             self.velocity.x *= -1
#         if abs(self.z) > half:
#             self.velocity.z *= -1

#         if self.velocity.length() > 0.01:
#             self.look_at(self.position + self.velocity)

#         self.label.text = f"D{self.id} | {len(self.ledger)}blk"




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
)


class Drone(Entity):
    def __init__(self, drone_id):
        spawn_x = random.uniform(-GROUND_SIZE / 2, GROUND_SIZE / 2)
        spawn_z = random.uniform(-GROUND_SIZE / 2, GROUND_SIZE / 2)

        super().__init__(
            model='cube',
            scale=(0.4, 0.15, 0.6),
            color=color.rgba(*MODE_A_COLOR),
            position=(spawn_x, 0.3, spawn_z),
        )

        self.id = drone_id

        angle = random.uniform(0, 360)
        self.velocity = Vec3(
            math.cos(math.radians(angle)),
            0,
            math.sin(math.radians(angle)),
        ) * DRONE_SPEED

        self.decision_timer = random.randint(0, 60)

        self.target_flight_height = random.uniform(FLIGHT_HEIGHT_MIN, FLIGHT_HEIGHT_MAX)
        self.state = 'grounded'   # grounded -> takeoff -> flying -> landing -> landed
        self.takeoff_delay = random.uniform(0, 2.0)
        self.landing_delay = random.uniform(0, 1.0)

        from mesh_comms import create_genesis_block
        self.ledger = [create_genesis_block()]
        self.mission_data = {'target': None, 'status': 'active'}

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



    def move(self, dt):
        # --- Grounded: waiting for takeoff ---
        if self.state == 'grounded':
            self.takeoff_delay -= dt
            if self.takeoff_delay <= 0:
                self.state = 'takeoff'
            self.label.text = f"D{self.id} | GROUND"
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

        # --- Flying: normal behavior ---
        self.position += self.velocity * dt

        half = GROUND_SIZE / 2
        if abs(self.x) > half:
            self.velocity.x *= -1
        if abs(self.z) > half:
            self.velocity.z *= -1

        if self.velocity.length() > 0.01:
            self.look_at(self.position + self.velocity)

        self.label.text = f"D{self.id} | {len(self.ledger)}blk"


    # def move(self, dt):
    #     # --- Grounded: waiting for takeoff ---
    #     if self.state == 'grounded':
    #         self.takeoff_delay -= dt
    #         if self.takeoff_delay <= 0:
    #             self.state = 'takeoff'
    #         self.label.text = f"D{self.id} | GROUND"
    #         return

    #     # --- Takeoff: smooth ease-out rise ---
    #     if self.state == 'takeoff':
    #         remaining = self.target_flight_height - self.y
    #         step = max(remaining * 2.0, 0.3) * TAKEOFF_SPEED * dt
    #         self.y += step
    #         self.label.text = f"D{self.id} | TAKEOFF"
    #         if self.y >= self.target_flight_height - 0.05:
    #             self.y = self.target_flight_height
    #             self.state = 'flying'
    #         return

    #     # --- Landing: smooth ease-in descent ---
    #     if self.state == 'landing':
    #         self.landing_delay -= dt
    #         if self.landing_delay > 0:
    #             self.label.text = f"D{self.id} | HOLD"
    #             return

    #         # horizontal drift slow down karo landing ke dauran
    #         self.velocity *= 0.9

    #         distance_to_ground = self.y - 0.3
    #         step = max(distance_to_ground * 1.5, 0.2) * LANDING_SPEED * dt
    #         self.y -= step
    #         self.label.text = f"D{self.id} | LANDING"

    #         if self.y <= 0.35:
    #             self.y = 0.3
    #             self.velocity = Vec3(0, 0, 0)
    #             self.state = 'landed'
    #         return

    #     # --- Landed: stay still ---
    #     if self.state == 'landed':
    #         self.label.text = f"D{self.id} | LANDED"
    #         return

    #     # --- Flying: normal behavior ---
    #     self.position += self.velocity * dt

    #     half = GROUND_SIZE / 2
    #     if abs(self.x) > half:
    #         self.velocity.x *= -1
    #     if abs(self.z) > half:
    #         self.velocity.z *= -1

    #     if self.velocity.length() > 0.01:
    #         self.look_at(self.position + self.velocity)

    #     self.label.text = f"D{self.id} | {len(self.ledger)}blk"