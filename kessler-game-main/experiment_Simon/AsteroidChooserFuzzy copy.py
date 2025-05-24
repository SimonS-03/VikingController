# -*- coding: utf-8 -*-
# Copyright © 2022 Thales. All Rights Reserved.
# NOTICE: This file is subject to the license agreement defined in file 'LICENSE', which is part of
# this source code package.

import sys
sys.path.append('/Users/simon_stoll/Documents/programmering/KEX/Swedish-Vikings/kessler-game-main')

import src
from src.kesslergame import KesslerController, asteroid
from typing import Dict, Tuple
import skfuzzy.control as ctrl
import skfuzzy as skf
import numpy as np
from AstChooserGenome import AsteroidChooserGenome
import time

class AsteroidChooserOld:
    """Uses a FIS in order to select a relevant asteorid to shoot at."""
    def __init__(self, genome: AsteroidChooserGenome):
        self.genome = genome
        self.prevRelevance = np.inf
        self.callNumber = 0
        self.hasFiredDict = {}
        self.relevanceDict = {}
         # ============= Initializing Fuzzy system =================
        distance = ctrl.Antecedent(np.linspace(0, 1.0, 11), "distance")
        angle = ctrl.Antecedent(np.linspace(-1.0, 1.0, 11), "angle")
        size = ctrl.Antecedent(np.linspace(0, 1.0, 11), "size")

        relevance = ctrl.Consequent(np.linspace(0, 1.0, 11), "relevance")
        

        distance_names = ["close", "medium", "far"]
        angle_names = ["zero", "small", "large"]
        size_names = ["small", "medium", "large"]
        relevance_names = ["zero", "small", "large"]

        distance.automf(3, names=distance_names)
        angle.automf(3, names=angle_names)
        size.automf(3, names=size_names)
        relevance.automf(3, names=relevance_names)

        self.genome.ApplyToTrap(distance, distance_names, "distance")
        self.genome.ApplyToTrap(angle, angle_names, "angle")
        self.genome.ApplyToTrap(size, size_names, "size")
        self.genome.ApplyToTrap(relevance, relevance_names, "relevance")

        # ============= Fuzzy Rules ================
        rules = []
        rules.append(ctrl.Rule(angle["zero"], relevance["large"] % 3.0))
        rules.append(ctrl.Rule(angle["small"], relevance["small"] % 0.9))
        rules.append(ctrl.Rule(angle["large"], relevance["zero"] % 1.8))
    
        rules.append(ctrl.Rule(distance["close"], relevance["large"] % 0.2))
        rules.append(ctrl.Rule(distance["medium"], relevance["small"] % 0.3))
        rules.append(ctrl.Rule(distance["far"], relevance["zero"] % 0.1))
    
        rules.append(ctrl.Rule(size["small"], relevance["zero"] % 0.2))
        rules.append(ctrl.Rule(size["medium"], relevance["small"] % 0.2))
        rules.append(ctrl.Rule(size["large"], relevance["small"] % 0.3))


        # creating a FIS controller from the rules + membership functions and simulation to evaluate
        self.fis = ctrl.ControlSystem(rules)
        self.fis_sim = ctrl.ControlSystemSimulation(self.fis)
        
    def get_asteroid(self, ship_state: Dict, game_state: Dict) -> Dict:
        """Get most relevant asteroid."""
        
        self.callNumber = game_state["sim_frame"]

        # ============= Calculating relevance for asteroids ====================
        most_relevant = [-1, None] # [relevance score, asteroid instance]

        callFrequency = 2 # Every 5 frames we update an asteroids relevancy score
        callsUntilMiss = int(1//(game_state["delta_time"]*2))

        for asteroid in game_state["asteroids"]:
            
            velIndex = asteroid["velocity"]

            #if self.relevanceDict.__contains__(velIndex): print(self.relevanceDict[velIndex][1])

            # ============= Optimizations ================
            if self.relevanceDict.__contains__(velIndex) and self.relevanceDict[velIndex][1] == asteroid["velocity"]: 

                if self.relevanceDict[velIndex][3]:
                    if not self.relevanceDict[velIndex][4] + callsUntilMiss/(asteroid["size"])**4 < self.callNumber: # Quickly switch target if it has been fired upon
                        continue
                    else: self.relevanceDict[velIndex][3] = False

                #print(f"Indexed asteroid is identical for call number {self.callNumber}")
                if self.relevanceDict[velIndex][2] > self.callNumber: 
                    astRelevance = self.relevanceDict[velIndex][0]
                    #print(f"Skipped assessment for call number {self.callNumber}")
                    if astRelevance >= self.prevRelevance:
                        self.prevRelevance = astRelevance
                        return asteroid
                    
                    elif astRelevance > most_relevant[0]:
                        most_relevant = [astRelevance, asteroid]
                        self.prevRelevance = astRelevance
                    
                    continue

            # =============== Raw calculations =================
            astDist = np.sqrt((ship_state["position"][0] - asteroid["position"][0])**2 + (ship_state["position"][1] - asteroid["position"][1])**2)
            self.fis_sim.input["distance"] = astDist/np.sqrt(game_state["map_size"][0]**2 + game_state["map_size"][1]**2)
            self.fis_sim.input["size"] = asteroid["size"]/3

            ast_pos = asteroid["position"]
            astAngle = np.arctan2(ast_pos[1]-ship_state["position"][1], ast_pos[0]-ship_state["position"][0]) - ship_state["heading"]*np.pi/180
            if abs(astAngle) > np.pi:
                astAngle += -1*np.sign(astAngle)*2*np.pi
            astAngle /= np.pi # Normalizing to (-1.0, 1.0)
            self.fis_sim.input["angle"] = abs(astAngle)

            self.fis_sim.compute()
            
            
            try:
                astRelevance = self.fis_sim.output["relevance"]
                
                prevHasFired = self.relevanceDict[velIndex][3] if self.relevanceDict.__contains__(velIndex) else False
                prevFiredFrame = self.relevanceDict[velIndex][4] if self.relevanceDict.__contains__(velIndex) else -100
                self.relevanceDict[velIndex] = [astRelevance, asteroid["velocity"], self.callNumber + np.random.randint(0, 2*callFrequency+len(game_state["asteroids"])), prevHasFired, prevFiredFrame]
                
            except:
                print("excepted, relevance set to zero")
                astRelevance = 0


            if astRelevance >= self.prevRelevance:
                self.prevRelevance = astRelevance
                return asteroid
            
            if astRelevance >= most_relevant[0]:
                most_relevant[0] = astRelevance
                most_relevant[1] = asteroid

        self.prevRelevance = most_relevant[0]
        return most_relevant[1]
