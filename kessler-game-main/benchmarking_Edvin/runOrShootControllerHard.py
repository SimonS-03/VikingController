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


class combinedControllerHard(KesslerController):
    def __init__(self, framerate: int = 30):        
        self.shootingController = shooterController()
        self.evasionController = evasionController()
        self.simController = simulationController()
        self.called_sim_last_frame = True

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
        print("ttc", ttc)
        # Always simulate if low ttc
        if ttc < 1.5: # Simulation
            print("Using simulation in emergency")
            thrust, turn_rate, fire, drop_mine = self.simController.actions(ship_state, game_state, called_last_frame=self.called_sim_last_frame)
            fire = True
            self.called_sim_last_frame = True
            return thrust, turn_rate, fire, drop_mine

        # ------------------- Use danger function to decide on what module to use -------------------
        nearby_asteroids = self.get_num_asteroids(game_state, ship_state)
        
        c = 1
        # danger = c *(nearby_asteroids + 10/(1+ttc))
        danger = ttc
        print(f"danger {danger} nearby asteroids {nearby_asteroids}")


        # if danger < 5: # Simulation
        #     print("Using simulation")
        #     thrust, turn_rate, fire, drop_mine = self.simController.actions(ship_state, game_state, called_last_frame=self.called_sim_last_frame)
        #     fire = True
        #     self.called_sim_last_frame = True
            

        if danger < 2.5:
            print("Using gradient")
            thrust, turn_rate, fire, drop_mine = self.evasionController.actions(ship_state, game_state)
            self.called_sim_last_frame = False

        else:
            print("Shooting")
            self.called_sim_last_frame = False
            thrust, turn_rate, fire, drop_mine = self.shootingController.actions(ship_state, game_state)
            

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
        return "Hard controller"
