"""
Implementation of the histogramming step of the analysis

The histogramming step produces histograms for each variable in each dataset.
Then, the resulting histograms are passed to the plotting
step, which combines them so that the physics of the decay can be studied.
"""
import time
import os
import sys
import argparse

import ROOT

sys.path.append('../')
from definitions.variables_def import VARIABLES_DICT
from definitions.samples_def import  SAMPLES
from definitions.selections_def import  SELECTIONS

from histogramming import histogramming_functions


def make_histo(args, path=""):
    """ Main function of the histogramming step. 
    The function loops over the outputs from the skimming step and produces the
    required histograms for the final plotting step.
    
    :param args: Global configuration of the analysis.
    :type args: argparse.Namespace
    :param path: Optional base path where the directories ``skim_data/`` and ``histograms/`` can be found.
    :type path: str
    """
    
    print(f"\n>>> Executing {os.path.basename(__file__)}\n")

    #Enamble multi-threading
    if args.parallel:
        ROOT.ROOT.EnableImplicitMT(args.nWorkers)
        thread_size = ROOT.ROOT.GetThreadPoolSize()
        print(f">>> Thread pool size for parallel processing: {thread_size}")

    
    # Create the directory and the output file to store the histograms
    dir_name = os.path.join(path, "histograms")
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        print("Directory " , dir_name ,  " Created ")
    outfile_path = os.path.join(dir_name, "histograms.root")
    outfile = ROOT.TFile(outfile_path, "RECREATE")
    
    if args.ml :
        var_dict = VARIABLES_DICT["tot"]
    else : 
        var_dict = VARIABLES_DICT["part"]
        
    variables = var_dict.keys()
        
    # Loop over the possible selections
    for selection, tree_name in SELECTIONS.items():
        
        # Loop through skimmed datasets and final states to produce histograms of all variables.
        for sample, final_states in SAMPLES.items():
            for final_state in final_states:
                print(f">>> Process sample {sample} and final state {final_state} with {selection}")
                start_time = time.time()

                # Create dataframe of the skimmed dataset.
                complete_name = os.path.join(path, "skim_data", f"{sample}{final_state}Skim.root")
                rdf = ROOT.RDataFrame(tree_name, complete_name)

                # Book histograms and write them to output file.
                histos = {}
                for variable in variables:
                    if variable != "Weight":
                        histos[variable] = histogramming_functions.BookHistogram1D(rdf, variable, var_dict[variable])
                        histogramming_functions.WriteHistogram(histos[variable], f"{sample}_{final_state}_{variable}_{selection}")
                        
                        #print(type(histos[variable]))
                print("Execution time: %s s" %(time.time() - start_time))

    outfile.Close()


if __name__ == "__main__":

    # global configuration
    parser = argparse.ArgumentParser( description = 'Analysis Tool' )
    parser.add_argument('-p', '--parallel',   default=False,   action='store_const',     const=True, help='enables running in parallel')
    parser.add_argument('-n', '--nWorkers',   default=0,                                 type=int,   help='number of workers' )  
    parser.add_argument('-m', '--ml', default=False,   action='store_const', const=True,   help='enables machine learning algorithm')
    args = parser.parse_args()
    
    make_histo(args, "..")