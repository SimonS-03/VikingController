# -*- coding: utf-8 -*-
# Copyright © 2022 Thales. All Rights Reserved.
# NOTICE: This file is subject to the license agreement defined in file 'LICENSE', which is part of
# this source code package.

import sys
import cProfile
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
from src.kesslergame import Scenario, KesslerGame, TrainerEnvironment, GraphicsType
from get_actions_using_simulations import GetActionsUsingSimulations
from graphics_both import GraphicsBoth



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

set1_scenario = Scenario(name='Test Scenario',
                            # num_asteroids=50,
                            asteroid_states=[{'position': (200, 400), 'angle': 180, 'speed': 50, 'size': 4}], 
                                            # {'position': (700, 400), 'angle': 180, 'speed': 0, 'size': 4}],
                            #                  {'position': (550, 300), 'angle': 90, 'speed': 30, 'size': 4}, 
                            #                 {'position': (300, 400), 'angle': 0, 'speed': 0, 'size': 4}, 
                            #                 {'position': (400, 400), 'angle': 0, 'speed': 30, 'size': 4}, 
                            ship_states=[
                                {'position': (500, 400), 'angle': 0, 'lives': 300, 'team': 1, "mines_remaining": 3},
                                # {'position': (400, 600), 'angle': 90, 'lives': 3, 'team': 2, "mines_remaining": 3},
                            ],
                            map_size=(1000, 800),
                            time_limit=60,
                            ammo_limit_multiplier=0,
                            stop_if_no_ammo=False)  

set2_scenario = Scenario(name='Test Scenario',
                            asteroid_states=[{'position': (400, 700), 'angle': 230, 'speed': 340, 'size': 4}, 
                                             {'position': (10, 200), 'angle': 160, 'speed': 170, 'size': 4}, 
                                             {'position': (500, 50), 'angle': 40, 'speed': 250, 'size': 4}, 
                                             {'position': (70, 400), 'angle': 130, 'speed': 30, 'size': 4},
                                             {'position': (70, 400), 'angle': 40, 'speed': 230, 'size': 4},
                                             {'position': (70, 400), 'angle': 130, 'speed': 330, 'size': 4},
                                             {'position': (340, 250), 'angle': 30, 'speed': 490, 'size': 4},
                                             {'position': (160, 270), 'angle': 70, 'speed': 330, 'size': 4},
                                             {'position': (10, 420), 'angle': 140, 'speed': 230, 'size': 4},
                                             {'position': (370, 530), 'angle': 280, 'speed': 330, 'size': 4},
                                             {'position': (480, 720), 'angle': 90, 'speed': 130, 'size': 4},
                                             {'position': (830, 10), 'angle': 240, 'speed': 130, 'size': 4},
                                             {'position': (340, 90), 'angle': 70, 'speed': 230, 'size': 4},
                                             {'position': (230, 170), 'angle': 160, 'speed': 230, 'size': 4}],
                            ship_states=[
                                {'position': (500, 400), 'angle': 0, 'lives': 300, 'team': 1, "mines_remaining": 3}
                                # {'position': (400, 600), 'angle': 90, 'lives': 3, 'team': 2, "mines_remaining": 3},
                            ],
                            map_size=(1000, 800),
                            time_limit=60,
                            ammo_limit_multiplier=0,
                            stop_if_no_ammo=False)

# Define Game Settings
game_settings = {'perf_tracker': True,  
                 'graphics_type': GraphicsType.Tkinter,
                 'realtime_multiplier': 1,
                 'graphics_obj': None,
                 'frequency': 30}
plot_sims = False
if plot_sims:
    game = TrainerEnvironment(settings=game_settings)  # Use this for max-speed, no-graphics simulation
else:
    game = KesslerGame(settings=game_settings)  # Use this to visualize the game scenario

# Evaluate the game
pre = time.perf_counter()
if False:
    profiler = cProfile.Profile()
    profiler.enable()
    score, perf_data = game.run(scenario=set1_scenario, controllers=[GetActionsUsingSimulations(), GetActionsUsingSimulations()])
    profiler.disable()
    profiler.dump_stats("kessler_profile.prof")

else:
    score, perf_data = game.run(scenario=set1_scenario, controllers=[GetActionsUsingSimulations(), GetActionsUsingSimulations()])
    #score, perf_data = game.run(scenario=set1_scenario, controllers=[MCTSModule(), MCTSModule()])

# Print out some general info about the result
print('Scenario eval time: '+str(time.perf_counter()-pre))
print(score.stop_reason)
print('Asteroids hit: ' + str([team.asteroids_hit for team in score.teams]))
print('Deaths: ' + str([team.deaths for team in score.teams]))
print('Accuracy: ' + str([team.accuracy for team in score.teams]))
print('Mean eval time: ' + str([team.mean_eval_time for team in score.teams]))





