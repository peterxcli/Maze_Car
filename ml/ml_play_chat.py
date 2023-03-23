import numpy as np
import random
from collections import deque

class QLearningAgent:
    def __init__(self, num_states, num_actions, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.num_states = num_states
        self.num_actions = num_actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table = np.zeros((num_states, num_actions))

    def choose_action(self, state):
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(range(self.num_actions))
        else:
            return np.argmax(self.q_table[state])

    def learn(self, state, action, reward, next_state):
        predict = self.q_table[state, action]
        target = reward + self.gamma * np.max(self.q_table[next_state])
        self.q_table[state, action] += self.alpha * (target - predict)


class MLPlay:
    def __init__(self, ai_name, *args, **kwargs):
        self.player_no = ai_name
        self.coordinate = deque(maxlen=50)
        self.control_list = {"left_PWM": 0, "right_PWM": 0}

        # Initialize Q-learning agent
        self.agent = QLearningAgent(num_states=243, num_actions=9)  # You can adjust the state and action space according to your needs.

        print(kwargs)

    def discretize_state(self, scene_info):
        # Discretize the state space based on the sensor values
        r = self.discretize_sensor_value(scene_info["R_sensor"])
        l = self.discretize_sensor_value(scene_info["L_sensor"])
        f = self.discretize_sensor_value(scene_info["F_sensor"])
        lt = self.discretize_sensor_value(scene_info["L_T_sensor"])
        rt = self.discretize_sensor_value(scene_info["R_T_sensor"])

        return r + l * 3 + f * 3**2 + lt * 3**3 + rt * 3**4

    def discretize_sensor_value(self, value):
        if value <= 10:
            return 0
        elif value <= 30:
            return 1
        else:
            return 2

    def update(self, scene_info: dict, *args, **kwargs):
        """
        Generate the command according to the received scene information
        """
        if scene_info["status"] != "GAME_ALIVE":
            return "RESET"

        current_state = self.discretize_state(scene_info)
        current_action = self.agent.choose_action(current_state)

        # Update PWM values based on the chosen action
        self.control_list["left_PWM"] = (current_action % 3 - 1) * 255
        self.control_list["right_PWM"] = (current_action // 3 - 1) * 255

        if "x" in scene_info and "y" in scene_info:
            self.coordinate.append((scene_info["x"], scene_info["y"]))

        if len(self.coordinate) >= 2:
            last_state = self.discretize_state(scene_info)
            reward = self.compute_reward(scene_info)

            self.agent.learn(last_state, current_action, reward, current_state)

        return self.control_list

    def compute_reward(self, scene_info):
        return -((scene_info["x"] - scene_info["end_x"]) ** 2 + (scene_info["y"] - scene_info["end_y"]) ** 2)
        # Define a reward function based on the scene information