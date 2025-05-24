import skfuzzy.control
import sys

import src
from src.kesslergame import KesslerController, asteroid
from typing import Dict, Tuple
import skfuzzy.control as ctrl
import skfuzzy as skf
import numpy as np
from typing import Any

class Genome:
    def __init__(self, geneDict: dict[str, list[float]] = None):
        self.geneDict: dict = geneDict if geneDict is not None else dict()
        self.geneNames = ["desired_speed", "current_speed", "relative_angle"]#, "check_radius"]

        self.geneNameToEdges = {
        "desired_speed": self.edges["standard"],
        "current_speed": self.edges["standard"],
        "relative_angle": self.edges["standard"],
        #"check_radius": self.edges["radius"]
        }

        #self.geneDict["check_radius"] = self.createRadiusGene(self.geneNameToEdges["check_radius"])
        for name in self.geneNames:
            if not self.geneDict.__contains__(name):
                self.geneDict[name] = self.createGene(self.geneNameToEdges[name])

    @property
    def state(self) -> Dict[str, list[float]]:
        return self.geneDict

    @property
    def edges(self) -> Dict[str, Any]:
        return {
            "standard": [(-1, 0), (-1, 1), (0, 1)],
            "standard5": [(-1, -0.5), (-0.5, 0), (-1, 1), (0, 0.5), (0.5, 1)],
            "radius": [(10, 1000)]
        }

    def createGene(self, edges: list[tuple[float]]) -> list[float]:
        gene = []
        for i in range(len(edges)*2):
            flt = 0
            edgeTuple = edges[i//2]
            if not i % 2:
                flt = np.random.random_sample() * (edgeTuple[1]-edgeTuple[0]) + edgeTuple[0]
            else:
                flt = flt = np.random.random_sample() * (edgeTuple[1]-gene[i-1]) + gene[i-1]
            gene.append(flt)

        return np.array(gene)
    
    def createRadiusGene(self, edges: list[tuple[float]]) -> list[float]:
        gene = [np.random.random_sample() * (edges[0][1] - edges[0][0]) + edges[0][0]]
        return np.array(gene)    

    def ApplyToTrap(self, member_function: ctrl.Antecedent, names: list[str], gene_to_apply: str,edges: list[tuple[float]] = [(-1.0, 0.0), (-1.0, 1.0), (0.0, 1.0)]):
        
        if len(names) != len(edges):
            print("Error: length of edges does not match length of names. Returning...")
            return
        
        for idx in range(len(names)):
            member_function[names[idx]] = skf.trapmf(member_function.universe, [edges[idx][0], self.state[gene_to_apply][idx*2], self.state[gene_to_apply][idx*2+1], edges[idx][1]])
    