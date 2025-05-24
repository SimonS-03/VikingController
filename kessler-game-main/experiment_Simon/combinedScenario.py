# -*- coding: utf-8 -*-
# Copyright © 2022 Thales. All Rights Reserved.
# NOTICE: This file is subject to the license agreement defined in file 'LICENSE', which is part of
# this source code package.

#import time
import sys
import os
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from numpy import array
from src.kesslergame import Scenario, KesslerGame, GraphicsType, TrainerEnvironment, kessler_game
from moduleChooserGenome import ModuleChooserGenome
from runOrShootController import combinedController
from exper_simulations.get_actions_using_simulations import GetActionsUsingSimulations
from EvasionModule import evasionController
from survivalBenchmark import get_randomized_scenario
#from experiment_Simon.genomeOld import Genome

# Define game scenario
# my_test_scenario = Scenario(name='Test Scenario',
#                             num_asteroids=10,
#                             ship_states=[
#                                 {'position': (400, 400), 'angle': 0, 'lives': 3, 'team': 1, "mines_remaining": 3},
#                                 # {'position': (400, 600), 'angle': 90, 'lives': 3, 'team': 2, "mines_remaining": 3},
#                             ],
#                             map_size=(1000, 800),
#                             time_limit=60,
#                             ammo_limit_multiplier=0,
#                             stop_if_no_ammo=False)

astSpeed = 100
set_scenario = Scenario(name='Test Scenario',
                            asteroid_states=[{'position': (-100, 200), 'angle': 90, 'speed': astSpeed, 'size': 3},
                                             {'position': (-800, 400), 'angle': 90, 'speed': astSpeed, 'size': 3},
                                             {'position': (-800, 50), 'angle': 0, 'speed': astSpeed, 'size': 1},
                                             {'position': (50, 50), 'angle': 0, 'speed': astSpeed, 'size': 3}],
                            ship_states=[
                                {'position': (400, 400), 'angle': np.random.randint(0, 360), 'lives': 100, 'team': 1, "mines_remaining": 3},
                                # {'position': (400, 600), 'angle': 90, 'lives': 3, 'team': 2, "mines_remaining": 3},
                            ],
                            map_size=(1000, 800),
                            time_limit=100,
                            ammo_limit_multiplier=0,
                            stop_if_no_ammo=False)

set_scenario_advanced = Scenario(name='Test Scenario',
                            asteroid_states=[{'position': (-100, 200), 'angle': 90, 'speed': astSpeed, 'size': 3},
                                             {'position': (-800, 400), 'angle': 90, 'speed': astSpeed*0.2, 'size': 3},
                                             {'position': (-800, 50), 'angle': -140, 'speed': astSpeed*0.4, 'size': 1},
                                             {'position': (50, 50), 'angle': -20, 'speed': astSpeed*2, 'size': 3},
                                             {'position': (-400, 50), 'angle': -89, 'speed': astSpeed*0.9, 'size': 2},
                                             {'position': (-500, 700), 'angle': 37, 'speed': astSpeed*0.3, 'size': 2},
                                             {'position': (800, 750), 'angle': 140, 'speed': astSpeed*0.4, 'size': 3},
                                             {'position': (200, 560), 'angle': 45, 'speed': astSpeed*1.5, 'size': 2},
                                             {'position': (-20, 290), 'angle': 19, 'speed': astSpeed*0.9, 'size': 1}],
                            ship_states=[
                                {'position': (400, 400), 'angle': np.random.randint(0, 360), 'lives': 100, 'team': 1, "mines_remaining": 3},
                                # {'position': (400, 600), 'angle': 90, 'lives': 3, 'team': 2, "mines_remaining": 3},
                            ],
                            map_size=(1000, 800),
                            time_limit=100,
                            ammo_limit_multiplier=0,
                            stop_if_no_ammo=False)

oneAst = Scenario(name='Test Scenario',
                            asteroid_states=[{'position': (800, 400), 'angle': 180, 'speed': 50, 'size': 3}],
                            ship_states=[
                                {'position': (400, 400), 'angle': np.random.randint(0, 360), 'lives': 100, 'team': 1, "mines_remaining": 3},
                                # {'position': (400, 600), 'angle': 90, 'lives': 3, 'team': 2, "mines_remaining": 3},
                            ],
                            map_size=(1000, 800),
                            time_limit=200,
                            ammo_limit_multiplier=0,
                            stop_if_no_ammo=False)

dynamic_scenario = Scenario(name='Test Scenario',
                           num_asteroids = 6,
                            ship_states=[
                                {'position': (400, 400), 'angle': np.random.randint(0, 359), 'lives':100, 'team': 1, "mines_remaining": 3}
                                #{'position': (400, 600), 'angle': 90, 'lives': 100, 'team': 2, "mines_remaining": 3},
                            ],
                            map_size=(1000, 800),
                            time_limit=80,
                            ammo_limit_multiplier=0,
                            stop_if_no_ammo=False
                            )
# Define Game Settings

dynamic_graphic_scenario = Scenario(name='Test Scenario',
                           num_asteroids = 2,
                            ship_states=[
                                {'position': (400, 400), 'angle': np.random.randint(0, 359), 'lives':10, 'team': 1, "mines_remaining": 3},
                                # {'position': (400, 600), 'angle': 90, 'lives': 3, 'team': 2, "mines_remaining": 3},
                            ],
                            map_size=(1000, 800),
                            time_limit=200,
                            ammo_limit_multiplier=0,
                            stop_if_no_ammo=False)

def crossing():
    asteroid_states = []
    # gap_y = 400  # vertical gap at y = 400
    # for y in range(0, 800, 25):
    #     if not (gap_y - 100 < y < gap_y + 100):  # leave a gap 200 pixels wide
    #         asteroid_states.append({'position': (-100, y), 'angle': 180, 'speed': 130, 'size': 3})
    
    for y in range(0, 800, 25):
        # if not (gap_y - 100 < y < gap_y + 100):  # leave a gap 200 pixels wide
        asteroid_states.append({'position': (1100, y), 'angle': 0, 'speed': 130, 'size': 3})

    scenario = Scenario(
            name='Chaotic Asteroid Storm',
            asteroid_states=asteroid_states,
            ship_states=[
                # Team 1 (left side)
                {'position': (600, 600), 'angle': 0, 'lives': 1, 'team': 1, 'mines_remaining': 3}
                # Team 2 (right side)
                #{'position': (600, 200), 'angle': 0, 'lives': 100, 'team': 2, 'mines_remaining': 3},
            ],
            map_size=(1000, 800),
            time_limit=300,  # 2-minute survival/combat
            ammo_limit_multiplier=0,  # Infinite ammo (focus on navigation)
            stop_if_no_ammo=False
        )
    return scenario

def vortex():
    asteroid_states = []
    center = (500, 400)
    for i in range(50):
        angle = i * 360 / 50
        asteroid_states.append({
            'position': (center[0] + np.cos(np.deg2rad(angle)) * 300,
                        center[1] + np.sin(np.deg2rad(angle)) * 300),
            'angle': (angle + 90) % 360,  # moving tangentially
            'speed': astSpeed,
            'size': 2,
        })
    scenario = Scenario(
            name='Chaotic Asteroid Storm',
            asteroid_states=asteroid_states,
            ship_states=[
                # Team 1 (left side)
                {'position': (600, 600), 'angle': 0, 'lives': 1, 'team': 1, 'mines_remaining': 3}
                # Team 2 (right side)
                #{'position': (600, 200), 'angle': 0, 'lives': 100, 'team': 2, 'mines_remaining': 3},
            ],
            map_size=(1000, 800),
            time_limit=30,  # 2-minute survival/combat
            ammo_limit_multiplier=0,  # Infinite ammo (focus on navigation)
            stop_if_no_ammo=False
        )
    return scenario


def cluster():
    asteroid_states = []
    center_x, center_y = 500, 400
    for angle in range(0, 360, 10):
        asteroid_states.append({'position': (center_x + np.random.randint(-50, 50),
                                            center_y + np.random.randint(-50, 50)),
                                'angle': angle, 'speed': astSpeed, 'size': 3})
    scenario = Scenario(
            name='Chaotic Asteroid Storm',
            asteroid_states=asteroid_states,
            ship_states=[
                # Team 1 (left side)
                {'position': (600, 600), 'angle': 0, 'lives': 100, 'team': 1, 'mines_remaining': 3}
                # Team 2 (right side)
                #{'position': (600, 200), 'angle': 0, 'lives': 100, 'team': 2, 'mines_remaining': 3},
            ],
            map_size=(1000, 800),
            time_limit=30,  # 2-minute survival/combat
            ammo_limit_multiplier=0,  # Infinite ammo (focus on navigation)
            stop_if_no_ammo=False
        )
    return scenario


def traffic():
    asteroid_states = []
    for x in range(0, 1000, 100):
        for y in range(0, 800, 100):
            if (x//100) % 2 != 0:
                asteroid_states.append({'position': (x, y+50), 'angle': 0, 'speed': 100, 'size': 2})
            else:
                asteroid_states.append({'position': (x, y), 'angle': 0, 'speed': 100, 'size': 2})

    scenario = Scenario(
            name='Chaotic Asteroid Storm',
            asteroid_states=asteroid_states,
            ship_states=[
                # Team 1 (left side)
                {'position': (600, 650), 'angle': 0, 'lives': 100, 'team': 1, 'mines_remaining': 3}
            ],
            map_size=(1000, 800),
            time_limit=120,  # 2-minute survival/combat
            ammo_limit_multiplier=0,  # Infinite ammo (focus on navigation)
            stop_if_no_ammo=False
        )
    return scenario

game_settings = {'graphics_type': None,
                 'realtime_multiplier': 0,
                 'frequency': 30}


graphics_game_settings = {'graphics_type': GraphicsType.Tkinter,
                 'realtime_multiplier': 1,
                 'frequency':30}


score = 0
scenario = None

def createNewScenario(nbr_asteroids: int, mean_speed: float, time_limit: float, lives: int = 3):
    global scenario
    scenario = get_randomized_scenario(nbr_asteroids = nbr_asteroids, mean_speed = mean_speed, time_limit = time_limit, lives = lives)
    return scenario



def runScenario(moduleChooserGenome: ModuleChooserGenome = ModuleChooserGenome(), graphics: bool = False) -> kessler_game.Score:

    if graphics: 
        game = KesslerGame(settings=graphics_game_settings)  # Use this to visualize the game scenario
        #score, perf_data = game.run(scenario=scenario, controllers=[combinedController(moduleChooserGenome)])
        score, perf_data = game.run(scenario=scenario, controllers=[combinedController(moduleChooserGenome)])
    
    else:
        game = TrainerEnvironment(settings=game_settings)  # Use this to visualize the game scenario
        score, perf_data = game.run(scenario=scenario, controllers=[combinedController(moduleChooserGenome)])
    
    team_scores = [team.asteroids_hit for team in score.teams]
    hits = team_scores[0]
    accuracy = score.teams[0].accuracy
    print(f"Hits: {hits}, acc: {round(accuracy, 2)}, time: {round(score.sim_time, 2)}")
    
    if False:
        # Print out some general info about the result
        print('Scenario eval time: '+str(time.perf_counter()-pre))
        print(score.stop_reason)
        print(str(score.stop_reason == kessler_game.StopReason.time_expired))
        print('Asteroids hit: ' + str([team.asteroids_hit for team in score.teams]))
        print('Deaths: ' + str([team.deaths for team in score.teams]))
        print('Accuracy: ' + str([team.accuracy for team in score.teams]))
        print('Mean eval time: ' + str([team.mean_eval_time for team in score.teams]))

    return score


def main():
    genome = ModuleChooserGenome({'ttc': array([0.35136837, 0.56828825, 0.28731017, 0.5123    , 0.67352783,
       0.82602995]), 'asteroids': array([0.5277166 , 0.75      , 0.47032659, 0.86462135, 0.66251344,
       0.84894466]), 'gradient': array([0.2473    , 0.51106308, 0.59371886, 0.81912705, 0.68945456,
       0.77981143]), 'angle': array([0.56737974, 0.67431904, 0.64336847, 0.86985   , 0.66840271,
       0.81090022]), 'module': array([-0.5       ,  0.33623879,  0.11057203,  0.39727597,  0.50210331,
        0.72355985])}) # Pretty Good!!!
    
    gen17 = ModuleChooserGenome({'ttc': array([0.15605311, 0.2915201 , 0.44533125, 0.7104    , 0.67352783,
       0.82602995]), 'asteroids': array([0.6157    , 0.68503105, 0.6522819 , 0.79764635, 0.66251344,
       0.84894466]), 'gradient': array([0.08284196, 0.36138487, 0.7570873 , 0.95605224, 0.68945456,
       0.77981143]), 'angle': array([0.30041387, 0.59052295, 0.55951895, 0.8027    , 0.66840271,
       0.81090022]), 'module': array([-0.5       ,  0.41605864,  0.20223549,  0.29938173,  0.50210331,
        0.72355985])})
    
    manyGens = ModuleChooserGenome({'ttc': array([0.12497811, 0.29066017, 0.44589653, 0.77616827, 0.67352783,
       0.82602995]), 'asteroids': array([0.4657    , 0.75      , 0.65192167, 0.84088262, 0.66251344,
       0.84894466]), 'gradient': array([0.17657653, 0.44183181, 0.6984    , 0.86448833, 0.68945456,
       0.77981143]), 'angle': array([0.2216    , 0.57523432, 0.6135    , 0.89345913, 0.66840271,
       0.81090022]), 'module': array([-0.5       ,  0.4184773 ,  0.17900349,  0.27465312,  0.50210331,
        0.72355985])}) # Long time sims
    testGenome = ModuleChooserGenome({'ttc': array([0.18261168, 0.31840807, 0.46114062, 0.72248329, 0.67352783,
       0.82602995]), 'asteroids': array([0.57761201, 0.67647329, 0.8609    , 0.8609    , 0.66251344,
       0.84894466]), 'gradient': array([0.12878155, 0.29604244, 0.65784365, 0.7381    , 0.68945456,
       0.77981143]), 'angle': array([0.3564    , 0.5953838 , 0.57394869, 0.7232    , 0.66840271,
       0.81090022]), 'module': array([-0.5       ,  0.34494047,  0.1569    ,  0.32420313,  0.50210331,
        0.72355985])}) # Also good
    gen37 = ModuleChooserGenome({'ttc': array([0.0691    , 0.48608573, 0.834     , 0.861425  , 0.67352783,
       0.82602995]), 'asteroids': array([0.45201767, 0.57718261, 0.41196672, 0.82660603, 0.66251344,
       0.84894466]), 'gradient': array([0.30783535, 0.42333012, 0.6866    , 0.9552    , 0.68945456,
       0.77981143]), 'angle': array([0.48247954, 0.6196013 , 0.46076399, 0.74262134, 0.66840271,
       0.81090022]), 'module': array([-0.5       ,  0.19998793,  0.2102011 ,  0.40349321,  0.50210331,
        0.72355985])})
    
    longTimer =  ModuleChooserGenome({'ttc': array([0.10131874, 0.28686053, 0.43133281, 0.8026738 , 0.67352783,
       0.82602995]), 'asteroids': array([0.6029    , 0.6029    , 0.63043446, 0.89608933, 0.66251344,
       0.84894466]), 'gradient': array([0.17551267, 0.44187525, 0.68072179, 0.6826    , 0.68945456,
       0.77981143]), 'angle': array([0.3189    , 0.59595418, 0.59873438, 0.90813721, 0.66840271,
       0.81090022]), 'module': array([-0.5       ,  0.4938    ,  0.1906527 ,  0.28448714,  0.50210331,
        0.72355985])})
    
    longTimer2 =  ModuleChooserGenome({'ttc': array([0.10595965, 0.41978028, 0.4606    , 0.79505296, 0.67352783,
       0.82602995]), 'asteroids': array([0.55856083, 0.66143989, 0.5305    , 0.7585    , 0.66251344,
       0.84894466]), 'gradient': array([0.0866219 , 0.43411377, 0.69454835, 1.        , 0.68945456,
       0.77981143]), 'angle': array([0.25372084, 0.5209    , 0.63821822, 0.89916521, 0.66840271,
       0.81090022]), 'module': array([-0.35320168,  0.31573283,  0.12022905,  0.31728476,  0.50210331,
        0.72355985])})
    
    longTimer3 =  ModuleChooserGenome({'ttc': array([0.23794045, 0.30597818, 0.41852173, 0.75507158, 0.67352783,
       0.82602995]), 'asteroids': array([0.62849528, 0.67865914, 0.66277899, 0.9067    , 0.66251344,
       0.84894466]), 'gradient': array([0.18781198, 0.5482    , 0.56692424, 0.93956053, 0.68945456,
       0.77981143]), 'angle': array([0.27883638, 0.62428344, 0.64141267, 0.89841849, 0.66840271,
       0.81090022]), 'module': array([-0.4327458 ,  0.29818289,  0.14384377,  0.20035292,  0.50210331,
        0.72355985])})
    
    longTimer4 =  ModuleChooserGenome({'ttc': array([0.3013767 , 0.55877617, 0.2835267 , 0.79796508, 0.67352783,
       0.82602995]), 'asteroids': array([0.2986    , 0.66161284, 0.77812247, 0.9783    , 0.66251344,
       0.84894466]), 'gradient': array([0.12925   , 0.4293    , 0.50563598, 0.86027718, 0.68945456,
       0.77981143]), 'angle': array([0.4073    , 0.53079812, 0.55220564, 0.8973087 , 0.66840271,
       0.81090022]), 'module': array([-0.34383572,  0.29476978,  0.08881271,  0.45215941,  0.50210331,
        0.72355985])})
    
    longTimer5 =  ModuleChooserGenome({'ttc': array([0.1843224 , 0.42217831, 0.22657351, 0.9184    , 0.67352783,
       0.82602995]), 'asteroids': array([0.37546354, 0.64024881, 0.76806196, 0.88715867, 0.66251344,
       0.84894466]), 'gradient': array([0.23750844, 0.48931641, 0.45011274, 0.9839    , 0.68945456,
       0.77981143]), 'angle': array([0.47441881, 0.63025567, 0.6565    , 0.81574085, 0.66840271,
       0.81090022]), 'module': array([-0.42604452,  0.5       ,  0.211     ,  0.36361161,  0.50210331,
        0.72355985])})
    
    longTimer6 =  ModuleChooserGenome({'ttc': array([0.0455    , 0.53823353, 0.25320726, 0.81558084, 0.67352783,
       0.82602995]), 'asteroids': array([0.28236097, 0.61551324, 0.76932109, 0.9873    , 0.66251344,
       0.84894466]), 'gradient': array([0.2399592 , 0.35415632, 0.36      , 0.9403638 , 0.68945456,
       0.77981143]), 'angle': array([0.31939138, 0.75      , 0.47172796, 0.8423    , 0.66840271,
       0.81090022]), 'module': array([-0.480975  ,  0.41601464,  0.2246726 ,  0.4144714 ,  0.50210331,
        0.72355985])})
    # All above this point utilizes shooting(-0.5, 0.2) evade(0.25, 0.4), simulation (0.45, 1)

    longTimer7 =  ModuleChooserGenome({'ttc': array([0.45619   , 0.50878333, 0.50148659, 0.66947627, 0.48331298,
       0.78338649]), 'asteroids': array([0.5351    , 0.54088633, 0.36140763, 0.7699427 , 0.6609898 ,
       0.9413142 ]), 'gradient': array([0.42432287, 0.63559756, 0.24847583, 0.77415   , 0.51652832,
       0.69846871]), 'angle': array([0.5837448 , 0.6892773 , 0.67948833, 0.92327782, 0.50910016,
       0.82097057]), 'module': array([-0.34949925,  0.34633845,  0.34000154,  0.52214395,  0.46316385,
        0.53784734])})
    
    longTimer8 =  ModuleChooserGenome({'ttc': array([0.40498665, 0.4492    , 0.41387628, 0.8975    , 0.36837711,
       0.74752099]), 'asteroids': array([0.33909447, 0.6634    , 0.5767557 , 0.75492657, 0.74038395,
       0.89105881]), 'gradient': array([0.28553352, 0.48462206, 0.43285147, 0.90087252, 0.51794813,
       0.76322296]), 'angle': array([0.3111625 , 0.49504699, 0.37490806, 0.9774    , 0.61536566,
       0.80294835]), 'module': array([-0.31615504,  0.025     ,  0.71871352,  0.75      ,  0.6896562 ,
        0.83824746])})
    
    edvin = ModuleChooserGenome({'ttc': array([0.37048926, 0.53296139, 0.31137941, 0.52869946, 0.82439451,
       0.90759315]), 'asteroids': array([0.06524608, 0.30151332, 0.76548504, 0.86074091, 0.70630803,
       0.8384958 ]), 'gradient': array([0.24989317, 0.68762961, 0.26661781, 0.43082113, 0.46491921,
       0.90226073]), 'angle': array([0.6480605 , 0.70128628, 0.4726123 , 0.71785482, 0.55354698,
       0.88864118]), 'module': array([-0.32774137,  0.16088961,  0.40917913,  0.50605546,  0.64204865,
        0.65722902])})
    
    edvin2 = ModuleChooserGenome({'ttc': array([0.2780008 , 0.30530722, 0.72654006, 0.9152015 , 0.99165878,
       0.99896013]), 'asteroids': array([0.61499948, 0.69218843, 0.44387571, 0.54028778, 0.76659382,
       0.9879912 ]), 'gradient': array([0.56220638, 0.70391367, 0.75514747, 0.86346281, 0.39890677,
       0.92311466]), 'angle': array([0.23139734, 0.67845055, 0.1169263 , 0.93613973, 0.54934195,
       0.6640768 ]), 'module': array([-0.42650007,  0.30911735,  0.31494657,  0.54681984,  0.48434913,
        0.6335976 ])})
    
    edvin2 = ModuleChooserGenome({'ttc': array([0.24483448, 0.50140978, 0.60027735, 0.80696239, 0.51136642,
       0.70271648]), 'asteroids': array([0.32322761, 0.46973179, 0.57706161, 0.83272463, 0.51454017,
       0.73335857]), 'gradient': array([0.08842221, 0.40638678, 0.5949    , 0.94143201, 0.62865478,
       0.69699925]), 'angle': array([0.2944435 , 0.55200895, 0.38509834, 0.5122    , 0.54425025,
       0.7592214 ]), 'module': array([-0.5       ,  0.2692929 ,  0.5598    ,  0.55981791,  0.69222928,
        0.93380065])})
    
    noWeights = ModuleChooserGenome({'ttc': array([0.28901945, 0.55620476, 0.6589    , 1.        , 0.52511135,
       0.71183694]), 'asteroids': array([0.38529605, 0.43983664, 0.4597    , 0.57738335, 0.51649685,
       0.73035575]), 'gradient': array([0.40004476, 0.70278556, 0.798957  , 0.8238    , 0.6353702 ,
       0.70769211]), 'angle': array([0.42102117, 0.50403622, 0.5303    , 0.5303    , 0.556045  ,
       0.76441921]), 'module': array([-0.4475    ,  0.15530921,  0.36449053,  0.6681625 ,  0.69625131,
        0.93001783])})
    
    noWeights2 = ModuleChooserGenome({'ttc': array([0.37016513, 0.5359631 , 0.2832    , 0.92596094, 0.52511048,
       0.71183597]), 'asteroids': array([0.47995473, 0.49640267, 0.41433254, 0.58893899, 0.51649795,
       0.73035409]), 'gradient': array([0.38112418, 0.6993125 , 0.91385781, 1.        , 0.6353716 ,
       0.7076935 ]), 'angle': array([0.4019    , 0.4019236 , 0.43800041, 0.5447177 , 0.55604885,
       0.76442329]), 'module': array([-0.33099872,  0.37      ,  0.39877184,  0.68774687,  0.69625169,
        0.93001872])})
    
    noWeights3 = ModuleChooserGenome({'ttc': array([0.1099125 , 0.22753933, 0.73010143, 0.983     , 0.52511039,
       0.71183589]), 'asteroids': array([0.00932715, 0.3694716 , 0.57134543, 0.90921107, 0.51649809,
       0.73035395]), 'gradient': array([0.02799375, 0.22672586, 0.5299    , 0.5299    , 0.63537179,
       0.70769368]), 'angle': array([0.1219533 , 0.418425  , 0.8769613 , 0.95001475, 0.55604928,
       0.76442373]), 'module': array([-0.18790425,  0.03553591,  0.51266561,  0.5127    ,  0.69625183,
        0.93001884])})
    
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
    
    overnighter_manual = ModuleChooserGenome({'ttc': array([0.12981881, 0.49345425, 0.65391315, 0.90848213, 0.52511039,
       0.71183589]), 'asteroids': array([0, 0.59171103, 0.317     , 0.6646    , 0.51649809,
       0.73035395]), 'gradient': array([0.44545541, 0.6213318 , 0.26774878, 0.8758384 , 0.63537179,
       0.70769368]), 'angle': array([0.52500047, 0.73055   , 0.58543977, 0.9326641 , 0.55604928,
       0.76442373]), 'module': array([-0.3673    ,  0.3800073 ,  0.5773938 ,  0.64525   ,  0.69625183,
        0.93001884])})
    
    newRounds = ModuleChooserGenome({'ttc': array([0.08805   , 0.28254602, 0.72055789, 0.968631  , 0.52511039,
       0.71183589]), 'asteroids': array([0.2606    , 0.61039498, 0.3988    , 0.75292171, 0.51649809,
       0.73035395]), 'gradient': array([0.58460303, 0.6657    , 0.35242765, 0.71661974, 0.63537179,
       0.70769368]), 'angle': array([0.51444355, 0.75      , 0.5588517 , 0.8112    , 0.55604928,
       0.76442373]), 'module': array([-0.07066275,  0.267635  ,  0.58814857,  0.62259772,  0.69625183,
        0.93001884])})
    
    gen29 = ModuleChooserGenome({'ttc': array([0.20164909, 0.75      , 0.70171702, 0.84942884, 0.52511039,
       0.71183589]), 'asteroids': array([0.        , 0.4391    , 0.56679222, 0.86817032, 0.51649809,
       0.73035395]), 'gradient': array([0.42434045, 0.6386    , 0.27178445, 0.541925  , 0.63537179,
       0.70769368]), 'angle': array([0.59137407, 0.68218232, 0.56470047, 0.82534179, 0.55604928,
       0.76442373]), 'module': array([-0.25618976,  0.37292393,  0.47954814,  0.63411415,  0.69625183,
        0.93001884])})
    
    gen27 = ModuleChooserGenome({'ttc': array([0.20829605, 0.58785149, 0.8239857 , 0.95671743, 0.52511039,
       0.71183589]), 'asteroids': array([0.49563845, 0.68107118, 0.5244961 , 0.81342453, 0.51649809,
       0.73035395]), 'gradient': array([0.44630504, 0.58366115, 0.27018624, 0.39314906, 0.63537179,
       0.70769368]), 'angle': array([0.7058    , 0.70856173, 0.56307402, 0.79789702, 0.55604928,
       0.76442373]), 'module': array([-0.19895942,  0.2054189 ,  0.41690097,  0.4608    ,  0.69625183,
        0.93001884])})
    
    gen45 = ModuleChooserGenome({'ttc': array([0.4228    , 0.4228    , 0.62430161, 0.93558277, 0.52511039,
       0.71183589]), 'asteroids': array([0.30807172, 0.5556    , 0.41217562, 0.87878852, 0.51649809,
       0.73035395]), 'gradient': array([0.5955    , 0.67515462, 0.        , 0.8246482 , 0.63537179,
       0.70769368]), 'angle': array([0.39032638, 0.62686273, 0.33236875, 0.9341    , 0.55604928,
       0.76442373]), 'module': array([-0.33976619,  0.27209622,  0.4095    ,  0.52616588,  0.69625183,
        0.93001884])})
    
    gen44 = ModuleChooserGenome({'ttc': array([0.24552037, 0.50233749, 0.66922849, 0.89637603, 0.52511039,
       0.71183589]), 'asteroids': array([0, 0.5466    , 0.6081    , 0.82005997, 0.51649809,
       0.73035395]), 'gradient': array([0.35233283, 0.75      , 0.17753663, 0.76649435, 0.63537179,
       0.70769368]), 'angle': array([0.34747725, 0.3475    , 0.50242193, 0.81473012, 0.55604928,
       0.76442373]), 'module': array([-0.25910539,  0.22494467,  0.29554296,  0.4862281 ,  0.69625183,
        0.93001884])})
    
    global scenario
    scenario = get_randomized_scenario(70, 50, 0, time_limit=200)
    #scenario = set_scenario
    
    #scenario = crossing()
    scenario = traffic()
    #scenario = cluster()
    #scenario = cluster()
    runScenario(graphics = True, moduleChooserGenome = overnighter_manual)


if __name__ == '__main__':
    main()
