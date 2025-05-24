from src.kesslergame import KesslerController

from typing import Dict
import numpy as np

class DodgeModule():
    def __init__(self, ship_state: Dict, asteroid_state: Dict):
        self.dodge_direction = None
        self.thrust_direction = None
        self.find_maneuver(ship_state, asteroid_state)
    
    # get asteroid velocity angle [-180, 180]
    def get_asteroid_heading(self, asteroid_state: dict) -> float:
        ast_vel = asteroid_state["velocity"]
        theta = 180/np.pi * np.arctan2(ast_vel[1], ast_vel[0])
        theta = (theta + 360) % 360
        return theta
    
    """def create_dodge_fis(self):
        # input 1 - 
        time_to = ctrl.Antecedent(np.linspace(0.0, 1.0, 11), "relative_angle")

        # input 2 - time to collision
        time_to_collision = ctrl.Antecedent(np.linspace(0.0, 1.0, 11), "time_to_collision")

        # output - Threat level
        threat_level = ctrl.Consequent(np.linspace(0.0, 1.0, 11), "threat_level")

        # create membership functions for the inputs
        relative_angle.automf(3, names=["close", "near", "far"])
        time_to_collision.automf(2, names=["low", "high"])

        # create membershipfunctions for the outputs
        threat_level.automf(3, names=["low", "medium", "high"])

        threat_level["low"] = skf.trapmf(threat_level.universe, [0.0, 0.0, 0.0, 0.5])
        threat_level["medium"] = skf.trapmf(threat_level.universe, [0.25, 0.5, 0.5, 0.75])
        threat_level["high"] = skf.trapmf(threat_level.universe, [0.5, 1.0, 1.0, 1.0])

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
        self.threat_fis_sim = ctrl.ControlSystemSimulation(self.threat_fis)"""
    def find_maneuver(self, ship_state: Dict, asteroid_state: Dict):
        # the angle between the asteroid velocity and the ship velocity
        asteroid_theta = self.get_theta(ship_state, asteroid_state)

        # if the asteroid has collision course towards the rear end of 
        # the ship, thrust forwards, otherwise backward  
        ship_coord = ship_state["position"]
        asteroid_coord = asteroid_state["position"]
        asteroid_to_ship_vector = tuple(a - b for a, b in zip(ship_coord, asteroid_coord))
        asteroid_to_ship_vector_theta = 180/np.pi * np.arctan2(asteroid_to_ship_vector[1], asteroid_to_ship_vector[0])
        asteroid_to_ship_vector_theta = (asteroid_to_ship_vector_theta + 360) % 360

        # the angle between the asteroid velocity and the asteroid_to_ship_vector
        asteroid_heading = self.get_asteroid_heading(asteroid_state)
        
        velocity_diff = (ship_state["heading"] - asteroid_heading) % 360
        print(ship_state["heading"], asteroid_heading)

        if velocity_diff < 60 or velocity_diff > 300:
            self.thrust_direction = "forward"
        elif 120 < velocity_diff < 240:
            self.thrust_direction = "backwards"
        else:
            angle = (asteroid_to_ship_vector_theta - asteroid_heading) % 360
            # use angle to determine which side of the asteroid velocity vector to dodge to
            if angle > 0:
                if velocity_diff < 180:
                    self.thrust_direction = "forward" 
                elif velocity_diff > 180:
                    self.thrust_direction = "backwards"
            else:
                if velocity_diff < 180:
                    self.thrust_direction = "backwards"
                elif velocity_diff > 180:
                    self.thrust_direction = "forward" 
            
        # turning while dodging (asteroid_theta is [-180, 180])
        if 0 < asteroid_theta < 90 or -180 < asteroid_theta < -90:
            self.dodge_direction = "right" 
        else:
            self.dodge_direction = "left" 
        #self.thrust_direction = "forward" if abs(asteroid_theta) < 90 else "backwards"

    def get_theta(self, ship_state: Dict, asteroid_state: Dict) -> float:
        ast_vel = asteroid_state["velocity"]
        asteroid_heading = self.get_asteroid_heading(asteroid_state)
        asteroid_theta = asteroid_heading - ship_state["heading"]
        # in range [-180, 180]
        if asteroid_theta > 180:
            asteroid_theta -= 360
        elif asteroid_theta < -180:
            asteroid_theta += 360
        return asteroid_theta

    def actions(self, ship_state: Dict, asteroid_state: Dict):
        asteroid_theta = self.get_theta(ship_state, asteroid_state)
        #print(asteroid_theta)
        if 60 < abs(asteroid_theta) < 120:
            turn_rate = 0
        else:
            turn_rate = 90 if self.dodge_direction == "left" else -90

        thrust = 240 if self.thrust_direction == "forward" else -240
        # linear turn rate:
        # turn_rate = 180 * (asteroid_theta - asteroid_theta/abs(asteroid_theta) * 90) / 90
        # print("turning", turn_rate, asteroid_state["angle"], ship_state["heading"])

        fire = True
        drop_mine = False

        return thrust, turn_rate, fire, drop_mine

    
    @property
    def name(self) -> str:
        return "Dodge Module"

"""if time_to_collision is None or time_to_collision > 1:
            print("No thrusting")
            thrust = 0
            heading = PositionForce(ship_state, game_state, 50, radius = 10000)
            print(heading.state["heading"])
            delta_theta = heading.state["heading"] - ship_state["heading"]
            turn_rate = delta_theta * 2
        asteroid_coord = asteroid_state["position"]
        ship_coord = ship_state["position"]
        ship_to_asteroid_vector = tuple(a - b for a, b in zip(asteroid_coord, ship_coord))

        direction = np.dot(ship_to_asteroid_vector, ship_state["velocity"])

        thrust = c/time_to_collision
        thrust *= direction / np.abs(direction)"""