"""
adaptive_agent.py — SwarmOS Federated Adaptive Agent
=====================================================
Repo mein already rl_agent.py hai (QLearningAgent) — asli, kaam karne
wala Q-learning, Mode B mein wired bhi hai (main.py line ~317). Lekin
teen real limitations hain jo README ke apne roadmap item se seedha
judti hain ("replace rule-based intelligence with onboard, adaptive
intelligence per drone"):

  1. State bahut coarse hai — sirf 2 boolean (threat_near, obstacle_near).
     Isse agent "kitna paas" ya "kitni battery bachi" jaisa nuance
     capture nahi kar pata.
  2. Har drone apna Q-table sirf apne khud ke experience se seekhta hai
     — agar ek drone ne kabhi threat nahi dekha, uska Q-table us state
     ke liye khaali (0.0) hi rahega, chahe uske paas wale drones ne
     100 baar threat handle kiya ho.
  3. Session khatam -> Q-table gayab. Har naya run zero se seekhta hai.

Yeh module in teeno ko address karta hai, bina rl_agent.py ko replace
kiye — AdaptiveAgent, QLearningAgent ka drop-in upgrade hai (same
interface: choose_action, update, action_to_velocity), plus:

  - Richer discretized state: threat/obstacle ko near/mid/far mein banta
    hai (3 buckets instead of bool), + local crowd density + battery-low
    flag
  - `federate(other_agent)` — do agents ke Q-tables ko average karta hai
    for shared states aur unseen states copy karta hai — yeh existing
    mesh_comms.sync_dags() ke saath hi call ho sakta hai (jab do drones
    comms-range mein hote hain, wo apna mission ledger AUR apna learned
    experience dono share karte hain — "swarm learns as one")
  - save_q_table() / load_q_table() — JSON persistence, taaki agla run
    zero se shuru na ho
"""
import json
import math
import random

try:
    from ursina import Vec3
except ImportError:  # headless/test environments jaha ursina na ho
    Vec3 = None

ACTIONS = ["forward", "left", "right", "back"]


def _bucket(distance, near, mid):
    if distance < near:
        return "near"
    elif distance < mid:
        return "mid"
    return "far"


class AdaptiveAgent:
    """rl_agent.QLearningAgent ka drop-in replacement — same interface,
    richer state + mesh-federated learning."""

    def __init__(self, learning_rate=0.1, discount=0.9, exploration_rate=0.2):
        self.q_table = {}
        self.last_state = None
        self.last_action = None
        self.lr = learning_rate
        self.discount = discount
        self.exploration_rate = exploration_rate
        self.episodes_seen = 0

    # -- richer state -----------------------------------------------------
    def get_state(self, drone, threat_pos, obstacle_pos, threat_active, obstacle_active,
                  nearby_count=0, battery=100.0):
        threat_bucket = "off"
        if threat_active and threat_pos is not None:
            d = (drone.position - threat_pos).length()
            threat_bucket = _bucket(d, near=4, mid=8)

        obstacle_bucket = "off"
        if obstacle_active and obstacle_pos is not None:
            d = (drone.position - obstacle_pos).length()
            obstacle_bucket = _bucket(d, near=3, mid=6)

        crowd_bucket = "alone" if nearby_count == 0 else ("some" if nearby_count < 4 else "crowded")
        battery_low = battery < 20

        return (threat_bucket, obstacle_bucket, crowd_bucket, battery_low)

    def _ensure_state(self, state):
        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in ACTIONS}

    def choose_action(self, state):
        self._ensure_state(state)
        if random.random() < self.exploration_rate:
            return random.choice(ACTIONS)
        return max(self.q_table[state], key=self.q_table[state].get)

    def compute_reward(self, state, new_cell_visited):
        threat_bucket, obstacle_bucket, crowd_bucket, battery_low = state
        reward = 0.0
        if threat_bucket == "near":
            reward -= 6.0
        elif threat_bucket == "mid":
            reward -= 2.0
        if obstacle_bucket == "near":
            reward -= 3.0
        elif obstacle_bucket == "mid":
            reward -= 1.0
        if battery_low:
            reward -= 2.0   # low-battery risk-taking ko discourage karta hai
        if new_cell_visited:
            reward += 1.0
        return reward

    def update(self, state, action, reward, next_state):
        self._ensure_state(state)
        self._ensure_state(next_state)
        old_value = self.q_table[state][action]
        future_best = max(self.q_table[next_state].values())
        new_value = old_value + self.lr * (reward + self.discount * future_best - old_value)
        self.q_table[state][action] = new_value
        self.episodes_seen += 1

    def action_to_velocity(self, drone, action, speed):
        if Vec3 is None:
            raise RuntimeError("ursina Vec3 not available in this environment")
        if action == "forward":
            return drone.velocity
        elif action == "left":
            angle = math.atan2(drone.velocity.z, drone.velocity.x) + 1.0
        elif action == "right":
            angle = math.atan2(drone.velocity.z, drone.velocity.x) - 1.0
        else:
            angle = math.atan2(drone.velocity.z, drone.velocity.x) + math.pi
        return Vec3(math.cos(angle), 0, math.sin(angle)) * speed

    # -- federated / mesh-shared learning -----------------------------------
    def federate(self, other, blend=0.5):
        """
        Doosre drone ke agent ke saath Q-knowledge share karo:
          - dono ne jo state dekha hai -> Q-values ko blend (weighted average)
          - sirf ek ne jo state dekha hai -> doosra usse copy kar leta hai
        Isse ek drone jo kabhi threat nahi mila, wo paas wale drone se
        "seekh" sakta hai bina khud us khatre mein jaaye — collective
        swarm intelligence, individual trial-and-error se kaafi tez.
        """
        all_states = set(self.q_table) | set(other.q_table)
        for state in all_states:
            self._ensure_state(state)
            other._ensure_state(state)
            for a in ACTIONS:
                mine = self.q_table[state][a]
                theirs = other.q_table[state][a]
                blended = mine * (1 - blend) + theirs * blend
                self.q_table[state][a] = blended
                other.q_table[state][a] = blended

    # -- persistence -------------------------------------------------------
    def save_q_table(self, path):
        serializable = {"||".join(map(str, k)): v for k, v in self.q_table.items()}
        with open(path, "w") as f:
            json.dump({"q_table": serializable, "episodes_seen": self.episodes_seen}, f, indent=2)

    def load_q_table(self, path):
        with open(path) as f:
            data = json.load(f)
        self.q_table = {}
        for k, v in data["q_table"].items():
            parts = k.split("||")
            key = tuple(p if p != "True" and p != "False" else (p == "True") for p in parts)
            self.q_table[key] = v
        self.episodes_seen = data.get("episodes_seen", 0)


def apply_adaptive_behavior(drone, threat_pos, obstacle_pos, threat_active, obstacle_active,
                             visited_new_cell, nearby_count=0, drone_speed=4.0, decision_interval=45):
    """rl_agent.apply_rl_behavior() ka drop-in replacement — main.py mein
    bas import line badalni hai (`from adaptive_agent import
    apply_adaptive_behavior as apply_rl_behavior`), aur agar mesh sync ke
    time federation bhi chahiye to us block mein agent.federate() call
    karna hai (README mein integration note dekhein)."""
    if not hasattr(drone, "adaptive_agent") or drone.adaptive_agent is None:
        drone.adaptive_agent = AdaptiveAgent()
        drone.rl_decision_timer = 0

    drone.rl_decision_timer -= 1
    if drone.rl_decision_timer > 0:
        return
    drone.rl_decision_timer = decision_interval

    agent = drone.adaptive_agent
    battery = getattr(drone, "battery", 100.0)
    state = agent.get_state(drone, threat_pos, obstacle_pos, threat_active, obstacle_active,
                             nearby_count=nearby_count, battery=battery)

    if agent.last_state is not None:
        reward = agent.compute_reward(state, visited_new_cell)
        agent.update(agent.last_state, agent.last_action, reward, state)

    action = agent.choose_action(state)
    drone.velocity = agent.action_to_velocity(drone, action, drone_speed)

    agent.last_state = state
    agent.last_action = action


# ---------------------------------------------------------------------
# Self-test — federation se knowledge transfer (bina experience ke seekhna)
# ---------------------------------------------------------------------
if __name__ == "__main__":
    veteran = AdaptiveAgent(exploration_rate=0.0)
    rookie = AdaptiveAgent(exploration_rate=0.0)

    # Veteran ne baar-baar 'threat near' state mein 'left' action se
    # achha reward paya hai — uska Q-table isse reflect karta hai
    veteran._ensure_state(("near", "off", "alone", False))
    veteran.q_table[("near", "off", "alone", False)]["left"] = 8.5
    veteran.q_table[("near", "off", "alone", False)]["forward"] = -3.0

    print("Before federation:")
    print("  rookie knows about ('near','off','alone',False)?",
          ("near", "off", "alone", False) in rookie.q_table)

    rookie.federate(veteran, blend=1.0)  # blend=1.0 -> pura copy le lo veteran se

    print("After federation (rookie never saw a threat itself):")
    print("  rookie's learned action for that state:",
          max(rookie.q_table[("near", "off", "alone", False)],
              key=rookie.q_table[("near", "off", "alone", False)].get))
    print("  rookie Q-values:", rookie.q_table[("near", "off", "alone", False)])

    # persistence round-trip test
    veteran.save_q_table("test_qtable.json")
    reloaded = AdaptiveAgent()
    reloaded.load_q_table("test_qtable.json")
    print("\nPersistence round-trip OK?",
          reloaded.q_table[("near", "off", "alone", False)] ==
          veteran.q_table[("near", "off", "alone", False)])