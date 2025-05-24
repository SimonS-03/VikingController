from src.kesslergame import KesslerController
from movement_module import MovementModule
from forces import PositionForce

from typing import Dict
import skfuzzy.control as ctrl
import skfuzzy as skf
import numpy as np

# threat assessment fis
class ThreatModule:
    def __init__(self):
        self.threat_fis = None
        self.threat_fis_sim = None

        #self.create_threat_fis()

    def create_threat_fis(self, ship_state: Dict, game_state: Dict) -> float:
       
        # input 1 - distance to the asteroid
        distance = ctrl.Antecedent(np.linspace(0.0, 1.0, 11), "distance")

        # input 2 - speed of the asteroid
        speed = ctrl.Antecedent(np.linspace(0.0, 1.0, 11), "speed")

        # input 3 -  angle of the asteroid's velocity vector towards the ship
        theta = ctrl.Antecedent(np.linspace(0.0, 1.0, 11), "theta")

        # output - Threat level
        threat_level = ctrl.Consequent(np.linspace(0.0, 1.0, 11), "threat_level")

        # create membership functions for the inputs
        distance.automf(3, names=["close", "near", "far"])
        speed.automf(2, names=["low", "high"])
        theta.automf(2, names=["small", "big"])

        # create membershipfunctions for the outputs
        threat_level.automf(3, names=["low", "medium", "high"])

        """threat_level["low"] = skf.trapmf(threat_level.universe, [0.0, 0.0, 0.0, 0.5])
        threat_level["medium"] = skf.trapmf(threat_level.universe, [0.25, 0.5, 0.5, 0.75])
        threat_level["high"] = skf.trapmf(threat_level.universe, [0.5, 1.0, 1.0, 1.0])"""

        # create rulebase
        rule1 = ctrl.rule(distance["low"] & speed["low"] & theta["small"], threat_level["high"])
        rule2 = ctrl.rule(distance["low"] & speed["low"] & theta["big"], threat_level["medium"])
        rule3 = ctrl.rule(distance["low"] & speed["high"] & theta["small"], threat_level["high"])
        rule4 = ctrl.rule(distance["low"] & speed["high"] & theta["big"], threat_level["high"])
        rule5 = ctrl.rule(distance["near"] & speed["low"] & theta["small"], threat_level["medium"])
        rule6 = ctrl.rule(distance["near"] & speed["low"] & theta["big"], threat_level["low"])
        rule7 = ctrl.rule(distance["near"] & speed["high"] & theta["small"], threat_level["high"])
        rule8 = ctrl.rule(distance["near"] & speed["high"] & theta["big"], threat_level["medium"])
        rule9 = ctrl.rule(distance["far"] & speed["low"] & theta["small"], threat_level["low"])
        rule10 = ctrl.rule(distance["far"] & speed["low"] & theta["big"], threat_level["low"])
        rule11 = ctrl.rule(distance["far"] & speed["high"] & theta["small"], threat_level["medium"])
        rule12 = ctrl.rule(distance["far"] & speed["high"] & theta["big"], threat_level["low"])
    
        rules = [rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11, rule12]

        # creating a FIS controller
        self.threat_fis = ctrl.ControlSystem(rules)
        # creating a controller sim to evaluate the FIS
        self.threat_fis_sim = ctrl.ControlSystemSimulation(self.threat_fis)

    def actions(self, ship_state, game_state):
        time_to_collision = self.find_time_to_collision(ship_state, game_state, 20)
        safe_time = 2
        if time_to_collision is None or time_to_collision > safe_time:
            #TODO apply breaking and activate the scoring module
            thrust = 0
            turn_rate = 0
            fire = True
            drop_mine = False
            return thrust, turn_rate, fire, drop_mine
        else:
            print("Movement active")
            move = MovementModule()
            heading = PositionForce(ship_state, game_state, 50, radius = 100)
            return move.actions(ship_state, game_state, heading.state)

    def find_time_to_collision(self, ship_state: Dict, game_state: Dict, danger_degree: float):
        shortest_time = None
        ship_coord = ship_state["position"]
        for asteroid in game_state["asteroids"]:
            asteroid_coord = asteroid["position"]
            # ship angle from the asteroid
            ship_theta = (180/np.pi)*np.arctan2(ship_coord[1]-asteroid_coord[1], 
                                                ship_coord[0]-asteroid_coord[0])
            if ship_theta < 0:
                ship_theta += 360
            if abs(ship_theta - asteroid["angle"]) < danger_degree:
                # distance between the asteroid and the ship
                dx = ship_coord[0] - asteroid_coord[0]
                dy = ship_coord[1] - asteroid_coord[1]
                distance = np.sqrt(dx**2 + dy**2)
                
                asteroid_speed = np.sqrt(asteroid["velocity"][0]**2 + asteroid["velocity"][1]**2)
                time_to_collision = distance / asteroid_speed
                if shortest_time is None or time_to_collision < shortest_time:
                    shortest_time = time_to_collision
        return shortest_time

    @property
    def name(self) -> str:
        return "Threat module"

    def find_closest_asteorid(self, ship_state: Dict, game_state: Dict):
        min_distance = 10000
        for asteroid in game_state["asteroids"]:
            dx = ship_state["position"][0] - asteroid["position"][0]
            dy = ship_state["position"][1] - asteroid["position"][1]
            distance = np.sqrt(dx**2 + dy**2)
            if distance < min_distance:
                min_distance = distance
                closest_asteroid = asteroid
        return closest_asteroid

        # Finds index of all asteroids inside radius r
    def find_asteroids_inside_radius(self, ship_state: Dict, game_state: Dict, radius) -> list[int]:
        asteroid_idx = []
        for idx, asteroid in enumerate(game_state["asteroids"]):
            distance = np.sqrt((ship_state["position"][0] - asteroid["position"][0])**2 + (ship_state["position"][1] - asteroid["position"][1])**2)
            if distance < radius:
                asteroid_idx.append(idx)
        return asteroid_idx
