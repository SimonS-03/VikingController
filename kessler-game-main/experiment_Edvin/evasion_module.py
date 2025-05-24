from heatmap import Heatmap

from typing import Dict, Tuple
import skfuzzy.control as ctrl
import skfuzzy as skf
import sys

import numpy as np

# evasion FIS 
class EvasionModule:
    def __init__(self, heatmap_size: tuple[float, float]=(1000, 800), heatmap_resolution: float=10):
        self.heatmap_size = heatmap_size
        self.heatmap_resolution = heatmap_resolution

        # desired theta from heatmap 
        self.best_theta = None
        self.ship_ttc = None
        self.frames_travelled = 0

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
        x_boundary = (max(ship_coord[0]-width/2, 0), min(ship_coord[0]+width/2, 1000))
        y_boundary = (max(ship_coord[1]-height/2, 0), min(ship_coord[1]+height/2, 800))
        map = Heatmap(x_boundary, y_boundary, self.heatmap_resolution)
        map.actions(ship_state, game_state)
        best_dir = map.weighted_gradient(ship_state["radius"], 3)
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
        
    
    