import skfuzzy.control as ctrl
from typing import Dict
import numpy as np


# the movement commands to the controller
class MovementModule: 
    """
    Movement module for the ship. Input a velocity vector that the ship is aiming for 
    and this module will output values to the acceleration and rotation module
    """
    def __init__(self):
        self.movement_fis = None
        self.movement_fis_sim = None

        self.create_movement_fis()

    
    def create_movement_fis(self):
        # =========================== Defining in- and output ==================================

        # input 1 - desired speed (from the desired velocity vector)
        desired_speed = ctrl.Antecedent(np.linspace(0.0, 1.0, 11), "desired_speed")
        # input 2 - current speed
        current_speed = ctrl.Antecedent(np.linspace(0.0, 1.0, 11), "current_speed")
        # input 3 - difference between the desired heading (deg) and the current heading
        relative_angle = ctrl.Antecedent(np.linspace(-1.0, 1.0, 11), "relative_angle")
        # input 4 - number of asteroids nearby
        number_of_asteroids = ctrl.Antecedent(np.linspace(0.0, 1.0, 11), "number_of_asteroids")

        # output 1 - desired turn rate
        
        # output 2 - desired thrust
        thrust = ctrl.Consequent(np.linspace(-1.0, 1.0, 11), "thrust")
        turn_rate = ctrl.Consequent(np.linspace(-1.0, 1.0, 11), "turn_rate")
        # =========================== Creating membership functions ================================

        desired_speed.automf(3, names=["low", "medium", "high"])
        current_speed.automf(3, names=["low", "medium", "high"])
        relative_angle.automf(5, names=["very_negative", "negative", "zero", "positive", "very_positive"]) 
        number_of_asteroids.automf(2, names=["few", "many"])
        #relative_angle.automf(3, names=["negative", "zero", "positive"]) 

        #thrust.automf(3, names=["negative", "zero", "positive"])
        thrust.automf(5, names=["very_negative", "negative", "zero", "positive", "very_positive"])
        turn_rate.automf(5, names=["very_negative", "negative", "zero", "positive", "very_positive"])
        #thrust.automf(5, names=["very_negative", "negative", "zero", "positive", "very_positive"])

        """self.genome.ApplyToTrap(desired_speed, ["low", "medium", "high"], "desired_speed")
        self.genome.ApplyToTrap(current_speed, ["low", "medium", "high"], "current_speed")
        self.genome.ApplyToTrap(relative_angle, ["negative", "zero", "positive"], "relative_angle")"""

        # =========================== Rules for movement FIS ========================================

        rule1 = ctrl.Rule(current_speed["low"] & desired_speed["low"] & number_of_asteroids["few"], thrust["zero"])
        rule1a = ctrl.Rule(current_speed["low"] & desired_speed["low"] & number_of_asteroids["many"], thrust["very_positive"])
        rule2 = ctrl.Rule(current_speed["medium"] & desired_speed["low"] & number_of_asteroids["few"], thrust["negative"])
        rule2a = ctrl.Rule(current_speed["medium"] & desired_speed["low"] & number_of_asteroids["many"], thrust["positive"])
        rule3 = ctrl.Rule(current_speed["high"] & desired_speed["low"] & number_of_asteroids["few"], thrust["very_negative"])
        rule3a = ctrl.Rule(current_speed["high"] & desired_speed["low"] & number_of_asteroids["many"], thrust["zero"])
        rule4 = ctrl.Rule(current_speed["low"] & desired_speed["medium"], thrust["positive"])
        rule5 = ctrl.Rule(current_speed["medium"] & desired_speed["medium"], thrust["zero"])
        rule6 = ctrl.Rule(current_speed["high"] & desired_speed["medium"], thrust["negative"])
        rule7 = ctrl.Rule(current_speed["low"] & desired_speed["high"], thrust["very_positive"])
        rule8 = ctrl.Rule(current_speed["medium"] & desired_speed["high"], thrust["positive"])
        rule9 = ctrl.Rule(current_speed["high"] & desired_speed["high"], thrust["zero"])

        rule10 = ctrl.Rule(relative_angle["very_positive"], turn_rate["very_positive"])
        rule11 = ctrl.Rule(relative_angle["positive"], turn_rate["positive"])
        rule12 = ctrl.Rule(relative_angle["zero"], turn_rate["zero"])
        rule13 = ctrl.Rule(relative_angle["negative"], turn_rate["negative"])
        rule14 = ctrl.Rule(relative_angle["very_negative"], turn_rate["very_negative"])

        rule = ctrl.Rule(relative_angle["positive"] | relative_angle["negative"], thrust["negative"])


        """# with rotation
        rule1 = ctrl.Rule(current_speed["low"] & desired_speed["low"] & relative_angle["zero"],
                          turn_rate["zero"] & thrust["zero"])
        
        rule2 = ctrl.Rule(current_speed["medium"] & desired_speed["medium"] & relative_angle["zero"], 
                          turn_rate["zero"] & thrust["zero"])
        
        rule3 = ctrl.Rule(current_speed["high"] & desired_speed["high"] & relative_angle["zero"], 
                          turn_rate["zero"] & thrust["zero"])
        
        # with acceleration
        rule4 = ctrl.Rule(current_speed["low"] & desired_speed["medium"] & relative_angle["zero"], 
                          turn_rate["zero"] & thrust["positive"])
        
        rule5 = ctrl.Rule(current_speed["low"] & desired_speed["high"] & relative_angle["zero"], 
                          turn_rate["zero"] & thrust["positive"])
        
        #rule5 = ctrl.Rule(current_speed["low"] & desired_speed["high"] & relative_angle["zero"], 
        #                  turn_rate["zero"] & thrust["very_positive"])
        
        rule6 = ctrl.Rule(current_speed["medium"] & desired_speed["low"] & relative_angle["zero"], 
                          turn_rate["negative"] & thrust["negative"])
        
        rule7 = ctrl.Rule(current_speed["high"] & desired_speed["low"] & relative_angle["zero"], 
                          turn_rate["zero"] & thrust["negative"])
        
        # with rotation
        rule8 = ctrl.Rule(current_speed["low"] & desired_speed["low"] & relative_angle["positive"], 
                          turn_rate["positive"] & thrust["zero"])
        
        rule9 = ctrl.Rule(current_speed["low"] & desired_speed["low"] & relative_angle["negative"], 
                          turn_rate["negative"] & thrust["zero"])
        
        rule10 = ctrl.Rule(current_speed["medium"] & desired_speed["medium"] & relative_angle["positive"], 
                          turn_rate["positive"] & thrust["negative"])
        
        rule11 = ctrl.Rule(current_speed["medium"] & desired_speed["medium"] & relative_angle["negative"], 
                          turn_rate["negative"] & thrust["negative"])
        
        rule12 = ctrl.Rule(current_speed["high"] & desired_speed["high"] & relative_angle["positive"], 
                          turn_rate["positive"] & thrust["negative"])
        
        rule13 = ctrl.Rule(current_speed["high"] & desired_speed["high"] & relative_angle["negative"], 
                          turn_rate["negative"] & thrust["negative"])
        
        # rotation and acceleration
        #rule14 = ctrl.Rule(current_speed["low"] & desired_speed["negative"] & relative_angle["zero"], 
        #                 turn_rate["negative"] & thrust["positive"])"""
        rules = [rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11, rule12, rule13, rule14, rule1a, rule2a, rule3a]

        # =========================== Create a FIS controller and sim ===============================
        self.movement_fis = ctrl.ControlSystem(rules)
        self.movement_fis_sim = ctrl.ControlSystemSimulation(self.movement_fis)        
    

    def actions(self, ship_state: Dict, game_state: Dict, desired_heading_vector: Dict):
        # normalize desired speed using the maximum magnitude of the desired_heading_vector

        norm_desired_speed = desired_heading_vector["magnitude"] / desired_heading_vector["max_magnitude"]

        # normalize using the max speed of 240 m/s
        norm_current_speed = ship_state["speed"] / 240

        # normalized relative 
        relative_angle = desired_heading_vector["heading"] - ship_state["heading"]
        if abs(relative_angle) > 180:
            relative_angle = -relative_angle/abs(relative_angle) * (360-abs(relative_angle))
        norm_relative_angle = relative_angle / 180
        print(desired_heading_vector["heading"], relative_angle)

        nbr_asteroids = self.nbr_asteroids_nearby(ship_state, game_state, 100)
        if nbr_asteroids > 1:
            norm_nbr_asteroids = 1
        else:
            norm_nbr_asteroids = 0

        self.movement_fis_sim.input["desired_speed"] = norm_desired_speed
        self.movement_fis_sim.input["current_speed"] = norm_current_speed
        self.movement_fis_sim.input["relative_angle"] = norm_relative_angle
        self.movement_fis_sim.input["number_of_asteroids"] = norm_nbr_asteroids
        # compute fis output
        self.movement_fis_sim.compute()

        try:
            thrust = self.movement_fis_sim.output["thrust"]
        except KeyError:
            print('KeyError')
            thrust = 0
            
        try:
            turn_rate = self.movement_fis_sim.output["turn_rate"] 
        except KeyError:
            turn_rate = 0

        # convert the outputs to control actions
        thrust *= 240
        turn_rate *= 180
        #print(thrust, turn_rate)
        fire = False
        drop_mine = False

        return thrust, turn_rate, fire, drop_mine
    
    def nbr_asteroids_nearby(self, ship_state: Dict, game_state: Dict, radius) -> list[int]:
        nbr = 0
        for idx, asteroid in enumerate(game_state["asteroids"]):
            distance = np.sqrt((ship_state["position"][0] - asteroid["position"][0])**2 + (ship_state["position"][1] - asteroid["position"][1])**2)
            if distance < radius:
                nbr += 1
        return nbr
    
    @property
    def name(self) -> str:
        return "Movement module"