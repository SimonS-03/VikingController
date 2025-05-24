# -*- coding: utf-8 -*-
# Copyright © 2022 Thales. All Rights Reserved.
# NOTICE: This file is subject to the license agreement defined in file 'LICENSE', which is part of
# this source code package.
import skfuzzy.control
import sys
sys.path.append('/Users/simon_stoll/Documents/programmering/KEX/Swedish-Vikings/kessler-game-main')

import src
from src.kesslergame import KesslerController, asteroid
from typing import Dict, Tuple
import skfuzzy.control as ctrl
import skfuzzy as skf
import numpy as np
from genome import Genome

class FuzzyController(KesslerController):
    def __init__(self, aimGenome: list[float], genome: Genome = None):
        self.aiming_fis = None
        self.aiming_fis_sim = None
        self.normalization_dist = None
        self.aimGenome = aimGenome
        self.genome = genome
        self.create_fuzzy_systems()

    def create_aiming_fis(self):
        # input 1 - distance to asteroid
        distance = ctrl.Antecedent(np.linspace(0.0, 1.0, 11), "distance")
        # input 2 - angle to asteroid (relative to ship heading)
        angle = ctrl.Antecedent(np.linspace(-1.0, 1.0, 11), "angle")
        # input 3 - angle velocity of asteroid
        angle_velocity = ctrl.Antecedent(np.linspace(-1.0, 1.0, 11), "angle_velocity")

        # output - desired relative angle to match to aim ship at asteroid
        aiming_angle = ctrl.Consequent(np.linspace(-1.0, 1.0, 11), "aiming_angle")

        # creating 3 equally spaced membership functions for the inputs
        distance.automf(3, names=["close", "medium", "far"])

        # Scale
        distance["close"].mf = distance["close"].mf * 0.1
        distance["medium"].mf = distance["medium"].mf * 0.1
        distance["far"].mf = distance["far"].mf * 0.1

        angle.automf(3, names=["negative", "zero", "positive"])
        angle_velocity.automf(3, names=["negative fast", "negative slow", "zero", "positive slow", "positive fast"])

        distNames = ["close", "medium", "far"]
        angleNames = ["negative", "zero", "positive"]
        angleVelNames = ["negative fast", "negative slow", "zero", "positive slow", "positive fast"]

        # creating 3 triangular membership functions for the output, APPLYING GENOME

        aiming_angle["negative"] = skf.trapmf(aiming_angle.universe, [-1.0, self.aimGenome[0], self.aimGenome[1], 0.0])
        aiming_angle["zero"] = skf.trapmf(aiming_angle.universe, [-1.0, self.aimGenome[2], self.aimGenome[3], 1.0])
        aiming_angle["positive"] = skf.trapmf(aiming_angle.universe, [0.0, self.aimGenome[4], self.aimGenome[5], 1.0])

        edges = [(-1.0, 0.0), (-1.0, 1.0), (0.0, 1.0)]
        for idx in range(len(angleNames)):
            angle[angleNames[idx]] = skf.trapmf(angle.universe, [edges[idx][0], self.angleGenome[idx*2], self.angleGenome[idx*2+1], edges[idx][1]])

        # creating the rule base for the fuzzy system
        rule1 = ctrl.Rule(distance["close"] & angle["negative"], aiming_angle["negative"])
        rule2 = ctrl.Rule(distance["medium"] & angle["negative"], aiming_angle["negative"])
        rule3 = ctrl.Rule(distance["far"] & angle["negative"], aiming_angle["negative"])
        rule4 = ctrl.Rule(distance["close"] & angle["zero"], aiming_angle["zero"])
        rule5 = ctrl.Rule(distance["medium"] & angle["zero"], aiming_angle["zero"])
        rule6 = ctrl.Rule(distance["far"] & angle["zero"], aiming_angle["zero"])
        rule7 = ctrl.Rule(distance["close"] & angle["positive"], aiming_angle["positive"])
        rule8 = ctrl.Rule(distance["medium"] & angle["positive"], aiming_angle["positive"])
        rule9 = ctrl.Rule(distance["far"] & angle["positive"], aiming_angle["positive"])
        
        rule10 = ctrl.Rule(angle_velocity["negative fast"] & distance["far"] & angle["zero"], aiming_angle["negative"])
        rule11 = ctrl.Rule(angle_velocity["positive fast"] & distance["far"] & angle["zero"], aiming_angle["positive"])
        rule12 = ctrl.Rule(angle_velocity["negative fast"] & distance["medium"] & angle["zero"], aiming_angle["negative"])
        rule13 = ctrl.Rule(angle_velocity["positive fast"] & distance["medium"] & angle["zero"], aiming_angle["positive"])
        
        rule14 = ctrl.Rule(angle_velocity["negative slow"] & distance["far"] & angle["zero"], aiming_angle["negative"])
        rule15 = ctrl.Rule(angle_velocity["positive slow"] & distance["far"] & angle["zero"], aiming_angle["positive"])

        rules = [rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11, rule12, rule13, rule14, rule15]

        distNames = ["close", "medium", "far"]
        angleNames = ["negative", "zero", "positive"]
        angleVelNames = ["negative fast", "negative slow", "zero", "positive slow", "positive fast"]

        for distName in distNames:
            rules.append(ctrl.Rule(distance[distName] & angle["zero"] & angle_velocity["zero"], aiming_angle["zero"]))

            

        # creating a FIS controller from the rules + membership functions
        self.aiming_fis = ctrl.ControlSystem(rules)
        # creating a controller sim to evaluate the FIS
        self.aiming_fis_sim = ctrl.ControlSystemSimulation(self.aiming_fis)

    def create_fuzzy_systems(self):
        self.create_aiming_fis()

    def find_nearest_asteroid(self, ship_state: Dict, game_state: Dict):
        # create list of distances from the ship to each asteroid
        asteroid_dist = [np.sqrt((ship_state["position"][0] - asteroid["position"][0])**2 + (ship_state["position"][1] - asteroid["position"][1])**2) for asteroid in game_state["asteroids"]]
        # get minimum distance
        ast_dist = min(asteroid_dist)
        # get index in list of nearest asteroid
        ast_idx = asteroid_dist.index(ast_dist)

        return ast_idx, ast_dist

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

        # calculate angle velocity of asteroid relative to ship
        relative_velocity = np.sqrt(nearest_ast["velocity"][0]**2 + nearest_ast["velocity"][1]**2)*np.sin(nearest_ast["angle"]-angle_to_ast)
        angle_velocity = relative_velocity/nearest_ast_dist
        self.aiming_fis_sim.input["angle_velocity"] = angle_velocity

        # clamp angle to be within +- 180 deg from front of ship (makes reasoning about right/left easier, just a preference)
        if relative_angle < -180.0:
            #relative_angle = -180.0
            relative_angle += 360
        
        elif relative_angle > 180.0:
            relative_angle -= 360
            #elative_angle = 180.0

        # normalize relative angle to be in [-1, 1]
        norm_relative_angle = relative_angle/180.0

        ##### Changed
        # if it hasn't already been calculated, calculate normalization distance by using map size diagonal/2
        if not self.normalization_dist:
            self.normalization_dist = np.sqrt(game_state["map_size"][0]**2 + game_state["map_size"][1]**2)/2

        # normalize distance where (the max) 1 means it is an entire screen distance away
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
        threshold = 0.5
        if desired_aim_angle < -1*threshold:
            turn_rate = ship_state["turn_rate_range"][1]*1 #abs(desired_aim_angle)
        elif desired_aim_angle > threshold:
            turn_rate = ship_state["turn_rate_range"][0]*1

        # set firing to always be true (fires as often as possible), all other values to 0
        thrust = 0
        fire = True
        drop_mine = False
        self.find_course(game_state)

        return thrust, turn_rate, fire, drop_mine

    def find_course(self, game_state: Dict):
        asteroid_state = game_state['asteroids']
        #print(asteroid_state[0]['position'][0])
        #best_pos = self.find_position(game_state)
        return

    def find_position(self, game_state: Dict):
        best_pos = []
        asteroid_states = game_state['asteroids']
        map_size = game_state['map_size']
        sigma = 1

        for x in range(map_size[0]):
            for y in range(map_size[1]):
                weight = 0

                #asteroid_states=[{'position': (200, 400), 'angle': 0, 'speed': 0, 'size': 4}]
                for asteroid in asteroid_states:
                    # Gaussian weighting each asteroid distance to ship
                    weight += np.exp(-((x-asteroid['position'][0])**2 + (y-asteroid['position'][1])**2) / (2*sigma**2))
                
                if best_pos == [] or weight < best_pos[1]:
                    best_pos = [(x, y), weight]
        print(best_pos)
        
    @property
    def name(self) -> str:
        """
        Simple property used for naming controllers such that it can be displayed in the graphics engine
 
        Returns:
            str: name of this controller
        """
        return "Fuzzy Test1"

    # @property
    # def custom_sprite_path(self) -> str:
    #     return "Neo.png"
