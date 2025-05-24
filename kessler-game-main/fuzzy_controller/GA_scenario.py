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
                            num_asteroids = 30,
                            ship_states=[
                                {'position': (200, 400), 'angle': 0, 'lives': 3, 'team': 1},
                                #{'position': (400, 400), 'angle': np.random.randint(0, 359), 'team': 1, "mines_remaining": 3},
                                # {'position': (400, 600), 'angle': 90, 'lives': 3, 'team': 2, "mines_remaining": 3},
                            ],
                            map_size=(1000, 800),
                            time_limit=15,
                            ammo_limit_multiplier=0,
                            stop_if_no_ammo=False)
# Define Game Settings

dynamic_graphic_scenario = Scenario(name='Test Scenario',
                           num_asteroids = 30,
                            ship_states=[
                                {'position': (400, 400), 'angle': np.random.randint(0, 359), 'lives':3, 'team': 1},
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
        score, perf_data = game.run(scenario=dynamic_graphic_scenario, controllers=[EvasionModule(genome = genome)])
    else: 
        game = TrainerEnvironment(settings=game_settings)  # Use this for max-speed, no-graphics simulation
        score, perf_data = game.run(scenario=dynamic_scenario, controllers=[EvasionModule(genome = genome)])

    lives = score.teams[0].lives_remaining
    print(f"Lives remaining: {lives}")
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
    
    handPickedGeneDict = {'desired_speed': array([-0.47735249, -0.15733097,  0.3003    ,  0.92948077,  0.56020473,
        0.72966194]), 'current_speed': array([-0.8517    , -0.1003    ,  0.4234    ,  0.5097345 ,  0.15757137,
        0.74021365]), 'relative_angle': array([-0.42574513, -0.09408824, -1.        ,  0.21406554,  0.38221635,
        0.56455094])}
    
    bestGeneDict = {'desired_angle': array([-0.83187842, -0.188443  ,  0.02246615,  0.3094    ,  0.40819134,
        0.84569428]), 'angle': array([-0.8585736 , -0.3773955 ,  0.2517    ,  0.62363418,  0.59478891,
        0.92938459]), 'angle_velocity': array([-0.8897    , -0.88968282, -0.37430249, -0.35265937, -0.1041    ,
        0.9599    ,  0.33405786,  0.3341    ,  0.78319544,  0.99401757])}
    genome = Genome(handPickedGeneDict)
    runScenario(genome=genome, graphics = True)

if __name__ == '__main__':
    main()
