# -*- coding: utf-8 -*-
# Copyright © 2022 Thales. All Rights Reserved.
# NOTICE: This file is subject to the license agreement defined in file 'LICENSE', which is part of
# this source code package.

import sys
import os
import pickle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
import formulaScenario as Game
import warnings

import numpy as np
import random
from experiment_Simon.Old.genomeOld import Genome
from gene_editor import GeneEditor

np.set_printoptions(legacy='1.25') # When printing out the genes we dont want it to say np.array

class GeneticAlgorithm:
    def __init__(self, pop_size, nbr_parents, generations, mutation_rate, mutation_amount, start_angle: float = None, start_point: list[float] = None, parents_ratio = 2):
        """Include start point to start from previous genetic code"""
        self.start_angle = start_angle
        self.random_angle = True if self.start_angle == None else False
        self.pop_size = pop_size
        self.nbr_parents = nbr_parents
        self.parent_ratio = parents_ratio
        self.generations = generations
        self.mutationProb = mutation_rate
        self.mutationAmount = mutation_amount

        self.current_pop: list[Genome] = None if start_point is None else start_point
        self.init_pop()

    def init_pop(self):
        if self.current_pop is None:
            print("Creating entire new generation...")
            self.current_pop = [] 
            for _ in range(self.pop_size-len(self.current_pop)):
                self.current_pop.append(Genome())  
            return


        for _ in range(self.pop_size-len(self.current_pop)):
            self.current_pop = np.append(self.current_pop, Genome())    
            #self.current_pop.append(Genome()) 
            print("Appending new genome to old list...")
        print(f"\nFirst genome is: {self.current_pop[0].state}... \n")
    
    def evolve(self):
        print(f"\n ============ Parameters ============\
              \n Population size: {self.pop_size} \
              \n Number of parents for one child: {self.nbr_parents} \
              \n Mutation probability: {self.mutationProb} \
              \n Max mutation amount: {self.mutationAmount} \n \n")

        for _ in range(self.generations):
            gen = NewGeneration(self.current_pop, parent_ratio= self.parent_ratio)
            gen.select_parents(self.start_angle)
            gen.crossover(arg = "mean")
            gen.mutate(self.mutationProb, self.mutationAmount)
            self.current_pop = gen.get_new_pop()
            with open("saveData.pickle", "wb") as F:
                seed = np.random.randint(0, 10000)
                pickle.dump((self.current_pop, seed), F)
                print(f"\n(Saved with seed {seed})\n")
                F.close()
            print(f"\n ========== Generation {_+1} complete ===========\n")

            



class NewGeneration:
    def __init__(self, pop, parent_ratio):
        self.pop = pop 
        self.pop_size = len(self.pop)
        self.parents = None
        self.parent_nbr = int(self.pop_size // parent_ratio)
        self.children: list[Genome] = []
        self.gene_editor = GeneEditor()
        self.fitnessAvg = 0
        self.avgAcc = 0
    
    def eval_fitness(self, eval_method: str) -> list[float]:
        score = []
        accuracy = []
        angle = np.random.randint(-180, 180)
        print(f"\n Evaluating fitness with angle = {angle}\n")
        bestGenome = {}
        bestScore = 0
        for ind in self.pop:
            result = Game.runScenario(genome=ind, angle = angle)
            newScore = result.teams[0].asteroids_hit
            if newScore >= bestScore: 
                bestScore = newScore
                bestGenome = ind
            score.append(newScore)
            accuracy.append(result.teams[0].accuracy)
            self.fitnessAvg += score[-1]
            self.avgAcc += result.teams[0].accuracy
        self.fitnessAvg /= len(self.pop)
        self.avgAcc /= len(self.pop)
        
        print(f"\n Most asteroids hit: {bestGenome.state}")

        if eval_method == "asteroids hit": 
            return score
        elif eval_method == "accuracy":
            return accuracy
        elif eval_method == "combine":
            return [score[i]*accuracy[i] for i in range(len(score))]
        else:
            warnings.warn("No valid evaluation method parsed in eval_method, use for example asteroids hit or accuracy. Returning...")
            
    
    def select_parents(self, angle = None):
        score = self.eval_fitness("accuracy")
        print(f"\n Score: {round(self.fitnessAvg, 2)} \n Accuracy: {round(self.avgAcc, 2)}")
        
        parents = sorted(enumerate(score), key=lambda x: x[1])[-self.parent_nbr:]
        indices, values = zip(*parents)

        self.parents = [self.pop[idx] for idx in indices]
        #print(f"\n The most effective: {self.parents[0].state}")
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
                for i in range(len(gene)//2 + 1):
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
            child.makeSymmetric()
        print("\n Mutated " + str(mut_count) + " genes")
                

    def get_new_pop(self):
        return self.children

def main():
    fresh_batch = False # Train further with the previous gene pool or create new
    
    mut_rate = 0.2
    mut_amount = 0.25
    pop_size = 60
    nbr_parents = 2
    gens = 200
    parent_ratio = 4

    if fresh_batch:
        GA = GeneticAlgorithm(pop_size=pop_size, nbr_parents=nbr_parents, generations=gens, mutation_rate=mut_rate, mutation_amount = mut_amount, parents_ratio=parent_ratio)
        GA.evolve()
    else:
        with open("saveData.pickle", "rb") as F:
            allData = pickle.load(F)
            data = allData[0]
            seed = allData[1]
            F.close()
        with open("saveData.pickle", "wb") as F:
            pickle.dump((data, seed), F)
            F.close()
            print(f"\n (Opening old save with seed {seed}) \n")
        GA = GeneticAlgorithm(pop_size=pop_size, nbr_parents=nbr_parents, generations=gens, mutation_rate=mut_rate, mutation_amount = mut_amount, start_point=data, parents_ratio=parent_ratio)
        GA.evolve()
    
    # Saving the AI model in pickle file
    with open("saveData.pickle", "wb") as F:
        seed = np.random.randint(0, 10000)
        pickle.dump((GA.current_pop, seed), F)
        print(f"\n (Saved with seed {seed})\n")
        F.close()

    
if __name__ == '__main__':
    main()
