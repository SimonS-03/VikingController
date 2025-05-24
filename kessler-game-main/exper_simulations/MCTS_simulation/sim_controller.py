from typing import Dict, List

# The action queue for each SIMULATION run is stored and run here.
class SimulationController():
    def __init__(self, actions_queue: List[Dict]):
        self.actions_queue = actions_queue

    def actions(self, ship_state: Dict, game_state: Dict):   
        # pop the first element from the actions queue and apply
        if not self.actions_queue:
            return 0, 0, False, False
        first_element = self.actions_queue[0]

        thrust = first_element.get("thrust", 0)
        turn_rate = first_element.get("turn_rate", 0)
        fire = first_element.get("fire", False)
        drop_mine = first_element.get("mine", False)
        
        # edit duration (in frames)
        if first_element["duration"] > 0:
            first_element["duration"] -= 1 
        else:
            self.actions_queue.pop(0)

        return thrust, turn_rate, fire, drop_mine

    @property
    def name(self) -> str:
        return "Simulation Controller"