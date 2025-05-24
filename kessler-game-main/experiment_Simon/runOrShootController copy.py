# -*- coding: utf-8 -*-
# Copyright © 2022 Thales. All Rights Reserved.
# NOTICE: This file is subject to the license agreement defined in file 'LICENSE', which is part of
# this source code package.
import skfuzzy.control
import sys
sys.path.append('/Users/simon_stoll/Documents/programmering/KEX/Swedish-Vikings/kessler-game-main')
sys.path.append('/Users/Edvin/Documents/KTH3/KEX/Project/Swedish-Vikings/kessler-game-main')


from src.kesslergame import KesslerController, asteroid
from typing import Dict, Tuple
import skfuzzy.control as ctrl
import skfuzzy as skf
import numpy as np
from experiment_Simon.ShootingModule import shooterController
from experiment_Simon.EvasionModule import evasionController
from exper_simulations.get_actions_using_simulations_alt import GetActionsUsingSimulations as simulationController
from experiment_Simon.moduleChooserGenome import ModuleChooserGenome
#from experiment_Simon.genomeOld import Genome
import time

class combinedController(KesslerController):
    def __init__(self, moduleChooserGenome: ModuleChooserGenome):        
        self.shootingController = shooterController()
        self.evasionController = evasionController()
        self.simController = simulationController()
        self.called_sim_last_frame = False
        self.map = self.evasionController.map
        self.module = None

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
        
        self.map.update_map(ship_state, game_state) # Updating map and ttc
        grad = np.linalg.norm(self.map.weighted_gradient(ship_state["radius"], 4, ship_state, game_state))
        grad = np.clip(grad*2.5, 0, 1)
        #print(f"gradient is {grad}")
        ttc = np.clip(self.map.ship_ttc / 10, 0, 1)

        smallest_theta_diff = 1
        for ast in game_state["asteroids"]:
            diff = np.array(ast["position"]) - np.array(ship_state["position"])
            theta = np.arctan2(diff[1], diff[0])*180/np.pi
            theta_diff = (abs(ship_state["heading"]-theta))
            theta_diff = theta_diff-360 if theta_diff > 180 else theta_diff   
            theta_diff /= 180

            if abs(theta_diff) < smallest_theta_diff:
                smallest_theta_diff = abs(theta_diff)
        #print(f"Smallest theta diff is {smallest_theta_diff}")
        module_nbr = self.moduleChooser.get_module(ship_state, game_state, ttc, grad, smallest_theta_diff)
        
        self.called_sim_last_frame = False

        #print(f"module nbr is: {module_nbr}")
        if 0 <= module_nbr < 0.33:
            self.module = self.shootingController

        if 0.33 < module_nbr < 0.66:
            self.module = self.evasionController

        if 0.66 < module_nbr <= 1:
            if self.module == self.simController: self.called_sim_last_frame = True
            self.module = self.simController


        fire = False

        if self.module == self.simController: # Simulation
            thrust, turn_rate, fire_sim, drop_mine = self.simController.actions(ship_state, game_state, called_last_frame=self.called_sim_last_frame)
            self.called_sim_last_frame = True

        else:
            thrust, turn_rate, fire, drop_mine = self.module.actions(ship_state, game_state)
        
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

        module = ctrl.Consequent(np.linspace(0, 1.0, 11), "module")
        
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
        rules.append(ctrl.Rule(ttc["zero"], module["simulation"]))
        rules.append(ctrl.Rule(nbr_asteroids["large"], module["simulation"]))
        rules.append(ctrl.Rule(grad_magnitude["zero"] & (ttc["small"] | ttc["zero"]), module["simulation"]))

        # For descent module
        rules.append(ctrl.Rule(ttc["small"], module["descent"]))
        rules.append(ctrl.Rule(nbr_asteroids["zero"], module["descent"]))

        # For shooting module
        rules.append(ctrl.Rule(angle_to_closest_asteroid["zero"], module["shooting"]))
        rules.append(ctrl.Rule(ttc["large"], module["shooting"]))
        rules.append(ctrl.Rule(nbr_asteroids["zero"] & ttc["large"], module["shooting"]))


        # creating a FIS controller from the rules + membership functions and simulation to evaluate
        self.fis = ctrl.ControlSystem(rules)
        self.fis_sim = ctrl.ControlSystemSimulation(self.fis)
    
    def get_module(self, ship_state, game_state, ttc, grad, closest_ast_theta):
        """Return module number between 0 and 1. All inputs must be normalised (except ship_state and game_state)."""
        self.fis_sim.input["ttc"] = ttc
        self.fis_sim.input["asteroids"] = len(game_state["asteroids"])
        self.fis_sim.input["gradient"] = grad
        self.fis_sim.input["angle"] = closest_ast_theta

        self.fis_sim.compute()
        try:
            module = self.fis_sim.output["module"]
        except:
            module = 0.5 # Defaulting to descent
        return module
