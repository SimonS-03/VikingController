
import skfuzzy.control

from src.kesslergame import KesslerController
from typing import Dict, Tuple
import skfuzzy.control as ctrl
import skfuzzy as skf

import numpy as np
import random
import sys


class FuzzyController(KesslerController):
    #def __init__(self):

        # Checks all asteroids inside a radius. Returns the time between the ship and each asteroid passing 
        # their respective collision point, and the time until the first object passes that same point. 
    def find_threatlevels(self, ship_state: Dict, game_state: Dict, radius) -> list[tuple[float, float]]:
        ast_idx = self.find_asteroids_inside_radius(ship_state, game_state, radius)
        time_to_collision = []
        for asteroid in game_state["asteroids"]:
            time_to_collision.append(self.time_to_collision(ship_state, asteroid, game_state["map_size"]))
        #print(time_to_collision)
        #sys.exit()
        return time_to_collision
    
        # Takes ship and asteroid state and returns the time between the object crossing the collision point and the time to collision
    def time_to_collision(self, ship_state: Dict, asteroid: Dict, map_size: tuple[float, float]) -> float:
        print(map_size)
        t1 = self.one_direction_collision(ship_state["position"][0], asteroid["position"][0], ship_state["velocity"][0], asteroid["velocity"][0], map_size[0])
        t2 = self.one_direction_collision(ship_state["position"][1], asteroid["position"][1], ship_state["velocity"][1], asteroid["velocity"][1], map_size[1])
        try:
            delta_t = abs(t2-t1)
        except TypeError:
            return None, None
        return delta_t, min(t1, t2)
    
        # Time to collision in one coordinate where map_len is the mapsize in the direction of interest
    def one_direction_collision(self, x1, x2, v1, v2, map_len) -> float:
        if v1 == v2:
            return None
        
        if x1 > x2:
            x1, x2 = x2, x1
            v1, v2 = v2, v1

        if v1 >= 0 and v2 <= 0:
            dist = x2-x1
            return dist/(v1-v2)
        elif v1 <= 0 and v2 >= 0:
            dist = x1 + (map_len-x2)
            return dist/(v2-v1)
        elif (v1 < 0 and v2 < 0) and abs(v1) < abs(v2):
            return (x2-x1)/(v1-v2)
        elif (v1 < 0 and v2 < 0) and abs(v1) > abs(v2):
            x1 += map_len
            return (x2-x1)/(v1-v2)
        elif (v1 > 0 and v2 > 0) and abs(v2) < abs(v1):
            return (x2-x1)/(v1-v2)
        elif (v1 > 0 and v2 > 0) and abs(v2) > abs(v1):
            x2 -= map_len
            return (x2-x1)/(v1-v2)

        # Finds index of all asteroids inside radius r
    def find_asteroids_inside_radius(self, ship_state: Dict, game_state: Dict, radius) -> list[int]:
        asteroid_idx = []
        for idx, asteroid in enumerate(game_state["asteroids"]):
            distance = np.sqrt((ship_state["position"][0] - asteroid["position"][0])**2 + (ship_state["position"][1] - asteroid["position"][1])**2)
            if distance < radius:
                asteroid_idx.append(idx)
        return asteroid_idx
        
    
    def actions(self, ship_state: Dict, game_state: Dict) -> Tuple[float, float, bool, bool]:
        """
        Method processed each time step by this controller to determine what control actions to take

        Arguments:
            ship_state (dict): contains state information for your own ship
            game_state (dict): contains state information for all objects in the game

        Returns:
            float: thrust control value
            float: turn-rate control value
            bool: fire control value. Shoots if true
            bool: mine deployment control value. Lays mine if true
        """
        self.find_threatlevels(ship_state, game_state, 500)
       
        # set firing to always be true (fires as often as possible), all other values to 0
        thrust = 0
        turn_rate = 0
        fire = True
        drop_mine = False
        #self.find_course(game_state)

        return thrust, turn_rate, fire, drop_mine
    
    @property
    def name(self) -> str:
        return "evasion_controller"