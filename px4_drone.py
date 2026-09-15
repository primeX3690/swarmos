import threading
import time
from ursina import Vec3
from pymavlink import mavutil
from dag_consensus import ConsensusDAGLedger


class PX4Drone:
    def __init__(self, drone_id, port):
        self.id = drone_id
        self.port = port
        self.position = Vec3(0, 0, 0)
        self.velocity = Vec3(0, 0, 0)
        self.compromised = False
        self.state = "flying"
        self.battery = 100.0

        self.ledger = []
        self.mission_data = {}
        self.dag = ConsensusDAGLedger(owner_id=drone_id)
        self.rl_agent = None
        self.decision_timer = 0

        self._conn = mavutil.mavlink_connection(f'udp:127.0.0.1:{port}')
        self._conn.wait_heartbeat()
        print(f"[PX4Drone {self.id}] connected on port {port}")

        self._running = True
        self._telemetry_thread = threading.Thread(
            target=self._telemetry_loop, daemon=True
        )
        self._telemetry_thread.start()

        self._offboard_ready = False
        self._arm_and_offboard()

    def _telemetry_loop(self):
        while self._running:
            msg = self._conn.recv_match(type='LOCAL_POSITION_NED', blocking=True, timeout=1)
            if msg:
                self.position = Vec3(msg.x, -msg.z, msg.y)

    def _send_velocity_setpoint(self, vx, vy, vz):
        type_mask = 0b0000111111000111
        self._conn.mav.set_position_target_local_ned_send(
            0, self._conn.target_system, self._conn.target_component,
            mavutil.mavlink.MAV_FRAME_LOCAL_NED, type_mask,
            0, 0, 0,
            vx, vy, vz,
            0, 0, 0,
            0, 0
        )

    def _arm_and_offboard(self):
        for _ in range(40):
            self._send_velocity_setpoint(0, 0, 0)
            time.sleep(0.05)

        self._conn.mav.command_long_send(
            self._conn.target_system, self._conn.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
            1, 393216, 0, 0, 0, 0, 0
        )
        time.sleep(0.3)
        self._conn.mav.command_long_send(
            self._conn.target_system, self._conn.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
            1, 0, 0, 0, 0, 0, 0
        )
        self._offboard_ready = True
        print(f"[PX4Drone {self.id}] OFFBOARD + ARMED")

    def look_at(self, target):
        pass

    def move(self, dt, wind_force=None):
        vx = self.velocity.x
        vy = self.velocity.z
        vz = -self.velocity.y
        self._send_velocity_setpoint(vx, vy, vz)

    def shutdown(self):
        self._running = False
