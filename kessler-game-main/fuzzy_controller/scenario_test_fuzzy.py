# -*- coding: utf-8 -*-
# Copyright © 2022 Thales. All Rights Reserved.
# NOTICE: This file is subject to the license agreement defined in file 'LICENSE', which is part of
# this source code package.

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import time
import numpy as np
import pickle

from src.kesslergame import Scenario, KesslerGame, GraphicsType, TrainerEnvironment, kessler_game
from graphics_both import GraphicsBoth
from evasion_module import EvasionModule
from genome import Genome


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
                            asteroid_states=[{'position': (30, 700), 'angle': 0, 'speed': 40, 'size': 4}, 
                                             {'position': (10, 200), 'angle': 0, 'speed': 40, 'size': 4}, 
                                             {'position': (500, 50), 'angle': 0, 'speed': 50, 'size': 4}, 
                                             {'position': (70, 400), 'angle': 0, 'speed': 30, 'size': 4}, ],
                            ship_states=[
                                {'position': (40, 400), 'angle': 0, 'lives': 10, 'team': 1, "mines_remaining": 3},
                                # {'position': (400, 600), 'angle': 90, 'lives': 3, 'team': 2, "mines_remaining": 3},
                            ],
                            map_size=(1000, 800),
                            time_limit=15,
                            ammo_limit_multiplier=0,
                            stop_if_no_ammo=False)
set2_scenario = Scenario(name='Test Scenario',
                            num_asteroids=30,
                            #asteroid_states=[{'position': (200, 400), 'angle': 0, 'speed': 30, 'size': 4}],
                            ship_states=[
                                {'position': (400, 400), 'angle': 0, 'lives': 10, 'team': 1, "mines_remaining": 3},
                                # {'position': (400, 600), 'angle': 90, 'lives': 3, 'team': 2, "mines_remaining": 3},
                            ],
                            map_size=(1000, 800),
                            time_limit=15,
                            ammo_limit_multiplier=0,
                            stop_if_no_ammo=False)

# Define Game Settings
game_settings = {
                 'perf_tracker': True,  
                 'graphics_type': GraphicsType.Tkinter,
                 'realtime_multiplier': 1,
                 'graphics_obj': None,
                 'frequency': 30
                 }

def runScenario(genome_params: list[float] = None, graphics: bool = False, angle: int = np.random.randint(0, 360), genome: Genome = None) -> kessler_game.Score:
    
    if graphics: game = KesslerGame(settings=game_settings)  # Use this to visualize the game scenario
    else: game = TrainerEnvironment(settings=game_settings)  # Use this for max-speed, no-graphics simulation

    # Evaluate the game
    #pre = time.perf_counter()
    #set_scenario.ship_states[0]['angle'] = angle
    score, perf_data = game.run(scenario=set1_scenario, controllers=[EvasionModule(genome = genome)])

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
    with open("saveData.pickle", "rb") as F:
        data = pickle.load(F)
    runScenario(genome = data[0], graphics = True)

if __name__ == '__main__':
    main()

