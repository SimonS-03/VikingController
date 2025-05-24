from src.kesslergame import KesslerController

from typing import Dict, List
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
       
        # input 1 - relative angle to the asteroid. Accounting for asteroid and ship velocity
        relative_angle = ctrl.Antecedent(np.linspace(0.0, 1.0, 11), "relative_angle")

        # input 2 - time to collision
        time_to_collision = ctrl.Antecedent(np.linspace(0.0, 1.0, 11), "time_to_collision")

        # output - Threat level
        threat_level = ctrl.Consequent(np.linspace(0.0, 1.0, 11), "threat_level")

        # create membership functions for the inputs
        relative_angle.automf(3, names=["close", "near", "far"])
        time_to_collision.automf(2, names=["low", "high"])

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

        return

    # calculate approximate threat score for all asteroids in a radius
    def find_threat_score(self, ship_state: Dict, game_state: Dict, radius: float, weights: List[float]):
        ship_coord = ship_state["position"]

        distance = []
        speed = []
        relative_angle = []
        for asteroid in game_state["asteroids"]:
            asteroid_coord = asteroid["position"]

            # distance between the asteroid and the ship
            dx = ship_coord[0] - asteroid_coord[0]
            dy = ship_coord[1] - asteroid_coord[1]
            current_distance = np.sqrt(dx**2 + dy**2)

            # calculate the relative velocity by subtracting the ship's 
            # velocity vector from the asteroid's veloicty vector
            
            ship_velocity = np.array([ship_state["velocity"][0], ship_state["velocity"][1]])
            asteroid_velocity = np.array([asteroid["velocity"][0], asteroid["velocity"][1]])

            relative_velocity = asteroid_velocity - ship_velocity
            magnitude = np.linalg.norm(relative_velocity)
            angle = np.degrees(np.arctan2(relative_velocity[1], relative_velocity[0]))
            
            distance.append(current_distance)
            speed.append(magnitude)
            relative_angle.append(angle)
        threat = (weights[0] * np.exp(-distance)) + (weights[1] * np.log(speed+1)) + \
                (weights[2] * np.abs(np.cos(relative_angle)))
        
        return threat
    
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
