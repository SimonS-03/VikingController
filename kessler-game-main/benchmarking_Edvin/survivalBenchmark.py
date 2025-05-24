# -*- coding: utf-8 -*-
# Copyright © 2022 Thales. All Rights Reserved.
# NOTICE: This file is subject to the license agreement defined in file 'LICENSE', which is part of
# this source code package.

# blir fuzzy bättre än hårdkodade gränser?
# byter fuzzy moduler mer sällan?

# är moduler sämre än en monolithic?
#import time
import sys
import os
import numpy as np
from scipy.stats import sem
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.kesslergame import Scenario, KesslerGame, GraphicsType, TrainerEnvironment, kessler_game

from neo_controller import NeoController
from exper_simulations.get_actions_using_simulations import GetActionsUsingSimulations
from benchmarking_Edvin.runOrShootControllerAlt import combinedControllerAlt  
from benchmarking_Edvin.runOrShootControllerHard import combinedControllerHard
from benchmarking_Edvin.EvasionModule import evasionController
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
                                {'position': (300, 400), 'angle': np.random.randint(0, 360), 'lives': 100, 'team': 1, "mines_remaining": 3},
                                {'position': (700, 400), 'angle': np.random.randint(0, 360), 'lives': 100, 'team': 1, "mines_remaining": 3},
                            ],
                            map_size=(1000, 800),
                            time_limit=100,
                            ammo_limit_multiplier=0,
                            stop_if_no_ammo=False)





# jag gjorde några för test
astSpeed2 = 70
trap_scenario = Scenario(name='Test Scenario',
                            asteroid_states=[{'position': (800, 400), 'angle': 180, 'speed': astSpeed2, 'size': 3},
                                             {'position': (500, 700), 'angle': 270, 'speed': astSpeed2, 'size': 3},
                                             {'position': (200, 400), 'angle': 0, 'speed': astSpeed2, 'size': 3},
                                             {'position': (500, 100), 'angle': 90, 'speed': astSpeed2, 'size': 3},
                                             {'position': (712, 612), 'angle': 225, 'speed': astSpeed2, 'size': 3},
                                             {'position': (288, 612), 'angle': 315, 'speed': astSpeed2, 'size': 3},
                                             {'position': (288, 188), 'angle': 45, 'speed': astSpeed2, 'size': 3},
                                             {'position': (712, 188), 'angle': 135, 'speed': astSpeed2, 'size': 3}],
                            ship_states=[
                                {'position': (500, 400), 'angle': 0, 'lives': 1, 'team': 1, "mines_remaining": 3},
                                # {'position': (400, 600), 'angle': 90, 'lives': 3, 'team': 2, "mines_remaining": 3},
                            ],
                            map_size=(1000, 800),
                            time_limit=100,
                            ammo_limit_multiplier=0,
                            stop_if_no_ammo=False)

def get_randomized_scenario(nbr_asteroids: int, lives: int = 1, mean_speed: float = 100, std_dev_speed: float = 50, time_limit: int = 30):
    
    def _get_randomized_position():
        """Returns a randomized position but allows a certain safe threshold at the ship position"""
        x = np.random.randint(0, 1000)
        y = np.random.randint(0, 800)
        while abs(x-500) < 50:
            x = np.random.randint(0, 1000)
        while abs(y-400) < 50:
            y = np.random.randint(0, 800)
        return (x, y)
    
    ast_states = [{'position': _get_randomized_position(), 'angle': np.random.rand()*360, 
                   'speed': np.random.normal(loc = mean_speed, scale = std_dev_speed), 'size': np.random.randint(1, 4)} for i in range(nbr_asteroids)]
    
    scenario = Scenario(name='benchmarking scenario',
                            asteroid_states=ast_states,
                            ship_states=[
                                {'position': (200, 400), 'angle': np.random.randint(0, 359), 'lives':lives, 'team': 1, "mines_remaining": 3}
                                # {'position': (500, 400), 'angle': np.random.randint(0, 359), 'lives':lives, 'team': 2, "mines_remaining": 3},
                                # {'position': (800, 400), 'angle': np.random.randint(0, 359), 'lives':lives, 'team': 3, "mines_remaining": 3}
                            ],
                            map_size=(1000, 800),
                            time_limit=time_limit,
                            ammo_limit_multiplier=0,
                            stop_if_no_ammo=False
                            )
    
    return scenario



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
            name='Crossing Scenario',
            asteroid_states=asteroid_states,
            ship_states=[
                # Team 1 (left side)
                {'position': (600, 400), 'angle': 0, 'lives': 1, 'team': 1, 'mines_remaining': 3}
                # Team 2 (right side)
                # {'position': (600, 400), 'angle': 0, 'lives': 100, 'team': 2, 'mines_remaining': 3},
                # {'position': (600, 200), 'angle': 0, 'lives': 100, 'team': 3, 'mines_remaining': 3}
            ],
            map_size=(1000, 800),
            time_limit=10,  # 2-minute survival/combat
            ammo_limit_multiplier=0,  # Infinite ammo (focus on navigation)
            stop_if_no_ammo=False
        )
    return scenario

def hybrid(nbr_asteroids: int, lives: int = 1, mean_speed: float = 100, std_dev_speed: float = 50, time_limit: int = 30):
    # gap_y = 400  # vertical gap at y = 400
    # for y in range(0, 800, 25):
    #     if not (gap_y - 100 < y < gap_y + 100):  # leave a gap 200 pixels wide
    #         asteroid_states.append({'position': (-100, y), 'angle': 180, 'speed': 130, 'size': 3})
    
    def _get_randomized_position():
        """Returns a randomized position but allows a certain safe threshold at the ship position"""
        x_min = 700
        x = np.random.randint(x_min, 1000)
        y = np.random.randint(0, 800)
        while abs(x-500) < 50:
            x = np.random.randint(x_min, 1000)
        while abs(y-400) < 50:
            y = np.random.randint(0, 800)
        return (x, y)
    
    # radnomly scattered asteroids
    ast_states = [{'position': _get_randomized_position(), 'angle': np.random.rand()*360, 
                   'speed': np.random.normal(loc = mean_speed, scale = std_dev_speed), 'size': np.random.randint(1, 4)} for i in range(nbr_asteroids)]

    # asteroid wall
    for y in range(0, 800, 50):
        # if not (gap_y - 100 < y < gap_y + 100):  # leave a gap 200 pixels wide
        ast_states.append({'position': (20, y), 'angle': 0, 'speed': 60, 'size': 3})

    scenario = Scenario(
            name='Hybrid scenario',
            asteroid_states=ast_states,
            ship_states=[
                # Team 1 (left side)
                {'position': (200, 600), 'angle': 0, 'lives': 100, 'team': 1, 'mines_remaining': 3},
                # Team 2 (right side)
                {'position': (200, 400), 'angle': 0, 'lives': 100, 'team': 2, 'mines_remaining': 3}
            ],
            map_size=(1000, 800),
            time_limit=120,  # 2-minute survival/combat
            ammo_limit_multiplier=0,  # Infinite ammo (focus on navigation)
            stop_if_no_ammo=False
        )
    return scenario

def traffic():
    asteroid_states = []
    for x in range(0, 1000, 100):
        for y in range(0, 800, 100):
            if x % 200 == 0:
                asteroid_states.append({'position': (x, y+50), 'angle': 0, 'speed': 80, 'size': 2})
            else:
                asteroid_states.append({'position': (x, y), 'angle': 0, 'speed': 80, 'size': 2})

    scenario = Scenario(
            name='Chaotic Asteroid Storm',
            asteroid_states=asteroid_states,
            ship_states=[
                # Team 1 (left side)
                {'position': (600, 400), 'angle': 0, 'lives': 1, 'team': 1, 'mines_remaining': 3}
                # Team 2 (right side)
                # {'position': (600, 200), 'angle': 0, 'lives': 100, 'team': 2, 'mines_remaining': 3}
            ],
            map_size=(1000, 800),
            time_limit=120,  # 2-minute survival/combat
            ammo_limit_multiplier=0,  # Infinite ammo (focus on navigation)
            stop_if_no_ammo=False
        )
    return scenario

def cluster():
    asteroid_states = []
    center_x, center_y = 500, 400
    for angle in range(0, 360, 5):
        asteroid_states.append({'position': (center_x + np.random.randint(-50, 50),
                                            center_y + np.random.randint(-50, 50)),
                                'angle': angle, 'speed': astSpeed, 'size': 2})
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
            time_limit=120,  # 2-minute survival/combat
            ammo_limit_multiplier=0,  # Infinite ammo (focus on navigation)
            stop_if_no_ammo=False
        )
    return scenario

def vortex():
    asteroid_states = []
    center = (500, 400)
    for i in range(30):
        angle = i * 360 / 30
        asteroid_states.append({
            'position': (center[0] + np.cos(np.deg2rad(angle)) * 0,
                        center[1] + np.sin(np.deg2rad(angle)) * 0),
            'angle': (angle + 90) % 360,  # moving tangentially
            'speed': 60,
            'size': 3,
        })
    scenario = Scenario(
            name='Vortex scenario',
            asteroid_states=asteroid_states,
            ship_states=[
                # Team 1 (left side)
                {'position': (600, 600), 'angle': 0, 'lives': 100, 'team': 1, 'mines_remaining': 3},
                # Team 2 (right side)
                {'position': (600, 200), 'angle': 0, 'lives': 100, 'team': 2, 'mines_remaining': 3},
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
def runBenchmark() -> kessler_game.Score:

    game = KesslerGame(settings=graphics_game_settings)  # Use this to visualize the game scenario
    # game = TrainerEnvironment(settings=game_settings)  # Use this to benchmark
    
    iterations = 2

    if False:
        fig = plt.figure()

        controllers = [combinedController(), GetActionsUsingSimulations(single_use=True), evasionController()]
        legend_labels = ["combined", "simulation", "evasion"]
        plot_styles = ["bo-", "ro-", "go-"]
        for i in range(len(controllers)):
            controller = controllers[i]
            times = []
            timeError = []
            asteroids = []

            print(f"\n Calculation")
            timeAvg = 0
            iterTimes = []
            for iter in range(iterations):
                if i == 1: controller = GetActionsUsingSimulations(single_use=True)
                if i == 0: controller = combinedController()
                if i == 2: controller = evasionController()
                score, perf_data = game.run(scenario=crossing(), controllers=[controller])
                timeAvg += score.sim_time
                iterTimes.append(score.sim_time)
                print(f"Iteration {iter+1}/{iterations} done")

            error = sem(iterTimes)
            timeError.append(error)
            timeAvg /= iterations
            
            times.append(round(timeAvg, 2)) 
            print(f"sim times for {legend_labels[i]}:{iterTimes}. Time average: {round(timeAvg, 2) } error: {error}")

    if False:
        fig = plt.figure()

        controllers = [combinedController(), GetActionsUsingSimulations(single_use=True), evasionController()]
        legend_labels = ["combined", "simulation", "evasion"]
        plot_styles = ["bo-", "ro-", "go-"]
        for i in range(len(controllers)):
            controller = controllers[i]
            times = []
            timeError = []
            asteroids = []

            for ast in range(10, 80, 10):
                

                print(f"\n Calculation for {ast} asteroids:\n")
                timeAvg = 0
                iterTimes = []
                for iter in range(iterations):
                    if i == 1: controller = GetActionsUsingSimulations(single_use=True)
                    if i == 0: controller = combinedController()
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
        # crossing, traffic, vortex, cluster, get_randomized_scenario
        score, perf_data = game.run(scenario=traffic(), controllers=[GetActionsUsingSimulations(single_use=True)])
        # score, perf_data = game.run(scenario=get_randomized_scenario(100, lives=1, mean_speed=40), controllers=[combinedControllerAlt()])

        # score, perf_data = game.run(scenario=get_randomized_scenario(70, lives=100, mean_speed=50), controllers=[NeoController()])
        # score, perf_data = game.run(scenario=traffic(nbr_asteroids=100, lives=100, mean_speed=40), controllers=[combinedControllerAlt(), combinedController()])
        # score, perf_data = game.run(scenario=traffic(), controllers=[NeoController()])
        # score, perf_data = game.run(scenario=get_randomized_scenario(130, lives=100, mean_speed=50), controllers=[combinedController(), GetActionsUsingSimulations(single_use=True), evasionController()])

    if True:
        # Print out some general info about the result
        # print('Scenario eval time: '+str(time.perf_counter()-pre)) 
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
