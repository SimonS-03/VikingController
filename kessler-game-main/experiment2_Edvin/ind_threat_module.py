from src.kesslergame import KesslerController
from dodge_module import DodgeModule

from typing import Dict
import skfuzzy.control as ctrl
import skfuzzy as skf
import numpy as np

# threat assessment fis for a single asteroid
class IndividualThreatModule:
    def __init__(self):
        self.threat_fis = None
        self.threat_fis_sim = None

        self.current_dodge = None

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
        """
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
        self.threat_fis_sim = ctrl.ControlSystemSimulation(self.threat_fis)"""

    def actions(self, ship_state, game_state):
        closest_asteroid, time_to_collision = self.find_time_to_collision(ship_state, game_state, 0)
        #TODO speed where it can shoot accurately
        safe_speed = 20
        # check if it is necessary to dodge. 
        if time_to_collision is None or time_to_collision > 0.3:
            self.current_dodge = None
            # check if braking is necessary
            if abs(ship_state["speed"]) > safe_speed:
                thrust = self.brake(ship_state)
                turn_rate = 0
                fire = True
                drop_mine = False
            else:
                thrust = 0
                turn_rate = 0
                fire = True
                drop_mine = False
        else:
            # dodge
            if self.current_dodge is None:
                self.current_dodge = DodgeModule(ship_state, closest_asteroid) 
            thrust, turn_rate, fire, drop_mine =  self.current_dodge.actions(ship_state, closest_asteroid)

        return thrust, turn_rate, fire, drop_mine 
    
    def brake(self, ship_state: Dict):
        if ship_state["speed"] > 0:
            thrust = -240
        else:
            thrust = 240
        return thrust

        safe_time = 2
        if time_to_collision is None or time_to_collision > safe_time:
            #TODO apply breaking and activate the scoring module
            thrust = 0
            turn_rate = 0
            fire = True
            drop_mine = False
            return thrust, turn_rate, fire, drop_mine
        else:
            print("Dodge active")
            dodge = DodgeModule()
            return dodge.actions(ship_state, game_state, closest_asteroid, time_to_collision)

    def find_time_to_collision(self, ship_state: Dict, game_state: Dict, margin: float):
        closest_asteroid = None
        shortest_time = None
        ship_coord = ship_state["position"]
        time_list = []
        for asteroid in game_state["asteroids"]:
            
            asteroid_coord = asteroid["position"]
            asteroid_vel = asteroid["velocity"]
            asteroid_to_ship_vector = tuple(a - b for a, b in zip(ship_coord, asteroid_coord))

            dot = np.dot(asteroid_vel, asteroid_to_ship_vector)
            # if asteroid is moving away from the ship
            if dot < 0:
                continue
            # angle between asteroid velocity and asteroid_to_ship_vector
            vec1_mag = np.linalg.norm(asteroid_vel)
            vec2_mag = np.linalg.norm(asteroid_to_ship_vector)
            theta = np.arccos(dot / (vec1_mag * vec2_mag))
            

            # distance between the asteroid and the ship
            dx = ship_coord[0] - asteroid_coord[0]
            dy = ship_coord[1] - asteroid_coord[1]
            distance = np.sqrt(dx**2 + dy**2)

            # minimum theta for collision not to happen
            safe_distance = asteroid["radius"] + ship_state["radius"] + margin
            safe_distance = distance if safe_distance > distance else safe_distance
            min_theta = np.arcsin(safe_distance / distance)
            #print(theta, min_theta)
            """# ship angle from the asteroid
            ship_theta = (180/np.pi)*np.arctan2(ship_coord[1]-asteroid_coord[1], 
                                                ship_coord[0]-asteroid_coord[0])
            if ship_theta < 0:
                ship_theta += 360"""
            if theta < min_theta:
                asteroid_speed = np.sqrt(asteroid["velocity"][0]**2 + asteroid["velocity"][1]**2)
                time_to_collision = (distance - asteroid["radius"] - ship_state["radius"]) / asteroid_speed
                #time_list.append(time_to_collision)
                if shortest_time is None or time_to_collision < shortest_time:
                    shortest_time = time_to_collision
                    closest_asteroid = asteroid
        print(shortest_time)
        #print(time_list)
            
        return closest_asteroid, shortest_time

    @property
    def name(self) -> str:
        return "Individual threat module"
