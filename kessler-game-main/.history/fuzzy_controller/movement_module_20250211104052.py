import skfuzzy.control as ctrl
import numpy as np

# input a desired velocity vector and this module will output the movement commands to the controller
class MovementModule:
    #def __init__(self):
    
    def create_movement_fis(self):
        # =========================== Defining in- and output ==================================

        # input 1 - desired speed (from the desired velocity vector)
        desired_speed = ctrl.Antecedent(np.linspace(0.0, 1.0, 11), "desired_speed")
        # input 2 - current speed
        current_speed = ctrl.Antecedent(np.linspace(0.0, 1.0, 11), "current_speed")
        # input 3 - difference between the desired heading (deg) and the current heading
        relative_angle = ctrl.Antecedent(np.linspace(-1.0, 1.0, 11), "relative_angle")

        # output 1 - desired turn rate
        turn_rate = ctrl.Consequent(np.linspace(-1.0, 1.0, 11), "turn_rate")
        # output 2 - desired thrust
        thrust = ctrl.Consequent(np.linspace(-1.0, 1.0, 11), "thrust")

        # =========================== Creating membership functions ================================

        desired_speed.automf(3, names=["low", "medium", "high"])
        current_speed.automf(3, names=["low", "medium", "high"])
        relative_angle.automf(3, names=["negative", "zero", "positive"])

        turn_rate.automf(3, names=["negative", "zero", "positive"])
        thrust.automf(3, names=["negative", "zero", "positive"])
        #thrust.automf(5, names=["very_negative", "negative", "zero", "positive", "very_positive"])

        # =========================== Rules for movement FIS ========================================
        # straight movement
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
                          turn_rate["zero"] & thrust["very_positive"])
        
        rule6 = ctrl.Rule(current_speed["medium"] & desired_speed["low"] & relative_angle["zero"], 
                          turn_rate["negative"] & thrust["very_positive"])
        
        rule7 = ctrl.Rule(current_speed["high"] & desired_speed["low"] & relative_angle["zero"], 
                          turn_rate["zero"] & thrust["very_negative"])
        
        rule8 = ctrl.Rule(current_speed["low"] & desired_speed["negative"] & relative_angle["zero"], 
                          turn_rate["negative"] & thrust["positive"])
        rule1 = ctrl.Rule(current_speed["low"] & desired_speed["negative"] & relative_angle["zero"], 
                          turn_rate["negative"] & thrust["positive"])
        rule1 = ctrl.Rule(current_speed["low"] & desired_speed["negative"] & relative_angle["zero"], 
                          turn_rate["negative"] & thrust["positive"])
        rule1 = ctrl.Rule(current_speed["low"] & desired_speed["negative"] & relative_angle["zero"], 
                          turn_rate["negative"] & thrust["positive"])
    
    def actions(self):

        
    
    @property
    def name(self) -> str:
        return "Movement module"