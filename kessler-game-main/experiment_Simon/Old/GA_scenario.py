# -*- coding: utf-8 -*-
# Copyright © 2022 Thales. All Rights Reserved.
# NOTICE: This file is subject to the license agreement defined in file 'LICENSE', which is part of
# this source code package.

#import time
import sys
import os
import numpy as np
from numpy import array
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.kesslergame import Scenario, KesslerGame, GraphicsType, TrainerEnvironment, kessler_game
from GA_controller import FuzzyController
from experiment_Simon.Old.genomeOld import Genome

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

set_scenario = Scenario(name='Test Scenario',
                            asteroid_states=[{'position': (-100, 200), 'angle': 90, 'speed': 100, 'size': 2},
                                             {'position': (-800, 400), 'angle': 90, 'speed': 250, 'size': 2},
                                             {'position': (-800, 50), 'angle': 0, 'speed': 180, 'size': 2},
                                             {'position': (50, 50), 'angle': 0, 'speed': 0, 'size': 2}],
                            ship_states=[
                                {'position': (400, 400), 'angle': np.random.randint(0, 360), 'lives': 3, 'team': 1, "mines_remaining": 3},
                                # {'position': (400, 600), 'angle': 90, 'lives': 3, 'team': 2, "mines_remaining": 3},
                            ],
                            map_size=(1000, 800),
                            time_limit=15,
                            ammo_limit_multiplier=0,
                            stop_if_no_ammo=False)

oneAst = Scenario(name='Test Scenario',
                            asteroid_states=[{'position': (-100, 200), 'angle': 90, 'speed': 250, 'size': 3}],
                            ship_states=[
                                {'position': (400, 400), 'angle': np.random.randint(0, 360), 'lives': 3, 'team': 1, "mines_remaining": 3},
                                # {'position': (400, 600), 'angle': 90, 'lives': 3, 'team': 2, "mines_remaining": 3},
                            ],
                            map_size=(1000, 800),
                            time_limit=20,
                            ammo_limit_multiplier=0,
                            stop_if_no_ammo=False)

dynamic_scenario = Scenario(name='Test Scenario',
                           num_asteroids = 3,
                            ship_states=[
                                {'position': (400, 400), 'angle': np.random.randint(0, 359), 'lives':10, 'team': 1, "mines_remaining": 3},
                                # {'position': (400, 600), 'angle': 90, 'lives': 3, 'team': 2, "mines_remaining": 3},
                            ],
                            map_size=(1000, 800),
                            time_limit=15,
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
                            time_limit=60,
                            ammo_limit_multiplier=0,
                            stop_if_no_ammo=False)


game_settings = {'graphics_type': None,
                 'realtime_multiplier': 0,
                 'frequency': 10}

graphics_game_settings = {'graphics_type': GraphicsType.Tkinter,
                 'realtime_multiplier': 1,
                 'frequency': 60}

score = 0
def runScenario(graphics: bool = False, angle: int = np.random.randint(0, 360), genome: Genome = None) -> kessler_game.Score:
    
    if graphics: 
        game = KesslerGame(settings=graphics_game_settings)  # Use this to visualize the game scenario
        score, perf_data = game.run(scenario=set_scenario, controllers=[FuzzyController(genome = genome)])
    else: 
        oneAst.ship_states[0]["angle"] = angle
        set_scenario.ship_states[0]["angle"] = angle
        game = TrainerEnvironment(settings=game_settings)  # Use this for max-speed, no-graphics simulation
        score, perf_data = game.run(scenario=set_scenario, controllers=[FuzzyController(genome = genome)])

    team_scores = [team.asteroids_hit for team in score.teams]
    hits = team_scores[0]
    accuracy = score.teams[0].accuracy
    print(f"Hits: {hits}, acc: {round(accuracy, 2)}")
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

    testGeneDict = {'desired_angle': array([-0.51244959, -0.12092446, -0.57247024,  0.57247024,  0.12092446,
        0.51244959]), 'angle': array([-0.8434    , -0.17904201, -0.08158081,  0.08158081,  0.17904201,
        0.8434    ]), 'angle_velocity': array([-0.58901088, -0.25      , -0.4911    , -0.49108516, -0.39092424,
        0.39092424,  0.49108516,  0.4911    ,  0.25      ,  0.58901088]), 'distance': array([0.1217    , 0.2504    , 0.20204011, 0.78806594, 0.81949106,
       0.92344017])}
    
    potential = {'desired_angle': array([-0.6236    , -0.18511064, -0.43029087,  0.43029087,  0.18511064,
        0.6236    ]), 'angle': array([-0.75008916,  0.        , -0.42883363,  0.42883363,  0.        ,
        0.75008916]), 'angle_velocity': array([-0.97965498, -0.38912892, -0.27573958, -0.0462    , -0.71596262,
        0.71596262,  0.0462    ,  0.27573958,  0.38912892,  0.97965498]), 'distance': array([0.43729643, 0.5       , 0.71996906, 0.76199207, 0.82076486,
       0.94856351])}
    
    PrettyGoodNEW = {'desired_angle': array([-0.41517652, -0.1647896 , -0.3808668 ,  0.3808668 ,  0.1647896 ,
        0.41517652]), 'angle': array([-0.77387575,  0.        , -0.2075517 ,  0.2075517 ,  0.        ,
        0.77387575]), 'angle_velocity': array([-0.6127875 , -0.5693    , -0.70573934, -0.3021    , -0.35692985,
        0.35692985,  0.3021    ,  0.70573934,  0.5693    ,  0.6127875 ]), 'distance': array([0.0018    , 0.23907085, 0.29310312, 0.5778    , 0.81949106,
       0.92344017])}
    
    alwaysLeads = {'desired_angle': array([-0.88541963, -0.3819    , -0.64521379,  0.64521379,  0.3819    ,
        0.88541963]), 'angle': array([-0.87935672,  0.        , -0.25368521,  0.25368521,  0.        ,
        0.87935672]), 'angle_velocity': array([-1.        , -0.66774124, -0.5464    , -0.22314616, -0.73913369,
        0.73913369,  0.22314616,  0.5464    ,  0.66774124,  1.        ]), 'distance': array([0.22151473, 0.27225079, 0.6664    , 0.88086468, 0.82076486,
       0.94856351])}

    genome = Genome(alwaysLeads)
    runScenario(genome=genome, graphics = True)

if __name__ == '__main__':
    main()
