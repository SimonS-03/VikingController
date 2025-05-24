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
from exper_simulations.get_actions_using_simulations import GetActionsUsingSimulations as simulationController
from experiment_Simon.moduleChooserGenome import ModuleChooserGenome
#from experiment_Simon.genomeOld import Genome
import time
from numpy import array

noWeights4 = ModuleChooserGenome({'ttc': array([0.08863368, 0.2068125 , 0.6909625 , 0.98288594, 0.52511039,
       0.71183589]), 'asteroids': array([0.4105    , 0.48525   , 0.6484    , 0.82374762, 0.51649809,
       0.73035395]), 'gradient': array([0.06989327, 0.2876    , 0.58559472, 0.71707397, 0.63537179,
       0.70769368]), 'angle': array([0.42542831, 0.6081    , 0.9186    , 0.91864504, 0.55604928,
       0.76442373]), 'module': array([-0.07751164,  0.04852502,  0.58535965,  0.75      ,  0.69625183,
        0.93001884])})

overnighter = ModuleChooserGenome({'ttc': array([0.12981881, 0.49345425, 0.65391315, 0.90848213, 0.52511039,
       0.71183589]), 'asteroids': array([0.53116602, 0.59171103, 0.317     , 0.6646    , 0.51649809,
       0.73035395]), 'gradient': array([0.44545541, 0.6213318 , 0.26774878, 0.8758384 , 0.63537179,
       0.70769368]), 'angle': array([0.52500047, 0.73055   , 0.58543977, 0.9326641 , 0.55604928,
       0.76442373]), 'module': array([-0.3673    ,  0.3800073 ,  0.5773938 ,  0.64525   ,  0.69625183,
        0.93001884])})

class combinedController(KesslerController):
    def __init__(self, moduleChooserGenome: ModuleChooserGenome = overnighter):        
        self.shootingController = shooterController()
        self.evasionController = evasionController()
        self.simController = simulationController()
        self.called_sim_last_frame = False
        self.map = self.evasionController.map
        self.module = self.evasionController

        self.explainability = True # EXPLAINABILITY 
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
        
        if ttc*10 < 1.5:
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
