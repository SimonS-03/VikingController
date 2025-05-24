
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