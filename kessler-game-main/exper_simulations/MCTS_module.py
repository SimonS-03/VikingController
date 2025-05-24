from MCTS_simulation.simulator import Simulator

from typing import Dict
import numpy as np

# The action queue is stored, updated and executed in the real game here
class MCTSModule:
    def __init__(self):
        self.actions_queue = None
        # if the time to collision of the ship is higher than the threshold the simulation stops
        self.ttc_threshold = 10
        # duration of each action
        self.action_duration = 10

    def actions(self, ship_state: Dict, game_state: Dict): 
        ttc = self.get_ttc(game_state, ship_state)
        if ttc is None or ttc > self.ttc_threshold:
            self.actions_queue = None
            thrust = self.brake(ship_state)
            print("Braking")
            return thrust, 0, False, False

        if self.actions_queue is None or self.actions_queue["duration"] == 0: 
            # Run simulator and return the best action
            sim = Simulator()
            self.actions_queue = sim.run_simulations(ship_state, game_state, ttc_threshold=self.ttc_threshold)

        thrust = self.actions_queue.get("thrust", 0)
        turn_rate = self.actions_queue.get("turn_rate", 0)
        fire = self.actions_queue.get("fire", False)
        drop_mine = self.actions_queue.get("mine", False)

        self.actions_queue["duration"] -= 1

        return thrust, turn_rate, fire, drop_mine

    # get the time to collision for the current position 
    def get_ttc(self, game_state: Dict, ship_state: Dict, margin: float = 0) -> float:
        """
        Called by the game to check the time to collision of the ship in the current spot
        """
        lowest_ttc = None
        for asteroid in game_state["asteroids"]:
            asteroid_pos = np.array(asteroid["position"])
            asteroid_vel = np.array(asteroid["velocity"])

            ship_pos = np.array(ship_state["position"])
            ship_vel = np.array(ship_state["velocity"])
            asteroid_speed = np.linalg.norm(asteroid_vel)

            rel_pos = ship_pos - asteroid_pos
            distance = np.linalg.norm(rel_pos)
            
            # skip if the asteroid is stationary
            if asteroid_speed == 0:
                continue

            dot = np.dot(asteroid_vel, rel_pos)

            # skip if they are moving away from eachother
            if dot <= 0:
                continue

            # Calculate what theta would result in a collision
            safe_distance = asteroid["radius"] + ship_state["radius"] + margin

            # if they have already collided
            if np.linalg.norm(rel_pos) < safe_distance:
                return 0.0

            theta = np.arccos(dot / (distance * asteroid_speed))
            min_theta = np.arctan(safe_distance / distance)

            if theta < min_theta:
                time_to_collision = distance / asteroid_speed
                if lowest_ttc is None or time_to_collision < lowest_ttc:
                    lowest_ttc = time_to_collision
        return lowest_ttc
    
    def brake(self, ship_state: Dict):
        safe_speed = 5
        if ship_state["speed"] > safe_speed:
            thrust = -240
        elif ship_state["speed"] < -safe_speed:
            thrust = 240
        else:
            thrust = 0
        return thrust

    @property
    def name(self) -> str:
        return "Get actions using Monte Carlo Tree Search"