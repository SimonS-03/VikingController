# -*- coding: utf-8 -*-
# Copyright © 2022 Thales. All Rights Reserved.
# NOTICE: This file is subject to the license agreement defined in file 'LICENSE', which is part of
# this source code package.

#import time
import sys
import os
import numpy as np
from scipy.stats import sem
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.kesslergame import Scenario, KesslerGame, GraphicsType, TrainerEnvironment, kessler_game
from experiment_Simon.EvasionModuleBenchmark import evasionController

from experiment_Simon.runOrShootController import combinedController
from  matplotlib import pyplot as plt
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

def get_randomized_scenario(nbr_asteroids: int, lives: int = 1, mean_speed: float = 100, std_dev_speed: float = 50, time_limit: int = 30, angle = np.random.rand()*360):
    
    def _get_randomized_position():
        """Returns a randomized position but allows a certain safe threshold at the ship position"""
        x = np.random.randint(0, 1000)
        y = np.random.randint(0, 800)
        while abs(x-500) < 50:
            x = np.random.randint(0, 1000)
        while abs(y-400) < 50:
            y = np.random.randint(0, 800)
        return (x, y)
    
    ast_states = [{'position': _get_randomized_position(), 'angle': angle, 
                   'speed': np.random.normal(loc = mean_speed, scale = std_dev_speed), 'size': np.random.randint(1, 4)} for i in range(nbr_asteroids)]
    
    scenario = Scenario(name='benchmarking scenario',
                            asteroid_states=ast_states,
                            ship_states=[
                                {'position': (500, 400), 'angle': np.random.randint(0, 359), 'lives':lives, 'team': 1, "mines_remaining": 3}
                            ],
                            map_size=(1000, 800),
                            time_limit=time_limit,
                            ammo_limit_multiplier=0,
                            stop_if_no_ammo=False
                            )
    
    return scenario

game_settings = {'graphics_type': None,
                 'realtime_multiplier': 0,
                 'frequency': 10}


graphics_game_settings = {'graphics_type': GraphicsType.Tkinter,
                 'realtime_multiplier': 0,
                 'frequency':30}


score = 0
def runBenchmark() -> kessler_game.Score:

    game = KesslerGame(settings=graphics_game_settings)  # Use this to visualize the game scenario
    #game = TrainerEnvironment(settings=game_settings)  # Use this to benchmark
    
    iterations = 20

    if False:
        fig = plt.figure()

        controllers = [combinedController(), evasionController()]
        legend_labels = ["simulation", "gradient descent"]
        plot_styles = ["bo-", "ro-"]
        for i in range(len(controllers)):
            controller = controllers[i]
            times = []
            timeError = []
            asteroids = []

            for ast in range(10, 80, 2):
                print(f"\n Calculation for {ast} asteroids:\n")
                timeAvg = 0
                iterTimes = []
                for iter in range(iterations):
                    score, perf_data = game.run(scenario=get_randomized_scenario(ast), controllers=[controller])
                    timeAvg += score.sim_time
                    iterTimes.append(score.sim_time)
                    print(f"Iteration {iter+1}/{iterations} done")

                error = sem(iterTimes)
                timeError.append(error)
                timeAvg /= iterations
                
                times.append(round(timeAvg, 2))
                asteroids.append(ast)
            
            plt.errorbar(asteroids, times, fmt = plot_styles[i], yerr=timeError, label = legend_labels[i])
        
        plt.ylabel("time survived (s)")
        plt.xlabel("asteroid count")
        plt.legend()
        plt.show()

    if True:
        score, perf_data = game.run(scenario=get_randomized_scenario(1), controllers=[combinedController()])


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
    runBenchmark()


if __name__ == '__main__':
    main()
