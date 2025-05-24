# -*- coding: utf-8 -*-
# Copyright © 2022 Thales. All Rights Reserved.
# NOTICE: This file is subject to the license agreement defined in file 'LICENSE', which is part of
# this source code package.

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
from src.kesslergame import Scenario, KesslerGame, TrainerEnvironment, GraphicsType
from test_controller5 import FuzzyController
from graphics_both import GraphicsBoth

import numpy as np
import random


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
class Game:
    def __init__(self, GA_values):
        self.scenario = Scenario(name='Test Scenario',
                            asteroid_states=[{'position': (200, 400), 'angle': 0, 'speed': 0, 'size': 4}],
                            ship_states=[
                                {'position': (400, 400), 'angle': 90, 'lives': 3, 'team': 1, "mines_remaining": 3},
                                # {'position': (400, 600), 'angle': 90, 'lives': 3, 'team': 2, "mines_remaining": 3},
                            ],
                            map_size=(1000, 800),
                            time_limit=60,
                            ammo_limit_multiplier=0,
                            stop_if_no_ammo=False)
        self.settings = {'perf_tracker': True,
                 'graphics_type': GraphicsType.Tkinter,
                 'realtime_multiplier': 1,
                 'graphics_obj': None,
                 'frequency': 60}
        #self.environment = KesslerGame(settings=self.settings)  # Use this to visualize the game scenario
        self.environment = TrainerEnvironment(settings=self.settings)  # Use this for max-speed, no-graphics simulation

        # Evaluate the game
        self.pre = time.perf_counter()
        self.score, self.perf_data = self.environment.run(scenario=self.scenario, controllers=[FuzzyController(GA_values), FuzzyController(GA_values)])
    def get_asteroids_hit(self):
        return [team.asteroids_hit for team in self.score.teams][0]

    def print_info(self):      
        # Print out some general info about the result
        print('Scenario eval time: '+str(time.perf_counter()-self.pre))
        print(self.score.stop_reason)
        print('Asteroids hit: ' + str([team.asteroids_hit for team in self.score.teams]))
        print('Deaths: ' + str([team.deaths for team in self.score.teams]))
        print('Accuracy: ' + str([team.accuracy for team in self.score.teams]))
        print('Mean eval time: ' + str([team.mean_eval_time for team in self.score.teams]))

class GeneticAlgorithm:
    def __init__(self, pop_size, nbr_parents, generations, mutation_rate, nbr_traits):
        self.pop_size = pop_size
        self.nbr_parents = nbr_parents
        self.generations = generations
        self.mutationRate = mutation_rate
        self.linspaces = {"negative":np.linspace(-1.0, 0.0, 11),
                          "zero":np.linspace(-1.0, 1.0, 11),
                          "positive":np.linspace(0.0, 1.0, 11),
                          }
        self.nbr_traits = nbr_traits
        
        self.current_pop = None
        self.init_pop()

    def init_pop(self):
        self.current_pop = []
        # Ind = [1, 2, 3, 4] intervals: [-1.0, 0.0], [-1.0, 1.0], [0.0, 1.0]
        for _ in range(self.pop_size):
            ind = 6*[0]
            n0, n1= random.sample(list(self.linspaces["negative"]), 2)
            n2, n3= random.sample(list(self.linspaces["zero"]), 2)
            n4, n5= random.sample(list(self.linspaces["positive"]), 2)
            ind[0], ind[1] = min(n0, n1), max(n0, n1)
            ind[2], ind[3] = min(n2, n3), max(n2, n3)
            ind[4], ind[5] = min(n4, n5), max(n4, n5)
            ind = [round(float(val), 1) for val in ind]

            self.current_pop.append(ind)
    
    def evolve(self):
        for _ in range(self.generations):
            gen = NewGeneration(self.current_pop, self.linspaces, nbr_traits=6)
            print(self.current_pop)
            gen.eval_fitness()
            gen.select_parents()
            gen.crossover()
            #gen.mutate()
            self.current_pop = gen.get_new_pop()
            print(self.current_pop)


class NewGeneration:
    def __init__(self, pop, linspaces, nbr_traits):
        self.pop = pop 
        self.pop_size = len(self.pop)
        self.linspaces = linspaces
        self.nbr_traits = nbr_traits
        self.parents = None
        self.children = []
    
    def eval_fitness(self):
        score = []
        for ind in self.pop:
            game = Game(ind)
            score.append(game.get_asteroids_hit())
    
    def select_parents(self):
        score = self.eval_fitness()
        parents = sorted(enumerate(score), key=lambda x: x[1])[-self.parents:]
        indices, values = zip(*parents)
        print(indices)
        self.parents = [self.pop[idx] for idx in indices]
    
    def crossover(self):
        # Combine parents
        # [[1, 2, 3, 4, 5, 6], [2, 2, 3, 3, 4, 5]]
        while len(self.children) < self.pop_size:
            parents = random.sample(self.parents, 2)
            for i in range(len(self.nbr_traits)):
                trait = parents[random.randint(0, 1)][i]
                self.children.append(trait)

    def mutate(self):
        for i in range(len(self.children)):
            # Randomly add or subtract 0.1 from one trait
            mutate_idx = random.randint(0, 5)
            delta = random.choice([-0.1, 0.1])
            if mutate_idx % 2 == 0:
                self.children[i][mutate_idx], self.children[i][mutate_idx+1] = min(self.children[i][mutate_idx+delta]), max(self.children[i][mutate_idx])
            else:
                self.children[i][mutate_idx-1], self.children[i][mutate_idx] = min(self.children[i][mutate_idx+delta]), max(self.children[i][mutate_idx])

    def get_new_pop(self):
        return self.children

def main():
    GA = GeneticAlgorithm(pop_size=4, nbr_parents=2, generations=1, mutation_rate=None, nbr_traits=6)
    GA.evolve()
    print

main()