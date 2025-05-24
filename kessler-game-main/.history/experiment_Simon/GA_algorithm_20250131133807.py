# -*- coding: utf-8 -*-
# Copyright © 2022 Thales. All Rights Reserved.
# NOTICE: This file is subject to the license agreement defined in file 'LICENSE', which is part of
# this source code package.

import sys
import os
import pickle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
import GA_scenario as Game

import numpy as np
import random

np.set_printoptions(legacy='1.25')

class GeneticAlgorithm:
    def __init__(self, pop_size, nbr_parents, generations, mutation_rate, mutation_amount, nbr_traits, start_angle: float = None, start_point: list[float] = None):
        """Include start point to start from previous genetic code"""
        self.start_angle = start_angle
        self.random_angle = True if self.start_angle == None else False
        self.pop_size = pop_size
        self.nbr_parents = nbr_parents
        self.generations = generations
        self.mutationProb = mutation_rate
        self.mutationAmount = mutation_amount
        self.linspaces = {"negative":np.linspace(-1.0, 0.0, 11),
                          "zero":np.linspace(-1.0, 1.0, 11),
                          "positive":np.linspace(0.0, 1.0, 11),
                          }
        self.nbr_traits = nbr_traits
        
        self.current_pop = None if (start_point == None) else start_point
        self.init_pop()

    def init_pop(self):
        self.current_pop = [] if self.current_pop == None else self.current_pop
        # Ind = [1, 2, 3, 4] intervals: [-1.0, 0.0], [-1.0, 1.0], [0.0, 1.0]
        for _ in range(self.pop_size-len(self.current_pop)):
            ind = self.nbr_traits*[0]
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
            gen = NewGeneration(self.current_pop, nbr_traits=6)
            gen.select_parents(self.start_angle)
            gen.crossover(arg = "mean")
            gen.mutate(self.mutationProb, self.mutationAmount)
            self.current_pop = gen.get_new_pop()
            print(f"Generation {_+1} complete \n")
            #print(self.current_pop)
            
            with open("saveData.pickle", "wb") as F:
                pickle.dump(self.current_pop, F)



class NewGeneration:
    def __init__(self, pop, nbr_traits):
        self.pop = pop 
        self.pop_size = len(self.pop)
        self.nbr_traits = nbr_traits
        self.parents = None
        self.parent_nbr = int(self.pop_size // 3)
        self.children = []
    
    def eval_fitness(self, angle: float = None):
        score = []
        
        if angle == None:
            angle = np.random.randint(-180, 180)
        print(f"Starting simulations, phi0 = {angle}...")
        for ind in self.pop:
            result = Game.runScenario(ind, angle = angle)
            score.append(result.teams[0].asteroids_hit)
        return score
    
    def select_parents(self, angle = None):
        score = self.eval_fitness(angle)
        parents = sorted(enumerate(score), key=lambda x: x[1])[-self.parent_nbr:]
        indices, values = zip(*parents)

        self.parents = [self.pop[idx] for idx in indices]
        print(f"Most effective were: {self.parents}")
    def crossover(self, arg: str = 'select'):
        # Combine parents
        # [[1, 2, 3, 4, 5, 6], [2, 2, 3, 3, 4, 5]]
        while len(self.children) < self.pop_size:
            parents = random.sample(self.parents, 2)
            child = []
            
            if arg == 'select':
                # Select entire genes from parents
                for i in range(self.nbr_traits):
                    trait = parents[random.randint(0, 1)][i]
                    child.append(trait)
            elif arg == 'mean':
                # Average the genes from both parents
                for i in range(self.nbr_traits):
                    trait = round(np.mean([parent[i] for parent in parents]), 4)
                    child.append(trait)
            else:
                print("Did not recognize arg")
            self.children.append(child)
    
    def mutate(self, mutationProb, mutationAmount):
        mutationProb = mutationProb
        mutationAmount = mutationAmount
        
        mut_count = 0
        for child in self.children:
            for i in range(len(child)):
                
                r = np.random.rand()
                if r < mutationProb:
                    #print("Mutated gene")
                    dr = (np.random.rand()*2 - 1) * mutationAmount
                    mut_count += 1
                    if i < 2:
                        child[i] = round(float(np.clip((child[i] + dr), -1, 0)), 4)
                    elif i >= 4:
                        child[i] = round(float(np.clip((child[i] + dr), 0, 1)), 4)
                    else:
                        child[i] = round(float(np.clip((child[i] + dr), -1, 1)), 4)
            # Sorts the genes in the wanted manner
            for i in range(int(len(child)//2)):
                if child[2*i] < child[2*i + 1]:
                    continue
                else:
                    temp = child[2*i]
                    child[2*i] = child[2*i + 1]
                    child[2*i + 1] = temp
        print("Mutated " + str(mut_count) + " genes")
                

    def get_new_pop(self):
        return self.children

def main():
    fresh_batch = False
    
    if fresh_batch:
        GA = GeneticAlgorithm(pop_size=10, nbr_parents=2, generations=1, mutation_rate=0.15, mutation_amount = 0.8, nbr_traits=6)
        GA.evolve()
    else:
        with open("saveData.pickle", "rb") as F:
            data = pickle.load(F)
        GA = GeneticAlgorithm(pop_size=10, nbr_parents=2, generations=10, mutation_rate=0.2, mutation_amount = 0.3, nbr_traits=6, start_point = data, start_angle = -90)
        GA.evolve()
    
    # Saving the AI model in pickle file
    with open("saveData.pickle", "wb") as F:
        pickle.dump(GA.current_pop, F)

    

main()
