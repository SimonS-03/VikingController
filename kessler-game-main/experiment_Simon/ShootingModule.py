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
from AstChooserGenome import AsteroidChooserGenome
from AsteroidChooserFuzzy import AsteroidChooser
from numpy import array
#from experiment_Simon.genomeOld import Genome
import time

class shooterController(KesslerController):
    def __init__(self, astChooserGenome: AsteroidChooserGenome = None, framerate: int = 30):
        self.cur_ast_vel = np.array((np.inf, np.inf))
        self.has_fired = False
        self.timeToHit = 0
        self.framesToHit = 0
        self.timeOfShot = time.time()
        self.cur_ast_size = 0
        self.shotsFired = 0
        self.frame = 0
        self.framerate = framerate
        self.framesSinceLastShot = 0
        self.desiredAngle = 0

        self.astChooserGenome = AsteroidChooserGenome({'angle': array([0.        , 0.38761215, 0.1107931 , 0.58357602, 0.69071515,
        0.88361165]), 'distance': array([0.15265988, 0.28503417, 0.95745695, 0.97783531, 0.83252896,
        0.91904276]), 'size': array([0.15262407, 0.44573077, 0.95392458, 0.97975342, 0.85713689,
        0.90948752]), 'relevance': array([0.26268984, 0.45705614, 0.46956284, 0.96877592, 0.65587678,
        0.93107172])}) if astChooserGenome is None else astChooserGenome # This preset was trained with the set_scenario_advanced with 200 generations
        
        self.astChooser = AsteroidChooser(self.astChooserGenome)


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

        asteroid = self.astChooser.get_asteroid(ship_state, game_state) # Get the most relevant asteroid using a FIS
        if asteroid == None:
            thrust = 0
            turn_rate = 0
            fire = False
            drop_mine = False
            return thrust, turn_rate, fire, drop_mine

        astDist = np.sqrt((ship_state["position"][0] - asteroid["position"][0])**2 + (ship_state["position"][1] - asteroid["position"][1])**2)
        estTime = astDist/800 # 800 is the bullet velocity
        newPos = np.array(asteroid["position"]) + np.array(asteroid["velocity"])*estTime
        astPosModified = np.array(asteroid["position"])
        
        if not(0 < newPos[0] < 1000):
            astPosModified[0] += -1*np.sign(newPos[0])*1000
        
        if not(0 < newPos[1] < 800):
            astPosModified[1] += -1*np.sign(newPos[1])*800

        # get cartesian components of position
        dx = astPosModified[0] - ship_state["position"][0]
        dy = astPosModified[1] - ship_state["position"][1]

        dxNext = (astPosModified[0] + asteroid["velocity"][0]/self.framerate) - ship_state["position"][0]
        dyNext = (astPosModified[1] + asteroid["velocity"][1]/self.framerate) - ship_state["position"][1]
        
        # calculate angle from ship to asteroid
        angle_to_ast = np.arctan2(dy, dx)*180/np.pi

        angle_to_ast_next = np.arctan2(dyNext, dxNext)*180/np.pi

        # calculate the angle to asteroid relative to the ship's current heading (resolve angle to ship frame instead of global frame)

        astAngle = np.arctan2(asteroid["velocity"][1], asteroid["velocity"][0])*180/np.pi
        
        # calculate angle velocity of asteroid relative to ship
        astVelocity = np.sqrt(asteroid["velocity"][0]**2 + asteroid["velocity"][1]**2)
        transversal_velocity = astVelocity*np.sin((astAngle-angle_to_ast)*np.pi/180)
        parallell_velocity = astVelocity*np.cos((astAngle-angle_to_ast)*np.pi/180)

        transversal_velocity_next = astVelocity*np.sin((astAngle-angle_to_ast_next)*np.pi/180)
        parallell_velocity_next = astVelocity*np.cos((astAngle-angle_to_ast_next)*np.pi/180)

        bullet_velocity = 800 # pixels per second
        dist_init = np.sqrt(dx**2 + dy**2)
        timeToHit = dist_init/(bullet_velocity - parallell_velocity)
  
        dist_init_next = np.sqrt(dxNext**2 + dyNext**2)
        timeToHit_next = dist_init/(bullet_velocity - parallell_velocity_next)

        # Compensating the approximation
        thetaSpeedComp = np.clip((astVelocity/250)**0.5, 1, 3)
        #print(f"Comp factor: {thetaSpeedComp}")

        theta_compensation = np.arctan2(transversal_velocity * timeToHit, dist_init + parallell_velocity*timeToHit) * thetaSpeedComp
        theta_compensation_next = np.arctan2(transversal_velocity_next * timeToHit_next, dist_init_next + parallell_velocity_next*timeToHit_next) * thetaSpeedComp

        theta_comp_deg = theta_compensation * 180 / np.pi
        theta_comp_deg_next = theta_compensation_next * 180 / np.pi
        
        desired_angle = ship_state["heading"] - (angle_to_ast + theta_comp_deg)
        
        desired_angle_next = ship_state["heading"] - (angle_to_ast_next + theta_comp_deg_next)

        # clamp angle to be within +- 180 deg from front of ship (makes reasoning about right/left easier, just a preference)
        if desired_angle < -180.0:
            desired_angle += 360
        
        elif desired_angle > 180.0:
            desired_angle -= 360

        if desired_angle_next < -180.0:
            desired_angle_next += 360
        
        elif desired_angle_next > 180.0:
            desired_angle_next -= 360
        
        self.desiredAngle = desired_angle_next

        turn_rate = np.clip(-desired_angle_next*self.framerate, ship_state["turn_rate_range"][0], ship_state["turn_rate_range"][1])
        
        self.framesToHit = (timeToHit * self.framerate) + 3

        new_vel = np.round(np.array(asteroid["velocity"]))
        #print(f"Frames to hit: {self.framesToHit}, time to hit: {timeToHit}")
        if (new_vel != self.cur_ast_vel).all() or (self.frame > self.framesToHit and self.shotsFired > 0):

                self.has_fired = False
                self.frame = 0
                self.shotsFired = 0
                #print("Reset")


        self.cur_ast_vel = np.round(np.array(asteroid["velocity"]))
        self.cur_ast_size = asteroid["size"]


        # set firing to always be true (fires as often as possible), all other values to 0
        thrust = 0
        
        maxShots = 1 + 1*(self.cur_ast_size-1)
        #print(f"Cur: {desired_angle}, next: {desired_angle_next}")
        #print(f"Frame {self.frame}")
        if abs(desired_angle) < 0.2 and (not self.has_fired) and self.framesSinceLastShot >= 3:
            self.shotsFired += 1
            
            fire = True
            self.framesSinceLastShot = 0
            #print(f"Shoot at frame {self.frame}")
            
        else:
            #print("Stop shooting")
            fire = False
        
        if self.shotsFired >= maxShots:
            self.has_fired = True
            hashKey = AsteroidChooser.get_hashKey(asteroid, game_state)
            self.astChooser.relevanceDict[hashKey][3] = True
            self.astChooser.relevanceDict[hashKey][4] = game_state["sim_frame"]

        if self.shotsFired == 0: self.frame = 0
        else: self.frame += 1

        drop_mine = False
        self.framesSinceLastShot += 1
        self.cur_ast_vel = asteroid["velocity"]
        return thrust, turn_rate, fire, drop_mine

        
    @property
    def name(self) -> str:
        """
        Simple property used for naming controllers such that it can be displayed in the graphics engine
 
        Returns:
            str: name of this controller
        """
        return "Scoring controller"
