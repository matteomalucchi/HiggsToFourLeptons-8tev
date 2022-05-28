import time
import os
import sys
import ROOT


from skimming import skim_tools

from definitions.base_path_def import  BASE_PATH
from definitions.samples_def import  SAMPLES
from definitions.variables_def import  VARIABLES

class Skimming:
    
    def __init__(self, samples):
        self.
    
    def create_rdf(self, sample_name):
        infile_path = os.path.join(BASE_PATH, f"{sample_name}.root")
        rdf = ROOT.RDataFrame("Events", infile_path)