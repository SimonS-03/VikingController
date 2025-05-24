from heatmap import Heatmap

from typing import Dict

import numpy as np

# evasion FIS 
class evasionController:
    def __init__(self, heatmap_size: tuple[float, float]=(1000, 800), heatmap_resolution: float=8):
        self.heatmap_size = heatmap_size
        self.heatmap_resolution = heatmap_resolution

        # desired theta from heatmap 
        self.best_theta = None
        self.ship_ttc = None
        self.frames_travelled = 0
        self.map = Heatmap((0, heatmap_size[0]), (0, heatmap_size[1]), resolution = heatmap_resolution)

    def actions(self, ship_state, game_state):
        
        #self.map.actions(ship_state, game_state) 

        if self.best_theta is None or self.frames_travelled > 0:
            self.frames_travelled = 0
            self.ship_ttc = self.find_course(ship_state, game_state)
        
        self.frames_travelled += 1
        
        #print("Best_theta:", self.best_theta)

        ship_heading = ship_state["heading"]
        diff = self.best_theta - ship_heading
        # diff [-180, 180]
        if diff > 180:
            diff = -(360 - diff)
        elif diff < -180:
            diff = 360 + diff

        thrust = 0
        if self.ship_ttc > 8: # was 5
            #print(round(ship_state["speed"], 2))
            thrust = -round(ship_state["speed"]*2, 2)
        
        elif abs(diff) < 15 and self.ship_ttc < 5:
                # brake
            if ship_state["speed"] < 150:
                thrust = 360
            elif ship_state["speed"] > 150:
                thrust = -360
        
        elif abs(diff) > 165 and self.ship_ttc < 5:
            if ship_state["speed"] > -150:
                thrust = -360
            elif ship_state["speed"] < -150:
                thrust = 360
        else:
            if ship_state["speed"] > 0:
                thrust = -240
            elif ship_state["speed"] < 0:
                thrust = 240   
            #thrust = c / self.ship_ttc * 240 


        if abs(diff) < 90:
            turn_rate = np.clip(diff*30, -180, 180)
        else:
            backwards_diff = -1*np.sign(diff)*(180-abs(diff))
            #print(backwards_diff)
            turn_rate = np.clip(backwards_diff*30, -180, 180)
        #print(self.ship_ttc)
        fire = False
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

        best_dir = self.map.weighted_gradient(ship_state["radius"], 4, ship_state, game_state)

        theta = 180/np.pi * np.arctan2(best_dir[1], best_dir[0])
        # convert to [0, 360]
        theta = (theta + 360) % 360
        self.best_theta = theta

        # ship danger
        ship_ttc = self.map.ship_ttc
        return ship_ttc
        
    @property
    def name(self) -> str:
        return "Evasion module"
        
    
    