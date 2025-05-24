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
import warnings

import numpy as np
import random
from genome import Genome
from gene_editor import GeneEditor

np.set_printoptions(legacy='1.25')

class GeneticAlgorithm:
    def __init__(self, pop_size, nbr_parents, generations, mutation_rate, mutation_amount, start_angle: float = None, start_point: list[float] = None):
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
        self.current_pop: list[Genome] = None if start_point is None else start_point
        self.init_pop()

    def init_pop(self):
        if self.current_pop is None:
            self.current_pop = [] 
            for _ in range(self.pop_size-len(self.current_pop)):
                self.current_pop.append(Genome())  
            return

        for _ in range(self.pop_size-len(self.current_pop)):
            self.current_pop = np.append(self.current_pop, Genome())    
    
    def evolve(self):
        print(f"\n ============ Parameters ============\
              \n Population size: {self.pop_size} \
              \n Number of parents for one child: {self.nbr_parents} \
              \n Mutation probability: {self.mutationProb} \
              \n Max mutation amount: {self.mutationAmount} \n \n")

        for _ in range(self.generations):
            gen = NewGeneration(self.current_pop)
            gen.select_parents(self.start_angle)
            gen.crossover(arg = "mean")
            gen.mutate(self.mutationProb, self.mutationAmount)
            self.current_pop = gen.get_new_pop()
            print(f"\n ========== Generation {_+1} complete ===========\n")
            #print(self.current_pop)
            
            with open("saveData.pickle", "wb") as F:
                pickle.dump(self.current_pop, F)
            
class NewGeneration:
    def __init__(self, pop):
        self.pop = pop 
        self.pop_size = len(self.pop)
        self.parents = None
        self.parent_nbr = int(self.pop_size // 3)
        self.children: list[Genome] = []
        self.gene_editor = GeneEditor()
        self.fitnessAvg = 0
        self.avgAcc = 0
    
    def eval_fitness(self, eval_method: str) -> list[float]:
        score = []
        #accuracy = []
        angle = np.random.randint(-180, 180)

        for ind in self.pop:
            result = Game.runScenario(genome=ind, angle = angle)
            score.append(result.teams[0].lives_remaining)
            #accuracy.append(result.teams[0].accuracy)
            self.fitnessAvg += score[-1]
            #self.avgAcc += result.teams[0].accuracy
        self.fitnessAvg /= len(self.pop)
        #self.avgAcc /= len(self.pop)
        
        if eval_method == "lives_remaining": 
            return score
        elif eval_method == "accuracy":
            return accuracy
        elif eval_method == "combine":
            return [score[i]*accuracy[i] for i in range(len(score))]
        else:
            warnings.warn("No valid evaluation method parsed in eval_method, use for example asteroids hit or accuracy. Returning...")
            
    
    def select_parents(self, angle = None):
        score = self.eval_fitness("lives_remaining")
        print(f"\n Generation average score: {round(self.fitnessAvg, 2)}")
        
        parents = sorted(enumerate(score), key=lambda x: x[1])[-self.parent_nbr:]
        indices, values = zip(*parents)

        self.parents = [self.pop[idx] for idx in indices]
        print(f"\n One of the most effective: {self.parents[0].state}")
    def crossover(self, arg: str = 'select'):
        # Combine parents
        # [[1, 2, 3, 4, 5, 6], [2, 2, 3, 3, 4, 5]]
        children: list[Genome] = self.parents.copy() # keep the old parents around
        while len(children) < self.pop_size:
            parents = random.sample(self.parents, 2)
            self.gene_editor.genomes = parents
            
            if arg == "mean":
                children.append(self.gene_editor.ChildUsingMean()) # Evolving all genes
            elif arg == "select":
                children.append(self.gene_editor.childUsingSelect())

        self.children = np.array(children)
    
    def mutate(self, mutationProb, mutationAmount):
        mutationProb = mutationProb
        mutationAmount = mutationAmount
        
        mut_count = 0
        for child in self.children:
            if child in self.parents:
                continue
            for gene_name in child.state.keys():
                gene = child.state[gene_name]
                for i in range(len(gene)):
                    r = np.random.rand()
                    if r < mutationProb:
                        dr = (np.random.rand()*2 - 1) * mutationAmount
                        mut_count += 1
                        edges = child.geneNameToEdges[gene_name] # Here the edges could be fitted to the gene, placeholder...
                        if i%2 == 0:
                            gene[i] = round(float(np.clip((gene[i] + dr), edges[int(i//2)][0], edges[int(i//2)][1])), 4)
                        else:
                            gene[i] = round(float(np.clip((gene[i] + dr), gene[i-1], edges[int(i//2)][1])), 4)

            # Sorts the genes in the wanted manner (lower and upper boundary)
                for i in range(int(len(gene)//2)):
                    if gene[2*i] < gene[2*i + 1]:
                        continue
                    else:
                        temp = gene[2*i]
                        gene[2*i] = gene[2*i + 1]
                        gene[2*i + 1] = temp
        print("Mutated " + str(mut_count) + " genes")
                

    def get_new_pop(self):
        return self.children

def main():
    fresh_batch = False
    
    if fresh_batch:
        GA = GeneticAlgorithm(pop_size=30, nbr_parents=2, generations=20, mutation_rate=0.2, mutation_amount = 1)
        GA.evolve()
    else:
        with open("saveData.pickle", "rb") as F:
            data = pickle.load(F)
        print(type(data))

        GA = GeneticAlgorithm(pop_size=30, nbr_parents=2, generations=20, mutation_rate=0.25, mutation_amount = 1, start_point=data)
        GA.evolve()
    
    # Saving the AI model in pickle file
    with open("saveData.pickle", "wb") as F:
        pickle.dump(GA.current_pop, F)

    
if __name__ == '__main__':
    main()
