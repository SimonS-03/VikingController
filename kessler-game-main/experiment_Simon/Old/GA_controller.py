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
from experiment_Simon.Old.genomeOld import Genome

class FuzzyController(KesslerController):
    def __init__(self, genome: Genome = None):
        self.aiming_fis = None
        self.aiming_fis_sim = None
        self.normalization_dist = None
        self.genome = genome if genome is not None else Genome()
        self.frame = 0
        self.create_fuzzy_systems()

    def create_aiming_fis(self):
        
        # =========================== Defining in- and output ==================================

        # input 1 - distance to asteroid
        distance = ctrl.Antecedent(np.linspace(0.0, 1.0, 11), "distance")
        # input 2 - angle to asteroid (relative to ship heading)
        angle = ctrl.Antecedent(np.linspace(-1.0, 1.0, 11), "angle")
        # input 3 - angle velocity of asteroid
        angle_velocity = ctrl.Antecedent(np.linspace(-1.0, 1.0, 11), "angle_velocity")

        # output - desired relative angle to match to aim ship at asteroid
        aiming_angle = ctrl.Consequent(np.linspace(-1.0, 1.0, 11), "aiming_angle")

        # =========================== Creating membership functions ================================




        distNames = ["close", "medium", "far"]
        angle3Names = ["negative", "zero", "positive"]
        angle5Names = ["negative high", "negative low", "zero", "positive low", "positive high"]

        aiming_angle.automf(3, names = angle3Names)
        distance.automf(3, names=distNames)
        angle.automf(3, names = angle3Names)
        angle_velocity.automf(5, names = angle5Names)

        # Genome class can automatically apply itself to a trapezoid membership function.
        self.genome.ApplyToTrap(aiming_angle, angle3Names, "desired_angle")
        self.genome.ApplyToTrap(distance, distNames, "distance")
        self.genome.ApplyToTrap(angle, angle3Names, "angle")
        self.genome.ApplyToTrap(angle_velocity, angle5Names, "angle_velocity")

        # ============================ Rules for aiming_FIS ===================================
        basicRules = []

        # Basic aiming rules, ex: if ast to the left aim left
        basicRules.append(ctrl.Rule(distance["close"] & angle["negative"], aiming_angle["negative"] % 1))
        basicRules.append(ctrl.Rule(distance["medium"] & angle["negative"], aiming_angle["negative"] % 1))
        basicRules.append(ctrl.Rule(distance["far"] & angle["negative"], aiming_angle["negative"] % 1))
        
        basicRules.append(ctrl.Rule(distance["close"] & angle["positive"], aiming_angle["positive"] % 1))
        basicRules.append(ctrl.Rule(distance["medium"] & angle["positive"], aiming_angle["positive"] % 1))
        basicRules.append(ctrl.Rule(distance["far"] & angle["positive"], aiming_angle["positive"] % 1))
        
        basicRules.append(ctrl.Rule(angle_velocity["zero"] & angle["zero"], aiming_angle["zero"] % 0.1))
        
        basicRules.append(ctrl.Rule(angle_velocity["zero"] & distance["close"] & angle["zero"], aiming_angle["zero"] % 1))
        basicRules.append(ctrl.Rule(angle_velocity["zero"] & distance["medium"] & angle["zero"], aiming_angle["zero"] % 1))
        basicRules.append(ctrl.Rule(angle_velocity["zero"] & distance["far"] & angle["zero"], aiming_angle["zero"] % 1))
        
        
        basicRules.append(ctrl.Rule(angle_velocity["zero"] & distance["close"] & angle["positive"], aiming_angle["positive"] % 1))
        basicRules.append(ctrl.Rule(angle_velocity["zero"] & distance["medium"] & angle["positive"], aiming_angle["positive"] % 1))
        basicRules.append(ctrl.Rule(angle_velocity["zero"] & distance["far"] & angle["positive"], aiming_angle["positive"] % 1))

        basicRules.append(ctrl.Rule(angle_velocity["zero"] & distance["close"] & angle["negative"], aiming_angle["negative"] % 1))
        basicRules.append(ctrl.Rule(angle_velocity["zero"] & distance["medium"] & angle["negative"], aiming_angle["negative"] % 1))
        basicRules.append(ctrl.Rule(angle_velocity["zero"] & distance["far"] & angle["negative"], aiming_angle["negative"] % 1))
        
        # ex: if asteroid lined up, dont change direction
        #rules.append(ctrl.Rule(distance["close"] & angle["zero"], aiming_angle["zero"]))
        #rules.append(ctrl.Rule(distance["medium"] & angle["zero"], aiming_angle["zero"]))
        #rules.append(ctrl.Rule(distance["far"] & angle["zero"], aiming_angle["zero"]))


        leadingRules = basicRules.copy()
        
        # ========= Get it to aim further on ============
        leadBasicFactor = 1.3

        leadingRules.append(ctrl.Rule(angle_velocity["negative high"] & (distance["far"]) & (angle["negative"]), aiming_angle["negative"] % (leadBasicFactor)))
        leadingRules.append(ctrl.Rule(angle_velocity["positive high"] & (distance["far"]) & (angle["positive"]), aiming_angle["positive"] % (leadBasicFactor)))
        
        leadingRules.append(ctrl.Rule(angle_velocity["negative high"] & (distance["medium"]) & (angle["negative"]), aiming_angle["negative"] % (leadBasicFactor*1)))
        leadingRules.append(ctrl.Rule(angle_velocity["positive high"] & (distance["medium"]) & (angle["positive"]), aiming_angle["positive"] % (leadBasicFactor*1)))
        
        leadingRules.append(ctrl.Rule(angle_velocity["negative high"] & (distance["close"]) & (angle["negative"]), aiming_angle["negative"] % (leadBasicFactor*1)))
        leadingRules.append(ctrl.Rule(angle_velocity["positive high"] & (distance["close"]) & (angle["positive"]), aiming_angle["positive"] % (leadBasicFactor*1)))

        leadWeakFactor = 1.2
        leadingRules.append(ctrl.Rule(angle_velocity["negative low"] & (distance["far"]) & (angle["negative"]), aiming_angle["negative"] % (leadWeakFactor)))
        leadingRules.append(ctrl.Rule(angle_velocity["positive low"] & (distance["far"]) & (angle["positive"]), aiming_angle["positive"] % (leadWeakFactor)))
        
        leadingRules.append(ctrl.Rule(angle_velocity["negative low"] & (distance["medium"]) & (angle["negative"]), aiming_angle["negative"] % (leadWeakFactor*1)))
        leadingRules.append(ctrl.Rule(angle_velocity["positive low"] & (distance["medium"]) & (angle["positive"]), aiming_angle["positive"] % (leadWeakFactor*1)))
        
        leadingRules.append(ctrl.Rule(angle_velocity["negative low"] & (distance["close"]) & (angle["negative"]), aiming_angle["negative"] % (leadWeakFactor*0.8)))
        leadingRules.append(ctrl.Rule(angle_velocity["positive low"] & (distance["close"]) & (angle["positive"]), aiming_angle["positive"] % (leadWeakFactor*0.8)))
        

        # ======= Get it to eventually stop aiming further on =================
        # Was 1
        weakeningFactor = 0.5
        leadingRules.append(ctrl.Rule(angle_velocity["negative high"] & (distance["far"] | distance["medium"] | distance["close"]) & (angle["positive"] | angle["zero"]), aiming_angle["positive"] % weakeningFactor))
        leadingRules.append(ctrl.Rule(angle_velocity["positive high"] & (distance["far"] | distance["medium"] | distance["close"]) & (angle["negative"] | angle["zero"]), aiming_angle["negative"] % weakeningFactor))

        leadingRules.append(ctrl.Rule(angle_velocity["negative low"] & (distance["far"] | distance["medium"] | distance["close"]) & (angle["positive"] | angle["zero"]), aiming_angle["positive"] % weakeningFactor))
        leadingRules.append(ctrl.Rule(angle_velocity["positive low"] & (distance["far"] | distance["medium"] | distance["close"]) & (angle["negative"] | angle["zero"]), aiming_angle["negative"] % weakeningFactor))


        # Leading rules
        leadingOGRules = basicRules.copy()
        # Was 2
        leadBasicFactor = 1.3
        # Get it to continue aiming further on
        leadingOGRules.append(ctrl.Rule(angle_velocity["negative high"] & (distance["far"] | distance["medium"] | distance["close"]) & (angle["negative"]), aiming_angle["negative"] % leadBasicFactor))
        leadingOGRules.append(ctrl.Rule(angle_velocity["positive high"] & (distance["far"] | distance["medium"] | distance["close"]) & (angle["positive"]), aiming_angle["positive"] % leadBasicFactor))
        
        # Was 1.5, dist did not include close
        leadWeakFactor = 1.3
        leadingOGRules.append(ctrl.Rule(angle_velocity["negative low"] & (distance["far"] | distance["medium"] | distance["close"]) & (angle["negative"]), aiming_angle["negative"] % leadWeakFactor))
        leadingOGRules.append(ctrl.Rule(angle_velocity["positive low"] & (distance["far"] | distance["medium"] | distance["close"]) & (angle["positive"]), aiming_angle["positive"] % leadWeakFactor))
        

        # Get it to eventually stop aiming further on
        # Was 1
        weakeningFactor = 0
        leadingOGRules.append(ctrl.Rule(angle_velocity["negative high"] & (distance["far"] | distance["medium"]) & (angle["positive"] | angle["zero"]), aiming_angle["positive"] % weakeningFactor))
        leadingOGRules.append(ctrl.Rule(angle_velocity["positive high"] & (distance["far"] | distance["medium"]) & (angle["negative"] | angle["zero"]), aiming_angle["negative"] % weakeningFactor))

        leadingOGRules.append(ctrl.Rule(angle_velocity["negative low"] & (distance["far"] | distance["medium"]) & (angle["positive"] | angle["zero"]), aiming_angle["positive"] % weakeningFactor))
        leadingOGRules.append(ctrl.Rule(angle_velocity["positive low"] & (distance["far"] | distance["medium"]) & (angle["negative"] | angle["zero"]), aiming_angle["negative"] % weakeningFactor))

        
        activeRules = leadingRules # These are the active rules

        # creating a FIS controller from the rules + membership functions
        self.aiming_fis = ctrl.ControlSystem(activeRules)
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

        astAngle = np.arctan2(nearest_ast["velocity"][1], nearest_ast["velocity"][0])*180/np.pi
        # calculate angle velocity of asteroid relative to ship
        relative_velocity = np.sqrt(nearest_ast["velocity"][0]**2 + nearest_ast["velocity"][1]**2)*np.sin((astAngle-angle_to_ast)*np.pi/180)
        angle_velocity = np.clip(relative_velocity/(nearest_ast_dist), -1, 1)
        angle_velocity *= -1
        self.aiming_fis_sim.input["angle_velocity"] = angle_velocity

        if not self.frame % 10:
            #print(f"angleVel: {angle_velocity}")
            pass
        
        self.frame += 1

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
            self.normalization_dist = np.sqrt(game_state["map_size"][0]**2 + game_state["map_size"][1]**2)

        # normalize distance where (the max) 1 means it is an entire screen distance away
        norm_ast_distance = nearest_ast_dist/self.normalization_dist

        # feed asteroid dist and angle to the FIS
        self.aiming_fis_sim.input["angle"] = norm_relative_angle
        self.aiming_fis_sim.input["distance"] = norm_ast_distance
        #print(self.aiming_fis_sim._get_inputs())


        # compute fis output
        self.aiming_fis_sim.compute()
        # map normalized output to angle range [-180, 180], note that the output of the fis is determined by the membership functions and they go from -1 to 1
        try: 
            desired_aim_angle = self.aiming_fis_sim.output["aiming_angle"]*180.0
        except:
            print("Excepted")
            desired_aim_angle = 0

        # this converts the desired aiming angle to a control action to be fed to the ship in terms of turn rate
        # set turn rate to 0
        turn_rate = 0
        # if desired aim angle is outside of +- 1 deg, turn in that direction with max turn rate, otherwise don't turn
        threshold = 0.01
        if desired_aim_angle < -threshold:
            turn_rate = ship_state["turn_rate_range"][1] #abs(desired_aim_angle)
        elif desired_aim_angle > threshold:
            turn_rate = ship_state["turn_rate_range"][0]

        # set firing to always be true (fires as often as possible), all other values to 0
        thrust = 0
        fire = True
        drop_mine = False
        return thrust, turn_rate, fire, drop_mine

        
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
