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
from FrameworkClasses.genome import Genome

class AsteroidChooserGenome(Genome):
    def __init__(self, geneDict: dict[str, list[float]] = None):
        self.geneDict: dict = geneDict if geneDict is not None else dict()
        self.geneNames = ["angle", "distance", "size", "relevance"]

        self.symmetricGenes = []

        for name in self.geneNames:
            if not self.geneDict.__contains__(name):
                self.geneDict[name] = self.createGene(self.geneNameToEdges[name])
        self.makeSymmetric()

    @property
    def state(self) -> Dict[str, list[float]]:
        return self.geneDict


    @property
    def geneNameToEdges(self) -> Dict[str, Any]:
        return {
            "angle": self.edges["positive3"],
            "distance": self.edges["positive3"],
            "size": self.edges["positive3"],
            "relevance": self.edges["positive3"]
        }


    @property
    def edges(self) -> Dict[str, Any]:
        return {
            "standard": [(-1, 0), (-1, 1), (0, 1)],
            "standard5": [(-1, -0.25), (-0.75, 0), (-1, 1), (0, 0.75), (0.25, 1)],
            "positive3": [(0, 0.5), (0, 1), (0.5, 1)]
        }
