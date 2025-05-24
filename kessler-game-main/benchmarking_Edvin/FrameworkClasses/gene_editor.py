import skfuzzy.control
import sys
sys.path.append('/Users/simon_stoll/Documents/programmering/KEX/Swedish-Vikings/kessler-game-main')

import warnings
import src
from src.kesslergame import KesslerController, asteroid
from typing import Dict, Tuple
import skfuzzy.control as ctrl
import skfuzzy as skf
import numpy as np
from typing import Any
from experiment_Simon.FrameworkClasses.genome import Genome

class GeneEditor:
    """Contains methods for combining two parent genomes into a child genome."""
    def __init__(self, genomes: tuple[Genome] = None):
        self.genomes = genomes
    
    def ChildUsingMean(self, specific_genes: list[str] = None):
        """Makes a child genome by combining the parents with a mean-method. Specify a single or list of strings for developing a specific gene,
            otherwise all genes will be combined."""
        child = self.genomes[0].__class__()
        if specific_genes == None:
            genes: dict[str, list[float]] = self.genomes[0].state
            for gene in genes.keys():
                child.state[gene] = np.zeros_like(self.genomes[0].state[gene])
                for genome in self.genomes:
                    child.state[gene] += genome.state[gene]
                child.state[gene] /= len(self.genomes)
            return child

        # If single string
        elif isinstance(specific_genes, str):
            specific_genes = [specific_genes]
        
        # If list of strings
        if isinstance(specific_genes, list[str]):
            for gene in specific_genes:
                child.state[gene] *= 0
                for genome in self.genomes:
                    child.state[gene] += genome.state[gene]
            return child

        warnings.warn("specific_gene parameter is of wrong type, must be either str, list[str] or nonetype. Returning none...")
        return None

    def childUsingSelect(self, specific_genes: list[str] = None):
        """Makes a child genome by combining the parents with a mean-method. Specify a single or list of strings for developing a specific gene,
        otherwise all genes will be combined."""
        child: Genome = Genome()
        if specific_genes is str: specific_genes = [specific_genes]
        specific_genes = specific_genes if specific_genes is not None else child.state.keys()

        if specific_genes is not list[str]:
            warnings.warn("specific_gene parameter is of wrong type, must be either str, list[str] or nonetype. Returning none...")
        
        genes: dict[str, list[float]] = child.state
        for gene in specific_genes:
            for i in range(genes[gene]):
                r = np.random.randint(0, len(self.genomes))
                child.state[gene][i] = self.genomes[r].state[gene][i]
        return child
    
