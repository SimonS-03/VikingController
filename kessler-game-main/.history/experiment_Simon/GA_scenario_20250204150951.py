# -*- coding: utf-8 -*-
# Copyright © 2022 Thales. All Rights Reserved.
# NOTICE: This file is subject to the license agreement defined in file 'LICENSE', which is part of
# this source code package.

import time
import sys
import os
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.kesslergame import Scenario, KesslerGame, GraphicsType, TrainerEnvironment, kessler_game
from GA_controller import FuzzyController
from graphics_both import GraphicsBoth
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

set_scenario = Scenario(name='Test Scenario',
                            asteroid_states=[{'position': (-100, 200), 'angle': 90, 'speed': 200, 'size': 3}],
                            ship_states=[
                                {'position': (400, 400), 'angle': np.random.randint(0, 360), 'lives': 3, 'team': 1, "mines_remaining": 3},
                                # {'position': (400, 600), 'angle': 90, 'lives': 3, 'team': 2, "mines_remaining": 3},
                            ],
                            map_size=(1000, 800),
                            time_limit=5,
                            ammo_limit_multiplier=0,
                            stop_if_no_ammo=False)

dynamic_scenario = Scenario(name='Test Scenario',
                           num_asteroids = 10,
                            ship_states=[
                                {'position': (400, 400), 'angle': np.random.randint(0, 360), 'lives': 3, 'team': 1, "mines_remaining": 3},
                                # {'position': (400, 600), 'angle': 90, 'lives': 3, 'team': 2, "mines_remaining": 3},
                            ],
                            map_size=(1000, 800),
                            time_limit=20,
                            ammo_limit_multiplier=0,
                            stop_if_no_ammo=False)
# Define Game Settings
game_settings = {'perf_tracker': True,
                 'graphics_type': GraphicsType.Tkinter,
                 'realtime_multiplier': 1,
                 'graphics_obj': None,
                 'prints_on': False,
                 'frequency': 60}


score = 0
def runScenario(genetic_params: list[float] = None, graphics: bool = False, angle: int = np.random.randint(0, 360), genome: Genome = None) -> kessler_game.Score:
    
    if graphics: game = KesslerGame(settings=game_settings)  # Use this to visualize the game scenario
    else: game = TrainerEnvironment(settings=game_settings)  # Use this for max-speed, no-graphics simulation

    # Evaluate the game
    pre = time.perf_counter()
    set_scenario.ship_states[0]['angle'] = angle
    score, perf_data = game.run(scenario=dynamic_scenario, controllers=[FuzzyController(genome), FuzzyController(genome)])

    team_scores = [team.asteroids_hit for team in score.teams]
    score0 = team_scores[0]
    print(score0)
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
    best = [np.float64(-1.0), np.float64(-0.16249999999999998), np.float64(0.0), np.float64(0.0), np.float64(0.15), np.float64(0.9187500000000001)]
    testGenes = [-0.9208, 0, -0, 0, 0, 0.6251]
    runScenario(testGenes, graphics = True, angle = -90)

if __name__ == '__main__':
    main()
