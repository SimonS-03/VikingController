import skfuzzy.control as ctrl
from typing import Dict
import numpy as np
from genome import Genome

# the movement commands to the controller
class MovementModule:
    """
    Movement module for the ship. Input a velocity vector that the ship is aiming for 
    and this module will output values to the acceleration and rotation module
    """
    def __init__(self, moveGenome: list[float] = None, genome: Genome = None):
        self.movement_fis = None
        self.movement_fis_sim = None

        # training
        self.moveGenome = moveGenome
        self.genome = genome if genome is not None else Genome()

        self.create_movement_fis()

    
    def create_movement_fis(self):
        # =========================== Defining in- and output ==================================

        # input 1 - desired speed (from the desired velocity vector)
        desired_speed = ctrl.Antecedent(np.linspace(0.0, 1.0, 11), "desired_speed")
        # input 2 - current speed
        current_speed = ctrl.Antecedent(np.linspace(0.0, 1.0, 11), "current_speed")
        # input 3 - difference between the desired heading (deg) and the current heading
        relative_angle = ctrl.Antecedent(np.linspace(-1.0, 1.0, 11), "relative_angle")

        # output 1 - desired turn rate
        
        # output 2 - desired thrust
        thrust = ctrl.Consequent(np.linspace(-1.0, 1.0, 11), "thrust")
        turn_rate = ctrl.Consequent(np.linspace(-1.0, 1.0, 11), "turn_rate")
        # =========================== Creating membership functions ================================

        desired_speed.automf(3, names=["low", "medium", "high"])
        current_speed.automf(3, names=["low", "medium", "high"])
        relative_angle.automf(3, names=["negative", "zero", "positive"])

        thrust.automf(3, names=["negative", "zero", "positive"])
        turn_rate.automf(3, names=["negative", "zero", "positive"])
        #thrust.automf(5, names=["very_negative", "negative", "zero", "positive", "very_positive"])

        self.genome.ApplyToTrap(desired_speed, ["low", "medium", "high"], "desired_speed")
        self.genome.ApplyToTrap(current_speed, ["low", "medium", "high"], "current_speed")
        self.genome.ApplyToTrap(relative_angle, ["negative", "zero", "positive"], "relative_angle")

        # =========================== Rules for movement FIS ========================================

        rule1 = ctrl.Rule(current_speed["low"] & desired_speed["low"], thrust["zero"])
        rule2 = ctrl.Rule(current_speed["medium"] & desired_speed["low"], thrust["negative"])
        rule3 = ctrl.Rule(current_speed["high"] & desired_speed["low"], thrust["negative"])
        rule4 = ctrl.Rule(current_speed["low"] & desired_speed["medium"], thrust["positive"])
        rule5 = ctrl.Rule(current_speed["medium"] & desired_speed["medium"], thrust["zero"])
        rule6 = ctrl.Rule(current_speed["high"] & desired_speed["medium"], thrust["negative"])
        rule7 = ctrl.Rule(current_speed["low"] & desired_speed["high"], thrust["positive"])
        rule8 = ctrl.Rule(current_speed["medium"] & desired_speed["high"], thrust["positive"])
        rule9 = ctrl.Rule(current_speed["high"] & desired_speed["high"], thrust["zero"])

        rule10 = ctrl.Rule(relative_angle["positive"], turn_rate["positive"])
        rule11 = ctrl.Rule(relative_angle["zero"], turn_rate["zero"])
        rule12 = ctrl.Rule(relative_angle["negative"], turn_rate["negative"])

        rule13 = ctrl.Rule(current_speed["high"] & relative_angle["positive"], thrust["negative"])
        rule14 = ctrl.Rule(current_speed["high"] & relative_angle["negative"], thrust["negative"])

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
        rules = [rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11, rule12]#, rule13, rule14]

        # =========================== Create a FIS controller and sim ===============================
        self.movement_fis = ctrl.ControlSystem(rules)
        self.movement_fis_sim = ctrl.ControlSystemSimulation(self.movement_fis)        
    

    def actions(self, ship_state: Dict, game_state: Dict, desired_heading_vector: Dict):
        # normalize desired speed using the maximum magnitude of the desired_heading_vector
        norm_desired_speed = desired_heading_vector["magnitude"] / desired_heading_vector["max_magnitude"]

        # normalize using the max speed of 240 m/s
        norm_current_speed = ship_state["speed"] / 240

        # normalized relative angle
        norm_relative_angle = (desired_heading_vector["heading"] - ship_state["heading"]) / 180

        self.movement_fis_sim.input["desired_speed"] = norm_desired_speed
        self.movement_fis_sim.input["current_speed"] = norm_current_speed
        self.movement_fis_sim.input["relative_angle"] = norm_relative_angle
        # compute fis output
        self.movement_fis_sim.compute()

        try:
            thrust = self.movement_fis_sim.output["thrust"]
        except KeyError:
            #print('Thrust, KeyError')
            thrust = 0
            
        try:
            turn_rate = self.movement_fis_sim.output["turn_rate"] 
        except KeyError:
            turn_rate = 0

        # convert the outputs to control actions
        thrust *= 240
        turn_rate *= 180
        fire = False
        drop_mine = False

        return thrust, turn_rate, fire, drop_mine
        
    
    @property
    def name(self) -> str:
        return "Movement module"