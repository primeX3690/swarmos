import random
import math
from ursina import Vec3
from config import RL_LEARNING_RATE, RL_DISCOUNT, RL_EXPLORATION_RATE, DRONE_SPEED

ACTIONS = ['forward', 'left', 'right', 'back']


class QLearningAgent:
    """
    Simple tabular Q-learning agent — har drone ka apna Q-table hota hai.
    State = (threat_near, obstacle_near) simplified discretized state.
    Isse har drone apne experience se seekhta hai ki kis situation mein
    kaunsa action zyada reward deta hai (fixed rules ki jagah).
    """
    def __init__(self):
        self.q_table = {}
        self.last_state = None
        self.last_action = None

    def get_state(self, drone, threat_pos, obstacle_pos, threat_active, obstacle_active):
        threat_near = False
        obstacle_near = False

        if threat_active and threat_pos is not None:
            threat_near = (drone.position - threat_pos).length() < 8

        if obstacle_active and obstacle_pos is not None:
            obstacle_near = (drone.position - obstacle_pos).length() < 6

        return (threat_near, obstacle_near)

    def choose_action(self, state):
        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in ACTIONS}

        if random.random() < RL_EXPLORATION_RATE:
            return random.choice(ACTIONS)

        return max(self.q_table[state], key=self.q_table[state].get)

    def compute_reward(self, state, new_cell_visited):
        threat_near, obstacle_near = state
        reward = 0.0
        if threat_near:
            reward -= 5.0
        if obstacle_near:
            reward -= 2.0
        if new_cell_visited:
            reward += 1.0
        return reward

    def update(self, state, action, reward, next_state):
        if next_state not in self.q_table:
            self.q_table[next_state] = {a: 0.0 for a in ACTIONS}

        old_value = self.q_table[state][action]
        future_best = max(self.q_table[next_state].values())

        new_value = old_value + RL_LEARNING_RATE * (
            reward + RL_DISCOUNT * future_best - old_value
        )
        self.q_table[state][action] = new_value

    def action_to_velocity(self, drone, action):
        if action == 'forward':
            return drone.velocity
        elif action == 'left':
            angle = math.atan2(drone.velocity.z, drone.velocity.x) + 1.0
        elif action == 'right':
            angle = math.atan2(drone.velocity.z, drone.velocity.x) - 1.0
        else:  # back
            angle = math.atan2(drone.velocity.z, drone.velocity.x) + math.pi

        return Vec3(math.cos(angle), 0, math.sin(angle)) * DRONE_SPEED


# def apply_rl_behavior(drone, threat_pos, obstacle_pos, threat_active, obstacle_active, visited_new_cell):
#     """Mode B ka naya RL-driven version — Q-learning se seekhta hai."""
#     if not hasattr(drone, 'rl_agent'):
#         drone.rl_agent = QLearningAgent()

#     agent = drone.rl_agent
#     state = agent.get_state(drone, threat_pos, obstacle_pos, threat_active, obstacle_active)

#     if agent.last_state is not None:
#         reward = agent.compute_reward(state, visited_new_cell)
#         agent.update(agent.last_state, agent.last_action, reward, state)

#     action = agent.choose_action(state)
#     drone.velocity = agent.action_to_velocity(drone, action)

#     agent.last_state = state
#     agent.last_action = action






def apply_rl_behavior(drone, threat_pos, obstacle_pos, threat_active, obstacle_active, visited_new_cell):
    """Mode B ka RL-driven version — Q-learning se seekhta hai, lekin
    decision har frame nahi, balki interval pe leta hai taaki movement
    smooth rahe (jitter na ho)."""
    if not hasattr(drone, 'rl_agent'):
        drone.rl_agent = QLearningAgent()
        drone.rl_decision_timer = 0

    drone.rl_decision_timer -= 1
    if drone.rl_decision_timer > 0:
        return  # abhi purana action/velocity hi continue rahega

    drone.rl_decision_timer = 45  # ~0.75 second (60fps assume) baad naya decision

    agent = drone.rl_agent
    state = agent.get_state(drone, threat_pos, obstacle_pos, threat_active, obstacle_active)

    if agent.last_state is not None:
        reward = agent.compute_reward(state, visited_new_cell)
        agent.update(agent.last_state, agent.last_action, reward, state)

    action = agent.choose_action(state)
    drone.velocity = agent.action_to_velocity(drone, action)

    agent.last_state = state
    agent.last_action = action