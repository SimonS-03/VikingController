import forces.py

from typing import Dict, Tuple
import skfuzzy.control as ctrl
import skfuzzy as skf

import numpy as np

# evasion FIS 
# inputs are the position and velocities of the asteroids and outputs an optimal heading direction and speed.
#TODO use it as input in a 'movement' module
class EvasionFIS:
    def __init__(self):
        self.evasion_fis = None
        self.evasion_fis_sim = None

        self.create_evasion_fis()

    def create_evasion_fis(self, ship_state: Dict, game_state: Dict) -> float:
        # =========================== Defining in- and output ==================================
        # input 1 - forcevector at the ship's position, from the vectorfield created by the asteroids POSITION
        force_from_positions = ctrl.Antecedent()

        # input 2 - forcevector from the asteroids VELOCITY

        # output 

        # ===========================  ==================================

       
        # input 1 - Number of asteroids at distance r or closer to the ship
        asteroid_density = ctrl.Antecedent(np.linspace(0.0, 1.0, 11), "density")

        # input 2 - Average distance to the asteroids at distance r or closer
        distance_to_asteroids = ctrl.Antecedent(np.linspace(0.0, 1.0, 11), "average_distance")

        # output - Threat level
        threat_level = ctrl.Consequent(np.linspace(0.0, 1.0, 11), "threat_level")

        # create membership functions for the inputs
        asteroid_density.automf(3, names=["low", "medium", "high"])

        distance_to_asteroids.automf(3, names=["close", "medium", "far"])

        # create membershipfunctions for the outputs
        threat_level["low"] = skf.trapmf(threat_level.universe, [0.0, 0.0, 0.0, 0.5])
        threat_level["medium"] = skf.trapmf(threat_level.universe, [0.25, 0.5, 0.5, 0.75])
        threat_level["high"] = skf.trapmf(threat_level.universe, [0.5, 1.0, 1.0, 1.0])

        # create rulebase
        rule1 = ctrl.rule(asteroid_density["low"] & distance_to_asteroids["far"], threat_level["low"])
        rule2 = ctrl.rule(asteroid_density["medium"] & distance_to_asteroids["far"], threat_level["low"])
        rule3 = ctrl.rule(asteroid_density["high"] & distance_to_asteroids["far"], threat_level["medium"])
        rule4 = ctrl.rule(asteroid_density["low"] & distance_to_asteroids["medium"], threat_level["low"])
        rule5 = ctrl.rule(asteroid_density["medium"] & distance_to_asteroids["medium"], threat_level["medium"])
        rule6 = ctrl.rule(asteroid_density["high"] & distance_to_asteroids["medium"], threat_level["high"])
        rule7 = ctrl.rule(asteroid_density["low"] & distance_to_asteroids["close"], threat_level["medium"])
        rule8 = ctrl.rule(asteroid_density["medium"] & distance_to_asteroids["close"], threat_level["high"])
        rule9 = ctrl.rule(asteroid_density["high"] & distance_to_asteroids["close"], threat_level["high"])

        rules = [rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9]

        # creating a FIS controller
        self.threat_fis = ctrl.ControlSystem(rules)
        # creating a controller sim to evaluate the FIS
        self.threat_fis_sim = ctrl.ControlSystemSimulation(self.threat_fis)

    def action(self, ship_state, game_state):
        heading = self.get_vector_from_position_field(ship_state, game_state, 500)
        if 

        return

        
    
    