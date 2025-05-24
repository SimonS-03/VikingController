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
from experiment_Simon.EvasionModule import evasionController
from experiment_Simon.runOrShootController import combinedController
from heatmap import Heatmap
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
                                {'position': (200, 100), 'angle': np.random.randint(0, 360), 'lives': 100, 'team': 1, "mines_remaining": 3},
                                # {'position': (400, 600), 'angle': 90, 'lives': 3, 'team': 2, "mines_remaining": 3},
                            ],
                            map_size=(1000, 800),
                            time_limit=100,
                            ammo_limit_multiplier=0,
                            stop_if_no_ammo=False)

set_scenario_advanced = Scenario(name='Test Scenario',
                            asteroid_states=[{'position': (100, 200), 'angle': 90, 'speed': astSpeed, 'size': 3},
                                             {'position': (800, 400), 'angle': 46, 'speed': astSpeed*0.2, 'size': 3},
                                             {'position': (800, 50), 'angle': -140, 'speed': astSpeed*0.4, 'size': 1},
                                             {'position': (50, 50), 'angle': -20, 'speed': astSpeed*2, 'size': 3},
                                             {'position': (400, 50), 'angle': -89, 'speed': astSpeed*0.9, 'size': 2},
                                             {'position': (500, 700), 'angle': 37, 'speed': astSpeed*0.3, 'size': 2},
                                             {'position': (800, 750), 'angle': 140, 'speed': astSpeed*0.4, 'size': 3},
                                             {'position': (200, 560), 'angle': 45, 'speed': astSpeed*1.5, 'size': 2},
                                             {'position': (20, 290), 'angle': 19, 'speed': astSpeed*0.9, 'size': 1}],
                            ship_states=[
                                {'position': (0, 400), 'angle': np.random.randint(0, 360), 'lives': 100, 'team': 1, "mines_remaining": 3},
                                # {'position': (400, 600), 'angle': 90, 'lives': 3, 'team': 2, "mines_remaining": 3},
                            ],
                            map_size=(1000, 800),
                            time_limit=20,
                            ammo_limit_multiplier=0,
                            stop_if_no_ammo=False)
  
set_scenario_crazy = Scenario(name='Test Scenario',
                              num_asteroids=50,
                            # asteroid_states=[{'position': (100, 200), 'angle': 90, 'speed': astSpeed, 'size': 3},
                            #                  {'position': (800, 400), 'angle': 46, 'speed': astSpeed*0.2, 'size': 3},
                            #                  {'position': (800, 50), 'angle': -140, 'speed': astSpeed*0.4, 'size': 1},
                            #                  {'position': (50, 50), 'angle': -20, 'speed': astSpeed*2, 'size': 3},
                            #                  {'position': (400, 50), 'angle': -89, 'speed': astSpeed*0.9, 'size': 2},
                            #                  {'position': (500, 700), 'angle': 37, 'speed': astSpeed*0.3, 'size': 2},
                            #                  {'position': (800, 750), 'angle': 140, 'speed': astSpeed*0.4, 'size': 3},
                            #                  {'position': (200, 560), 'angle': 45, 'speed': astSpeed*1.5, 'size': 2},
                            #                  {'position': (20, 290), 'angle': 19, 'speed': astSpeed*0.9, 'size': 3},
                            #                  {'position': (800, 750), 'angle': 140, 'speed': astSpeed*0.4, 'size': 3},
                            #                  {'position': (200, 560), 'angle': 45, 'speed': astSpeed*2, 'size': 2},
                            #                  {'position': (400, 750), 'angle': 20, 'speed': astSpeed*0.8, 'size': 3},
                            #                  {'position': (200, 560), 'angle': 45, 'speed': astSpeed*1.5, 'size': 2},
                            #                  {'position': (80, 50), 'angle': -10, 'speed': astSpeed*0.4, 'size': 3},
                            #                  {'position': (50, 50), 'angle': -129, 'speed': astSpeed*2, 'size': 3},
                            #                  {'position': (400, 20), 'angle': -80, 'speed': astSpeed*1.4, 'size': 3},
                            #                  {'position': (150, 250), 'angle': -90, 'speed': astSpeed*2, 'size': 3}],
                            ship_states=[
                                {'position': (300, 400), 'angle': np.random.randint(0, 360), 'lives': 100, 'team': 1, "mines_remaining": 3}
                                #{'position': (800, 300), 'angle': np.random.randint(0, 360), 'lives': 100, 'team': 1, "mines_remaining": 3}
                            ])
oneAst = Scenario(name='Test Scenario',
                            asteroid_states=[{'position': (100, 0), 'angle': 90, 'speed': 300, 'size': 3}],
                            ship_states=[
                                {'position': (500, 400), 'angle': np.random.randint(0, 360), 'lives': 100, 'team': 1, "mines_remaining": 3},
                                # {'position': (400, 600), 'angle': 90, 'lives': 3, 'team': 2, "mines_remaining": 3},
                            ],
                            map_size=(1000, 800),
                            time_limit=20,
                            ammo_limit_multiplier=0,
                            stop_if_no_ammo=False)

dynamic_scenario = Scenario(name='Test Scenario',
                           num_asteroids = 30,
                            ship_states=[
                                {'position': (500, 400), 'angle': np.random.randint(0, 359), 'lives':100, 'team': 1, "mines_remaining": 3}
                                #{'position': (400, 600), 'angle': 90, 'lives': 100, 'team': 2, "mines_remaining": 3},
                            ],
                            map_size=(1000, 800),
                            time_limit=80,
                            ammo_limit_multiplier=0,
                            stop_if_no_ammo=False
                            )
# Define Game Settings

dynamic_graphic_scenario = Scenario(name='Test Scenario',
                           num_asteroids = 8,
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
                 'realtime_multiplier': 0,
                 'frequency':30}


score = 0
def runScenario(graphics: bool = False, angle: int = np.random.randint(0, 360)) -> kessler_game.Score:

    if graphics: 
        game = KesslerGame(settings=graphics_game_settings)  # Use this to visualize the game scenario
        score, perf_data = game.run(scenario=set_scenario_crazy, controllers=[combinedController()])
    
    else:
        game = TrainerEnvironment(settings=game_settings)  # Use this to visualize the game scenario
        score, perf_data = game.run(scenario=set_scenario, controllers=[evasionController()])
    
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

    runScenario(graphics = True)


if __name__ == '__main__':
    main()
