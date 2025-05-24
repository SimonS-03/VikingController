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
from experiment_Simon.ShootingModule import shooterController
from AstChooserGenome import AsteroidChooserGenome
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
                            asteroid_states=[{'position': (-100, 200), 'angle': 90, 'speed': 50, 'size': 3}],
                            ship_states=[
                                {'position': (400, 400), 'angle': np.random.randint(0, 360), 'lives': 100, 'team': 1, "mines_remaining": 3},
                                # {'position': (400, 600), 'angle': 90, 'lives': 3, 'team': 2, "mines_remaining": 3},
                            ],
                            map_size=(1000, 800),
                            time_limit=20,
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


game_settings = {'graphics_type': None,
                 'realtime_multiplier': 0,
                 'frequency': 30}


graphics_game_settings = {'graphics_type': GraphicsType.Tkinter,
                 'realtime_multiplier': 1,
                 'frequency':30}


score = 0
def runScenario(astChooserGenome: AsteroidChooserGenome = AsteroidChooserGenome(), graphics: bool = False, angle: int = np.random.randint(0, 360)) -> kessler_game.Score:

    if graphics: 
        game = KesslerGame(settings=graphics_game_settings)  # Use this to visualize the game scenario
        score, perf_data = game.run(scenario=set_scenario_advanced, controllers=[shooterController(astChooserGenome, 30)])
    
    else:
        game = TrainerEnvironment(settings=game_settings)  # Use this to visualize the game scenario
        score, perf_data = game.run(scenario=set_scenario, controllers=[shooterController(astChooserGenome, 30)])
    
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

    benchmarkGenome = AsteroidChooserGenome({'angle': array([0.        , 0.30314477, 0.61976454, 0.6802    , 0.71382689,
       0.82463633]), 'distance': array([0.33292555, 0.49662009, 0.3915    , 0.7119256 , 0.74582965,
       0.85263465]), 'size': array([0.40834865, 0.47434244, 0.45831567, 1.        , 0.91528792,
       0.96818314]), 'relevance': array([0.2338    , 0.47638214, 0.7332616 , 0.97158281, 0.63510685,
       0.73748204])})
    currentTestGenome = AsteroidChooserGenome({'angle': array([0.        , 0.3209769 , 0.69716059, 0.79038239, 0.71382689,
       0.82463633]), 'distance': array([0.30435391, 0.48086151, 0.1867006 , 0.7127    , 0.74582965,
       0.85263465]), 'size': array([0.49415637, 0.5       , 0.2831    , 0.917775  , 0.91528792,
       0.96818314]), 'relevance': array([0.2971    , 0.48575565, 0.65372271, 0.8837    , 0.63510685,
       0.73748204])})
    
    currentTestGenome2 = AsteroidChooserGenome({'angle': array([0.        , 0.4175113 , 0.88391136, 0.981     , 0.71382689,
       0.82463633]), 'distance': array([0.2065091 , 0.40958359, 0.30563031, 0.5486    , 0.74582965,
       0.85263465]), 'size': array([0.3156    , 0.40150016, 0.37662921, 0.83950838, 0.91528792,
       0.96818314]), 'relevance': array([0.30876134, 0.40787312, 0.80826715, 0.98032665, 0.63510685,
       0.73748204])})
    
    currentTestGenome3 = AsteroidChooserGenome({'angle': array([0.        , 0.2437    , 0.91191449, 0.96757187, 0.71382689,
       0.82463633]), 'distance': array([0.04546799, 0.32872956, 0.03219026, 0.34876637, 0.74582965,
       0.85263465]), 'size': array([0.42968202, 0.4297    , 0.061     , 0.59007834, 0.91528792,
       0.96818314]), 'relevance': array([0.17408994, 0.1741    , 0.74071365, 0.8318    , 0.63510685,
       0.73748204])})
    
    currentTestGenome4 = AsteroidChooserGenome({'angle': array([0.        , 0.1967179 , 0.5188    , 0.98040258, 0.71382689,
       0.82463633]), 'distance': array([0.13775031, 0.21034436, 0.0528989 , 0.40345069, 0.74582965,
       0.85263465]), 'size': array([0.24706708, 0.4907    , 0.34471494, 0.57802446, 0.91528792,
       0.96818314]), 'relevance': array([0.0727728 , 0.31298437, 0.37412445, 0.84944636, 0.63510685,
       0.73748204])})
    
    
    trainedWithAdvanced200Gens = AsteroidChooserGenome({'angle': array([0.        , 0.38761215, 0.1107931 , 0.58357602, 0.69071515,
       0.88361165]), 'distance': array([0.15265988, 0.28503417, 0.95745695, 0.97783531, 0.83252896,
       0.91904276]), 'size': array([0.15262407, 0.44573077, 0.95392458, 0.97975342, 0.85713689,
       0.90948752]), 'relevance': array([0.26268984, 0.45705614, 0.46956284, 0.96877592, 0.65587678,
       0.93107172])})
    
    trainedWithAdvanced20Gens = AsteroidChooserGenome({'angle': array([0.        , 0.40860059, 0.58623407, 0.81390466, 0.69071515,
       0.88361165]), 'distance': array([0.15815974, 0.33731431, 0.80233183, 0.92825832, 0.83252896,
       0.91904276]), 'size': array([0.18748192, 0.48162204, 0.75128353, 0.81364943, 0.85713689,
       0.90948752]), 'relevance': array([0.3769    , 0.3769    , 0.1764    , 0.90365386, 0.65587678,
       0.93107172])})
    
    currentBestGenome= AsteroidChooserGenome({'angle': array([0.        , 0.4881    , 0.8768    , 0.9043    , 0.69071515,
       0.88361165]), 'distance': array([0.23686547, 0.43790554, 0.82016071, 0.97308002, 0.83252896,
       0.91904276]), 'size': array([0.19973127, 0.40186394, 0.50927517, 0.90090847, 0.85713689,
       0.90948752]), 'relevance': array([0.13305   , 0.44299503, 0.11144889, 0.52545833, 0.65587678,
       0.93107172])})

    runScenario(graphics = True, astChooserGenome = trainedWithAdvanced200Gens)


if __name__ == '__main__':
    main()
