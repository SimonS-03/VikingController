from typing import Dict, List
import sys

# The action queue for each SIMULATION run is stored and run here.
class SimulationController():
    def __init__(self, actions_queue: List[Dict]):
        self.actions_queue = actions_queue

    def actions(self, ship_state: Dict, game_state: Dict):   
        # pop the first element from the actions queue and apply
        if self.actions_queue.size == 0:
            safe_speed = 5 
            if abs(ship_state["speed"]) > safe_speed:
                thrust = self.brake(ship_state, safe_speed)
                return thrust, 0, False, False
            else:
                return 0, 0, False, False
        
        if len(self.actions_queue) == 3:
            first_element = self.actions_queue[0]
            # edit duration (in frames)
            if first_element["duration"] > 0:
                first_element["duration"] -= 1
            elif first_element["duration"] <= 0:
                self.actions_queue = self.actions_queue[1:]
            safe_speed = 5 
            if abs(ship_state["speed"]) > safe_speed:
                thrust = self.brake(ship_state, safe_speed)
                return thrust, 0, False, False
            else:
                return 0, 0, False, False

        first_element = self.actions_queue[0]
        thrust = first_element['thrust'] 
        turn_rate = first_element['turn_rate']
        
        # edit duration (in frames)
        if first_element["duration"] > 0:
            first_element["duration"] -= 1
        elif first_element["duration"] <= 0:
            self.actions_queue = self.actions_queue[1:]
        else:
            print("error in the queue")
            sys.exit()

        return thrust, turn_rate, False, False

    def brake(self, ship_state: Dict, safe_speed: float):
        current_speed = ship_state["speed"]
        if current_speed > 0:
            speed_error = current_speed - safe_speed
        else:
            speed_error = current_speed + safe_speed
        Kp = 10 

        # proportional control
        thrust = -Kp * speed_error
        thrust = max(min(thrust, 240), -240)
        return thrust

    @property
    def name(self) -> str:
        return "Simulation Controller"