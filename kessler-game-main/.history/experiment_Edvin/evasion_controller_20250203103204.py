
import skfuzzy.control

from src.kesslergame import KesslerController
from typing import Dict, Tuple
import skfuzzy.control as ctrl
import skfuzzy as skf

import numpy as np
import random
from sympy import mod_inverse, gcd


class FuzzyController(KesslerController):
    def __init__(self, GA_values):
        self.aiming_fis = None
        self.aiming_fis_sim = None
        self.normalization_dist = None
        # GA parameter values
        self.GA_values = GA_values
        self.linspaces = {"distance":np.linspace(0.0, 1.0, 11),
                          "angle":np.linspace(-1.0, 1.0, 11),
                          "aiming_angle":np.linspace(-1.0, 1.0, 11),
                          }

        self.create_fuzzy_systems()

    def find_dangerlevel(self, ship_state: Dict, game_state: Dict, radius):
        # Find time to collision for all asteroids inside radius of r
        ast_idx, ast_dist = self.find_asteroids_inside_radius(ship_state, game_state, radius)
        time_to_collision_x = []
        time_to_collision_y = []
        for asteroid in game_state["asteroids"]:
            time_to_collision_x.append((ship_state["position"][0] - asteroid["position"][0]))
    def find_time_to_collision(self, x1, v1, x2, v2, map_size):
        delta_pos = (x2-x1) % map_size
        delta_vel = (v1-v2) % map_size

        if delta_vel == 0:
            return 0 if delta_pos == 0 else None
        
        g = gcd(delta_vel, map_size)
        
        # Solve for t using modular inverse
        delta_vel //= g
        delta_pos //= g
        mapsize //= g 
        t = (mod)

    
    def find_asteroids_inside_radius(self, ship_state: Dict, game_state: Dict, radius):
        # create list of closest asteroids
        asteroid_dist = []
        for asteroid in game_state["asteroids"]:
            asteroid_dist.append(np.sqrt((ship_state["position"][0] - asteroid["position"][0])**2 + (ship_state["position"][1] - asteroid["position"][1])**2))
        ast_dist = [x for x in asteroid_dist if x < radius]
        ast_idx = [asteroid_dist.index(x) for x in ast_dist] 
        return ast_idx, ast_dist

    def create_fuzzy_systems(self):
        self.find_dangerlevel()
    
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
        # get nearest asteroid
        nearest_ast_idx, nearest_ast_dist = self.find_nearest_asteroid(ship_state, game_state)

        nearest_ast = game_state["asteroids"][nearest_ast_idx]
        # get cartesian components of position
        dx = nearest_ast["position"][0] - ship_state["position"][0]
        dy = nearest_ast["position"][1] - ship_state["position"][1]

        # calculate angle from ship to asteroid
        angle_to_ast = np.arctan2(dy, dx)*180/np.pi
        # calculate the angle to asteroid relative to the ship's current heading (resolve angle to ship frame instead of global frame)
        relative_angle = ship_state["heading"] - angle_to_ast

        # clamp angle to be within +- 180 deg from front of ship (makes reasoning about right/left easier, just a preference)
        if relative_angle < -180.0:
            relative_angle = -180.0
        elif relative_angle > 180.0:
            relative_angle = 180.0

        # normalize relative angle to be in [-1, 1]
        norm_relative_angle = relative_angle/180.0

        # if it hasn't already been calculated, calculate normalization distance by using map size diagonal/2
        if not self.normalization_dist:
            self.normalization_dist = np.sqrt(game_state["map_size"][0]**2 + game_state["map_size"][1]**2)/2

        # normalize distance
        norm_ast_distance = nearest_ast_dist/self.normalization_dist

        # feed asteroid dist and angle to the FIS
        self.aiming_fis_sim.input["angle"] = norm_relative_angle
        self.aiming_fis_sim.input["distance"] = norm_ast_distance
        # compute fis output
        self.aiming_fis_sim.compute()
        # map normalized output to angle range [-180, 180], note that the output of the fis is determined by the membership functions and they go from -1 to 1
        desired_aim_angle = self.aiming_fis_sim.output["aiming_angle"]*180.0

        # this converts the desired aiming angle to a control action to be fed to the ship in terms of turn rate
        # set turn rate to 0
        turn_rate = 0
        # if desired aim angle is outside of +- 1 deg, turn in that direction with max turn rate, otherwise don't turn
        if desired_aim_angle < -0.5:
            turn_rate = ship_state["turn_rate_range"][1]*abs(desired_aim_angle)/180
        elif desired_aim_angle > 0.5:
            turn_rate = ship_state["turn_rate_range"][0]*abs(desired_aim_angle)/180

        # set firing to always be true (fires as often as possible), all other values to 0
        thrust = 0
        fire = True
        drop_mine = False
        #self.find_course(game_state)

        return thrust, turn_rate, fire, drop_mine