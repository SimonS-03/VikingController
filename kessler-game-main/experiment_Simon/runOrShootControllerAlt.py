# -*- coding: utf-8 -*-
# Copyright © 2022 Thales. All Rights Reserved.
# NOTICE: This file is subject to the license agreement defined in file 'LICENSE', which is part of
# this source code package.
import skfuzzy.control
import sys
# sys.path.append('/Users/simon_stoll/Documents/programmering/KEX/Swedish-Vikings/kessler-game-main')
sys.path.append('/Users/Edvin/Documents/KTH3/KEX/Project/Swedish-Vikings/kessler-game-main')


from src.kesslergame import KesslerController, asteroid
from typing import Dict, Tuple
import skfuzzy.control as ctrl
import skfuzzy as skf
import numpy as np
from experiment_Simon.ShootingModule import shooterController
from experiment_Simon.EvasionModule import evasionController
from exper_simulations.get_actions_using_simulations import GetActionsUsingSimulations as simulationController
#from experiment_Simon.genomeOld import Genome
import time

# jag testade att göra en

class combinedControllerAlt(KesslerController):
    def __init__(self, framerate: int = 30):        
        self.shootingController = shooterController()
        self.evasionController = evasionController()
        self.simController = simulationController()
        self.called_sim_last_frame = True
        
        # FIS
        self.fis = None
        self.fis_sim = None
        self.create_fis()
    
    def create_fis(self):
        # =========================== Defining in- and output ==================================

        # input 1 - time to collision 
        ttc = ctrl.Antecedent(np.linspace(0.0, 1.0, 11), "ttc")
        # input 2 - number of nearby asteroids
        nearby_asteroids = ctrl.Antecedent(np.linspace(0.0, 1.0, 11), "nearby_asteroids")

        # output 1 - danger value
        danger = ctrl.Consequent(np.linspace(0.0, 1.0, 11), "danger")
        # =========================== Creating membership functions ================================

        ttc.automf(3, names=["low", "medium", "high"])
        nearby_asteroids.automf(3, names=["few", "medium", "many"])
        danger.automf(3, names=["low", "medium", "high"]) 

        """self.genome.ApplyToTrap(desired_speed, ["low", "medium", "high"], "desired_speed")
        self.genome.ApplyToTrap(current_speed, ["low", "medium", "high"], "current_speed")
        self.genome.ApplyToTrap(relative_angle, ["negative", "zero", "positive"], "relative_angle")"""

        # =========================== Rules for FIS ========================================

        rule1 = ctrl.Rule(ttc["high"] & nearby_asteroids["few"], danger["low"])
        rule2 = ctrl.Rule(ttc["high"] & nearby_asteroids["medium"], danger["low"])
        rule3 = ctrl.Rule(ttc["high"] & nearby_asteroids["many"], danger["medium"])
        rule4 = ctrl.Rule(ttc["medium"] & nearby_asteroids["few"], danger["low"])
        rule5 = ctrl.Rule(ttc["medium"] & nearby_asteroids["medium"], danger["medium"])
        rule6 = ctrl.Rule(ttc["medium"] & nearby_asteroids["many"], danger["high"])
        rule7 = ctrl.Rule(ttc["low"] & nearby_asteroids["few"], danger["high"])
        rule8 = ctrl.Rule(ttc["low"] & nearby_asteroids["medium"], danger["high"])
        rule9 = ctrl.Rule(ttc["low"] & nearby_asteroids["many"], danger["high"])

        rules = [rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9]#, rule10, rule11, rule12, rule13, rule14, rule1a, rule2a, rule3a]

        # =========================== Create a FIS controller and sim ===============================
        self.fis = ctrl.ControlSystem(rules)
        self.fis_sim = ctrl.ControlSystemSimulation(self.fis)    

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
        self.evasionController.map.update_map(ship_state, game_state) # Updating map and ttc
        ttc = self.evasionController.map.ship_ttc

        # Always simulate if low ttc
        if ttc < 3: # Simulation
            print("Using simulation")
            thrust, turn_rate, fire, drop_mine = self.simController.actions(ship_state, game_state, called_last_frame=self.called_sim_last_frame)
            fire = True
            self.called_sim_last_frame = True
            return thrust, turn_rate, fire, drop_mine

        # ------------------- Use the fuzzy system to decide on what module to use -------------------
        norm_ttc = ttc/10 if ttc < 10 else 1

        nearby_asteroids = self.get_num_asteroids(game_state, ship_state)

        # normalize using the max speed of 240 m/s
        norm_nearby_asteroids = nearby_asteroids/10 if nearby_asteroids < 10 else 1

        self.fis_sim.input["ttc"] = norm_ttc
        self.fis_sim.input["nearby_asteroids"] = norm_nearby_asteroids

        # compute fis output
        self.fis_sim.compute()

        danger = self.fis_sim.output["danger"]

        if danger > 0.6: # Simulation
            print("Using simulation")
            thrust, turn_rate, fire, drop_mine = self.simController.actions(ship_state, game_state, called_last_frame=self.called_sim_last_frame)
            fire = True
            self.called_sim_last_frame = True
            

        elif danger > 0.45:
            print("Using gradient")
            thrust, turn_rate, fire, drop_mine = self.evasionController.actions(ship_state, game_state)
            self.called_sim_last_frame = False
        
        else:
            print("Shooting")
            self.called_sim_last_frame = False
            thrust, turn_rate, fire, drop_mine = self.shootingController.actions(ship_state, game_state)
            
        
        # if not self.called_sim_last_frame: print("False")
        #fire = True
        return thrust, turn_rate, fire, drop_mine

    def get_num_asteroids(self, game_state: Dict, ship_state: Dict) -> int:
        radius = 50
        counter = 0
        ship_pos = ship_state["position"]
        for asteroid in game_state["asteroids"]:
            
            dx = ship_pos[0] - asteroid["position"][0]
            dy = ship_pos[1] - asteroid["position"][1]
            dist = np.sqrt(dx**2 + dy**2)
            if dist < radius:
                counter += 1
        
        return counter

        
    @property
    def name(self) -> str:
        """
        Simple property used for naming controllers such that it can be displayed in the graphics engine
 
        Returns:
            str: name of this controller
        """
        return "Scoring controller"
