# -*- coding: utf-8 -*-
# Copyright © 2022 Thales. All Rights Reserved.
# NOTICE: This file is subject to the license agreement defined in file 'LICENSE', which is part of
# this source code package.

import sys


from src.kesslergame import KesslerController, asteroid
from typing import Dict, Tuple
import skfuzzy.control as ctrl

import numpy as np
from ShootingModule import shooterController
from EvasionModule import evasionController
from get_actions_using_simulations import GetActionsUsingSimulations as simulationController
from moduleChooserGenome import ModuleChooserGenome

from numpy import array

overnighter = ModuleChooserGenome({'ttc': array([0.20164909, 0.75      , 0.70171702, 0.84942884, 0.52511039,
       0.71183589]), 'asteroids': array([0.        , 0.4391    , 0.56679222, 0.86817032, 0.51649809,
       0.73035395]), 'gradient': array([0.42434045, 0.6386    , 0.27178445, 0.541925  , 0.63537179,
       0.70769368]), 'angle': array([0.59137407, 0.68218232, 0.56470047, 0.82534179, 0.55604928,
       0.76442373]), 'module': array([-0.25618976,  0.37292393,  0.47954814,  0.63411415,  0.69625183,
        0.93001884])})

class combinedController(KesslerController):
    def __init__(self, moduleChooserGenome: ModuleChooserGenome = overnighter):
        self.reset(moduleChooserGenome = overnighter)   
        
    def reset(self, moduleChooserGenome: ModuleChooserGenome = overnighter):
        self.shootingController = shooterController()
        self.evasionController = evasionController()
        self.simController = simulationController()
        self.called_sim_last_frame = False
        self.map = self.evasionController.map
        self.module = self.evasionController

        self.explainability = False # EXPLAINABILITY 
        self.map.explain = self.explainability

        self.moduleChooser = ModuleChooser(moduleChooserGenome)

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

        # check if a new game state has been created
        if game_state["time"] == 0.0:
            self.reset()
        
        self.map.actions(ship_state, game_state) # Updating map and ttc
        grad = np.linalg.norm(self.map.weighted_gradient(ship_state["radius"], 4, ship_state, game_state))
        grad = np.clip(grad*4, 0, 1)
        #print(f"gradient is {grad}")
        ttc = np.clip(self.map.ship_ttc / 10, 0, 1)
        #print(ttc)

        close_asteroids = 0
        smallest_theta_diff = 1
        dist_to_smallest_theta = 10000
        
        for ast in game_state["asteroids"]:
            diff = (np.array(ast["position"]) - np.array(ship_state["position"]))
            
            if np.linalg.norm(diff) < 200 or np.linalg.norm(diff) > 900: close_asteroids += 1
            
            theta = np.arctan2(diff[1], diff[0])*180/np.pi
            theta_diff = (abs(ship_state["heading"]-theta))
            theta_diff = theta_diff-360 if theta_diff > 180 else theta_diff   
            theta_diff /= 180

            if abs(theta_diff) < smallest_theta_diff:
                smallest_theta_diff = abs(theta_diff)
                dist_to_smallest_theta = np.linalg.norm(diff)
                
        #print(f"Smallest theta diff is {smallest_theta_diff}")
        #print(f"close asteroids: {close_asteroids}")

        module_nbr = self.moduleChooser.get_module(ship_state, game_state, ttc, grad, smallest_theta_diff, close_asteroids)
        
        self.called_sim_last_frame = False

        #if smallest_theta_diff < 0.02: fire = True
        debugging = False
        fire = False
        #if debugging: print(f"ttc is {ttc}")
        
        if ttc*10 < 1.2:
            if self.module != self.simController and debugging: print("Switched to SIMULATION with exception")
            if self.module == self.simController: self.called_sim_last_frame = True
            self.module = self.simController
            thrust, turn_rate, fire_sim, drop_mine = self.simController.actions(ship_state, game_state, called_last_frame=self.called_sim_last_frame)
            self.map.moduleActive = "Module: Simulations (emergency)"
            #fire = True
            
        else: 
            #if np.random.randint(0, 10) == 2 and debugging: print(f"module nbr is: {module_nbr}")
            if module_nbr < 0.3:
                if self.module != self.shootingController and debugging: print("Switched to shooting")
                self.module = self.shootingController
                self.map.moduleActive = "Module: Scoring"

            elif 0.3 < module_nbr < 0.45:
                if self.module != self.evasionController and debugging: print("Switched to evasion")
                self.module = self.evasionController
                self.map.moduleActive = "Module: Gradient Ascent"

            elif ttc*10 > 3:
                if self.module != self.evasionController and debugging: print("Switched to evasion")
                self.module = self.evasionController
                self.map.moduleActive = "Module: Gradient Ascent"

            elif 0.45 < module_nbr <= 1:
                if self.module != self.simController and debugging: print("Switched to SIMULATION")
                if self.module == self.simController: self.called_sim_last_frame = True
                self.module = self.simController
                self.map.moduleActive = "Module: Simulations"


            if self.module == self.simController: # Simulation
                thrust, turn_rate, fire_sim, drop_mine = self.simController.actions(ship_state, game_state, called_last_frame=self.called_sim_last_frame)

            elif self.module == self.evasionController:
                thrust, turn_rate, fire_module, drop_mine = self.module.actions(ship_state, game_state)
            
            elif self.module == self.shootingController:
                thrust, turn_rate, fire, drop_mine = self.shootingController.actions(ship_state, game_state)
        
            if self.module == self.simController or self.module == self.evasionController:
                if smallest_theta_diff < 0.04 and dist_to_smallest_theta < 400: fire = True

        

        return thrust, turn_rate, fire, drop_mine

    @property
    def name(self) -> str:
        """
        Simple property used for naming controllers such that it can be displayed in the graphics engine
 
        Returns:
            str: name of this controller
        """
        return "Scoring controller"
    

class ModuleChooser:
    """Uses a FIS in order to select a relevant asteorid to shoot at."""
    def __init__(self, genome: ModuleChooserGenome = ModuleChooserGenome()):
        self.genome = genome

        self.callNumber = 0

         # ============= Initializing Fuzzy system =================
        ttc = ctrl.Antecedent(np.linspace(0, 1.0, 11), "ttc")
        nbr_asteroids = ctrl.Antecedent(np.linspace(0, 1.0, 11), "asteroids")
        grad_magnitude = ctrl.Antecedent(np.linspace(0, 1.0, 11), "gradient")
        angle_to_closest_asteroid = ctrl.Antecedent(np.linspace(0, 1.0, 11), "angle")

        module = ctrl.Consequent(np.linspace(-0.5, 1.0, 11), "module")
        
        names3 = ["zero", "small", "large"]

        module_names = ["shooting", "descent", "simulation"]

        ttc.automf(3, names=names3)
        nbr_asteroids.automf(3, names=names3)
        grad_magnitude.automf(3, names=names3)
        angle_to_closest_asteroid.automf(3, names=names3)
        module.automf(3, names = module_names)

        self.genome.ApplyToTrap(ttc, names3, "ttc")
        self.genome.ApplyToTrap(nbr_asteroids, names3, "asteroids")
        self.genome.ApplyToTrap(grad_magnitude, names3, "gradient")
        self.genome.ApplyToTrap(angle_to_closest_asteroid, names3, "angle")
        self.genome.ApplyToTrap(module, module_names, "module")

        # ============= Fuzzy Rules ================
        rules = []
        # For simulation module

        rules.append(ctrl.Rule(ttc["zero"] & nbr_asteroids["large"], module["simulation"])) # 4
        rules.append(ctrl.Rule(ttc["zero"] & nbr_asteroids["small"], module["simulation"])) # 2
        rules.append(ctrl.Rule(nbr_asteroids["large"], module["simulation"])) # 4
        rules.append(ctrl.Rule(grad_magnitude["zero"] & ttc["zero"], module["simulation"])) # 4

        # For descent module
        rules.append(ctrl.Rule(ttc["zero"], module["descent"])) # 1
        rules.append(ctrl.Rule(nbr_asteroids["small"], module["descent"]))
        rules.append(ctrl.Rule(grad_magnitude["large"], module["descent"])) # 4 
        rules.append(ctrl.Rule(grad_magnitude["large"] & ttc["small"], module["descent"])) # 2

        # For shooting module
        rules.append(ctrl.Rule(ttc["large"], module["shooting"])) # was 4
        rules.append(ctrl.Rule(angle_to_closest_asteroid["zero"] & ttc["small"], module["shooting"]))
        rules.append(ctrl.Rule(nbr_asteroids["zero"], module["shooting"]))

        # creating a FIS controller from the rules + membership functions and simulation to evaluate
        self.fis = ctrl.ControlSystem(rules)
        self.fis_sim = ctrl.ControlSystemSimulation(self.fis)
    
    def get_module(self, ship_state, game_state, ttc, grad, closest_ast_theta, close_asteroids):
        """Return module number between 0 and 1. All inputs must be normalised (except ship_state and game_state)."""
        self.fis_sim.input["ttc"] = ttc
        self.fis_sim.input["asteroids"] = np.clip(close_asteroids/15, 0, 1)
        self.fis_sim.input["gradient"] = grad
        self.fis_sim.input["angle"] = closest_ast_theta

        self.fis_sim.compute()
        try:
            module = self.fis_sim.output["module"]
        except:
            module = 0.5 # Defaulting to descent
        return module
