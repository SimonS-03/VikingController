# -*- coding: utf-8 -*-
# Copyright © 2022 Thales. All Rights Reserved.
# NOTICE: This file is subject to the license agreement defined in file 'LICENSE', which is part of
# this source code package.

#import time
import sys
import os
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", 'kessler-game-main')))

from numpy import array
from src.kesslergame import Scenario, KesslerGame, GraphicsType, TrainerEnvironment, kessler_game
from moduleChooserGenome import ModuleChooserGenome
from runOrShootControllerEXPLANATIONS import combinedController


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
            time_limit=30,  # 2-minute survival/combat
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

def traffic():
    asteroid_states = []
    for x in range(0, 1000, 100):
        for y in range(0, 800, 100):
            if x%2 == 0: asteroid_states.append({'position': (x, y+50), 'angle': 0, 'speed': 100, 'size': 2})
            else:
                asteroid_states.append({'position': (x, y), 'angle': 0, 'speed': 100, 'size': 2})

    scenario = Scenario(
            name='Chaotic Asteroid Storm',
            asteroid_states=asteroid_states,
            ship_states=[
                # Team 1 (left side)
                {'position': (600, 550), 'angle': 0, 'lives': 100, 'team': 1, 'mines_remaining': 3}
                # Team 2 (right side)
                #{'position': (600, 200), 'angle': 0, 'lives': 100, 'team': 2, 'mines_remaining': 3},
            ],
            map_size=(1000, 800),
            time_limit=10,  # 2-minute survival/combat
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
        score, perf_data = game.run(scenario=scenario, controllers=[combinedController()])
    
    else:
        game = TrainerEnvironment(settings=game_settings)  # Use this to visualize the game scenario
        score, perf_data = game.run(scenario=scenario, controllers=[combinedController()])
    
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


def get_randomized_scenario(nbr_asteroids: int, lives: int = 1, mean_speed: float = 100, std_dev_speed: float = 50, time_limit: int = 30, angle: float = np.random.rand()*360):
    
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
                                {'position': (500, 400), 'angle': angle, 'lives':lives, 'team': 1, "mines_remaining": 3}
                            ],
                            map_size=(1000, 800),
                            time_limit=time_limit,
                            ammo_limit_multiplier=0,
                            stop_if_no_ammo=False
                            )
    
    return scenario


def main():
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
    scenario = get_randomized_scenario(50, 100, 50, time_limit=100)
    #scenario = crossing()
    # scenario = traffic()
    # scenario = vortex()
    #scenario = set_scenario
    runScenario(graphics = True, moduleChooserGenome = gen29)


if __name__ == '__main__':
    main()
