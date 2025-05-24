import skfuzzy.control
import sys
sys.path.append('/Users/simon_stoll/Documents/programmering/KEX/Swedish-Vikings/kessler-game-main')

import src
import warnings
from src.kesslergame import KesslerController, asteroid
from typing import Dict, Tuple
import skfuzzy.control as ctrl
import skfuzzy as skf
import numpy as np
from typing import Any

class GenomeOld:
    def __init__(self, geneDict: dict[str, list[float]] = None):
        self.geneDict: dict = geneDict if geneDict is not None else dict()
        self.geneNames = ["desired_angle", "angle", "angle_velocity", "distance"]

        self.geneNameToEdges = {
        "desired_angle": self.edges["standard"],
        "angle": self.edges["standard"],
        "angle_velocity": self.edges["standard5"],
        "distance": self.edges["distance"]
        }

        self.geneNameToSymmetry = {
            "desired_angle": True,
            "angle": True,
            "angle_velocity": True,
            "distance": False
        }

        for name in self.geneNames:
            if not self.geneDict.__contains__(name):
                self.geneDict[name] = self.createGene(self.geneNameToEdges[name])
        self.makeSymmetric()

    @property
    def state(self) -> Dict[str, list[float]]:
        return self.geneDict

    @property
    def edges(self) -> Dict[str, Any]:
        return {
            "standard": [(-1, 0), (-1, 1), (0, 1)],
            "standard5": [(-1, -0.25), (-0.75, 0), (-1, 1), (0, 0.75), (0.25, 1)],
            "distance": [(0, 0.5), (0, 1), (0.5, 1)]
        }

        
    
    
    def createGene(self, edges: list[tuple[float]]) -> list[float]:
        gene = []
        for i in range(len(edges)*2):
            flt = 0
            edgeTuple = edges[i//2]
            """
            if symmetric and i >= len(edges): # Makes a symmetric gene
                symmetry_partner = gene[(len(edges) - (1+i%len(edges)))]
                if symmetry_partner <= 0:
                    flt = abs(gene[(len(edges) - (1+i%len(edges)))])
                    gene.append(flt)
                    continue
                else:
                    pass
                """
            if not i % 2:
                flt = np.random.random_sample() * (edgeTuple[1]-edgeTuple[0]) + edgeTuple[0]
            else:
                flt = flt = np.random.random_sample() * (edgeTuple[1]-gene[i-1]) + gene[i-1]
            gene.append(flt)
        # Symmetric part
        return np.array(gene)
        
    def makeSymmetric(self):
        for gene_name in self.state.keys():
            if not self.geneNameToSymmetry[gene_name]:
                continue

            edges = self.geneNameToEdges[gene_name]
            gene = self.state[gene_name]

            for i in range(len(edges), len(edges)*2):
                symmetry_partner = gene[(len(edges) - (1+i%len(edges)))]
                if symmetry_partner <= 0:
                    gene[i] = abs(symmetry_partner)
                else:
                    gene[(len(edges) - (1+i%len(edges)))] = -1*abs(symmetry_partner)
                    gene[i] = abs(symmetry_partner)
                
            

    def ApplyToTrap(self, member_function: ctrl.Antecedent, names: list[str], gene_to_apply: str):
        if not self.geneNameToEdges.__contains__(gene_to_apply):
            warnings.warn(f"The gene {gene_to_apply} does not have an associated edge in the geneNamesToEdges dictionary, returning...")
            return
        
        edges = self.geneNameToEdges[gene_to_apply] 
        if len(names) != len(edges):
            print("Error: length of edges does not match length of names. Returning...")
            return
        
        for idx in range(len(names)):
            member_function[names[idx]] = skf.trapmf(member_function.universe, [edges[idx][0], self.state[gene_to_apply][idx*2], self.state[gene_to_apply][idx*2+1], edges[idx][1]])
    