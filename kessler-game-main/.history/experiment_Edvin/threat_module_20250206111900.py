# Threat assessment fis


import skfuzzy.control

from src.kesslergame import KesslerController
from typing import Dict, Tuple
import skfuzzy.control as ctrl
import skfuzzy as skf

import numpy as np
import random
import sys

class ThreatAssessFIS:
    def __init__(self):
        self.threat_fis = None
        self.threat_fis_sim = None

        self.create_threat_fis()

    # assesses 
    def create_threat_fis(self, ship_state: Dict, game_state: Dict) -> float:
       
        # input 1 - Number of asteroids at distance r or closer to the ship
        asteroid_density = ctrl.Antecedent(np.linspace(0.0, 1.0, 11), "density")

        # input 2 - Average distance to the asteroids at distance r or closer
        distance_to_asteroids = ctrl.Antecedent(np.linspace(0.0, 1.0, 11), "average_distance")

        # output - Threat level
        threat_lvl = ctrl.Consequent(np.linspace(0.0, 1.0, 11))

        # create membership functions for the inputs
        asteroid_density.automf(3, names=["low", "medium", "high"])

        distance_to_asteroids.automf(3, names=["close", "medium", "far"])

        # create membershipfunctions for the outputs
        threat_lvl["low"] = skf.trapmf(threat_lvl.universe, [0.0, 0.0, 0.0, 0.5])
        threat_lvl["medium"] = skf.trapmf(threat_lvl.universe, [0.25, 0.5, 0.5, 0.75])
        threat_lvl["high"] = skf.trapmf(threat_lvl.universe, [0.5, 1.0, 1.0, 1.0])

        # create rulebase
        rule1 = ctrl.rule(asteroid_density["low"] & distance_to_asteroids["far"], threat_lvl["low"])
        rule2 = ctrl.rule(asteroid_density["medium"] & distance_to_asteroids["far"], threat_lvl["low"])
        rule3 = ctrl.rule(asteroid_density["high"] & distance_to_asteroids["far"], threat_lvl["medium"])
        rule4 = ctrl.rule(asteroid_density["low"] & distance_to_asteroids["medium"], threat_lvl["low"])
        rule5 = ctrl.rule(asteroid_density["medium"] & distance_to_asteroids["medium"], threat_lvl["medium"])
        rule6 = ctrl.rule(asteroid_density["high"] & distance_to_asteroids["medium"], threat_lvl["high"])
        rule7 = ctrl.rule(asteroid_density["low"] & distance_to_asteroids["close"], threat_lvl["medium"])
        rule8 = ctrl.rule(asteroid_density["medium"] & distance_to_asteroids["close"], threat_lvl["high"])
        rule9 = ctrl.rule(asteroid_density["high"] & distance_to_asteroids["close"], threat_lvl["high"])

        rules = [rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9]

        # creating a FIS controller
        self.threat_fis = ctrl.ControlSystem(rules)
        # creating a controller sim to evaluate the FIS
        self.threat_fis_sim = ctrl.ControlSystemSimulation(self.threat_fis)

    def action(self, ship_state, game_state):
        r = 500
        asteroid_idx = self.find_asteroids_inside_radius(ship_state, game_state, r)
        nbr_asteroids = len(asteroid_idx)

        # asteroid density, assuming each asteroid is of size 4 -> area = pi*(4*8)**2 = 3217
        norm_density = nbr_asteroids * 3217 / (np.pi*r**2)

        # capped at 1
        norm_density = min(1, norm_density)

        # average distance between the asteroids and the ship
        average_distance = 0
        for idx in asteroid_idx:
            current_asteroid = game_state["asteroid"][idx]
            dx = current_asteroid["position"][0]-ship_state["position"][0]
            dy = current_asteroid["position"][1]-ship_state["position"][1]
            average_distance += np.sqrt(dx**2 + dy**2)
        average_distance /= nbr_asteroids

        # normalize with r
        norm_distance_to_asteroids = average_distance / r
       
        # feed density and distance to the fis
        self.threat_fis_sim.input["density"] = norm_density
        self.threat_fis_sim.input["average_distance"] = norm_distance_to_asteroids

        # Finds index of all asteroids inside radius r
    def find_asteroids_inside_radius(ship_state: Dict, game_state: Dict, radius) -> list[int]:
        asteroid_idx = []
        for idx, asteroid in enumerate(game_state["asteroids"]):
            distance = np.sqrt((ship_state["position"][0] - asteroid["position"][0])**2 + (ship_state["position"][1] - asteroid["position"][1])**2)
            if distance < radius:
                asteroid_idx.append(idx)
        return asteroid_idx
