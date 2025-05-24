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

class AsteroidChooser:
    """Uses a FIS in order to select a relevant asteorid to shoot at."""
    def __init__(self, genome: AsteroidChooserGenome):
        self.genome = genome
        self.prevRelevance = np.inf
        self.callNumber = 0
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
    
        rules.append(ctrl.Rule(size["small"], relevance["large"] % 0.5)) # was 0.2
        rules.append(ctrl.Rule(size["medium"], relevance["small"] % 0.5)) # 0.2
        rules.append(ctrl.Rule(size["large"], relevance["zero"] % 0.5)) # 0.3


        # creating a FIS controller from the rules + membership functions and simulation to evaluate
        self.fis = ctrl.ControlSystem(rules)
        self.fis_sim = ctrl.ControlSystemSimulation(self.fis)
    
    def get_hashKey(asteroid: Dict, game_state: Dict):
        "Returns a hash key for an asteroid"
        initialPos = (round(asteroid["position"][0]-game_state["time"]*asteroid["velocity"][0], 3), round(asteroid["position"][1]-game_state["time"]*asteroid["velocity"][1], 3))
        return hash((initialPos, asteroid["velocity"], asteroid["mass"], asteroid["radius"], asteroid["size"]))

    def get_asteroid(self, ship_state: Dict, game_state: Dict) -> Dict:
        """Get most relevant asteroid."""
        
        self.callNumber = game_state["sim_frame"]
        
        # ============= Calculating relevance for asteroids ====================
        most_relevant = [-100, None] # [relevance score, asteroid instance]

        callFrequency = 15 # Every 5 frames we update an asteroids relevancy score
        callsUntilMiss = int(1//(game_state["delta_time"]*2))

        for asteroid in game_state["asteroids"]:
            hashKey = AsteroidChooser.get_hashKey(asteroid, game_state)

            # ============= Optimizations ================
            if self.relevanceDict.__contains__(hashKey): 

                if self.relevanceDict[hashKey][3]:
                    if ((self.relevanceDict[hashKey][4] + callsUntilMiss/(asteroid["size"])**4) > self.callNumber): # Quickly switch target if it has been fired upon
                        continue
                    else: self.relevanceDict[hashKey][3] = False

                #print(f"Indexed asteroid is identical for call number {self.callNumber}")
                if self.relevanceDict[hashKey][2] > self.callNumber: 
                    astRelevance = self.relevanceDict[hashKey][0]
                    #print(f"Skipped assessment for call number {self.callNumber}")
                    
                    if astRelevance >= self.prevRelevance:
                        self.prevRelevance = astRelevance
                        return asteroid
                    
                    if astRelevance > most_relevant[0]:
                        most_relevant = [astRelevance, asteroid]
                    
                    continue

            # =============== Raw calculations =================
            astDist = np.sqrt((ship_state["position"][0] - asteroid["position"][0])**2 + (ship_state["position"][1] - asteroid["position"][1])**2)
            estTime = astDist/800 # 800 is the bullet velocity
            newPos = np.array(asteroid["position"]) + np.array(asteroid["velocity"])*estTime
            astPosModified = np.array(asteroid["position"])
            
            if not(0 < newPos[0] < 1000):
                astPosModified[0] += -1*np.sign(newPos[0])*1000
            
            if not(0 < newPos[1] < 800):
                astPosModified[1] += -1*np.sign(newPos[1])*800

            astDist = np.sqrt((ship_state["position"][0] - astPosModified[0])**2 + (ship_state["position"][1] - astPosModified[1])**2)

            self.fis_sim.input["distance"] = astDist/np.sqrt(game_state["map_size"][0]**2 + game_state["map_size"][1]**2)
            self.fis_sim.input["size"] = asteroid["size"]/3


            astAngle = np.arctan2(astPosModified[1]-ship_state["position"][1], astPosModified[0]-ship_state["position"][0]) - ship_state["heading"]*np.pi/180
            if abs(astAngle) > np.pi:
                astAngle += -1*np.sign(astAngle)*2*np.pi
            astAngle /= np.pi # Normalizing to (-1.0, 1.0)
            self.fis_sim.input["angle"] = abs(astAngle)

            self.fis_sim.compute()
            
            
            try:
                astRelevance = self.fis_sim.output["relevance"]

                prevHasFired = self.relevanceDict[hashKey][3] if self.relevanceDict.__contains__(hashKey) else False
                prevFiredFrame = self.relevanceDict[hashKey][4] if self.relevanceDict.__contains__(hashKey) else game_state["sim_frame"]
                self.relevanceDict[hashKey] = [astRelevance, asteroid["velocity"], self.callNumber + np.random.randint(callFrequency, callFrequency+len(game_state["asteroids"])), prevHasFired, prevFiredFrame]
                
            except:
                print("excepted, relevance set to zero")
                astRelevance = 0


            if astRelevance > self.prevRelevance:
                self.prevRelevance = astRelevance
                return asteroid
            
            if astRelevance >= most_relevant[0]:
                most_relevant[0] = astRelevance
                most_relevant[1] = asteroid

        self.prevRelevance = most_relevant[0]
        return most_relevant[1]
