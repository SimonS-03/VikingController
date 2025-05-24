from heatmap import Heatmap

from typing import Dict, Tuple
import skfuzzy.control as ctrl
import skfuzzy as skf
import sys

import numpy as np

# evasion FIS 
class Evasion2Module:
    def __init__(self, heatmap_size: tuple[float, float]=(500, 400), heatmap_resolution: float=10):
        self.heatmap_size = heatmap_size
        self.heatmap_resolution = heatmap_resolution

        # desired theta from heatmap 
        self.best_theta = None
        self.ship_ttc = None
        self.frames_travelled = 0
    
    def create_evasion_fis(self):
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

        rules = [rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11, rule12, rule13, rule14, rule1a, rule2a, rule3a]

        # =========================== Create a FIS controller and sim ===============================
        self.movement_fis = ctrl.ControlSystem(rules)
        self.movement_fis_sim = ctrl.ControlSystemSimulation(self.movement_fis)        

    def actions(self, ship_state, game_state):
        
        if self.best_theta is None or self.frames_travelled > 30:
            self.frames_travelled = 0
            self.ship_ttc = self.find_course(ship_state, game_state)
        
        self.frames_travelled += 1
        
        print("Best_theta:", self.best_theta)
        ship_heading = ship_state["heading"]
        diff = self.best_theta - ship_heading
        # diff [-180, 180]
        if diff > 180:
            diff = -(360 - diff)
        elif diff < -180:
            diff = 360 + diff
        
    
        c = 10    
        if abs(diff) > 60:
                # brake
            if ship_state["speed"] > 3:
                thrust = -240
            elif ship_state["speed"] < 3:
                thrust = 240      
        else:
            if ship_state["speed"] < 40:
                thrust = 240
            else:
                thrust = 0
            #thrust = c / self.ship_ttc * 240 
        # turn rate
        turn_rate = diff 

        fire = True
        drop_mine = False
        return thrust, turn_rate, fire, drop_mine
    
    def brake(self, ship_state: Dict):
        if ship_state["speed"] > 0:
            thrust = -240
        else:
            thrust = 240
        return thrust

    def find_course(self, ship_state: Dict, game_state: Dict):
        # initialize heatmap
        ship_coord = ship_state["position"]
        width, height = self.heatmap_size
        boundries = []
        x_boundary = (max(ship_coord[0]-width/2, 0), min(ship_coord[0]+width/2, 1000))
        y_boundary = (max(ship_coord[1]-height/2, 0), min(ship_coord[1]+height/2, 800))
        map = Heatmap(x_boundary, y_boundary, self.heatmap_resolution)
        map.actions(ship_state, game_state)
        best_dir = map.gradient_descent()
        theta = 180/np.pi * np.arctan2(best_dir[1], best_dir[0])
        # convert to [0, 360]
        theta = (theta + 360) % 360
        self.best_theta = theta

        # ship danger
        ship_ttc = map.ship_ttc
        return ship_ttc
        
    @property
    def name(self) -> str:
        return "Evasion module"
        
    
    