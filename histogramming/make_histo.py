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
import logging

import ROOT

sys.path.append('../')
from Definitions.variables_def import VARIABLES_DICT
from Definitions.samples_def import  SAMPLES
from Definitions.selections_def import  SELECTIONS

from Histogramming import histogramming_functions


def make_histo(args, logger, path=""):
    """ Main function of the histogramming step.
    The function loops over the outputs from the skimming step and produces the
    required histograms for the final plotting step.

    :param args: Global configuration of the analysis.
    :type args: argparse.Namespace
    :param logger: Configurated logger for printing messages.
    :type logger: logging.RootLogger
    :param path: Optional base path where the directories ``skim_data/``
        and ``histograms/`` can be found.
    :type path: str
    """

    logger.info(">>> Executing %s \n", os.path.basename(__file__))

    #Enamble multi-threading
    if args.parallel:
        ROOT.ROOT.EnableImplicitMT(args.nWorkers)
        thread_size = ROOT.ROOT.GetThreadPoolSize()
        logger.info(">>> Thread pool size for parallel processing: %s", thread_size)


    # Create the directory and the output file to store the histograms
    dir_name = os.path.join(path, args.output, "histograms")
    try:
        os.makedirs(dir_name)
        logger.debug("Directory %s/ Created", dir_name)
    except FileExistsError:
        logger.debug("The directory %s/ already exists", dir_name)
        
    outfile_path = os.path.join(dir_name, "histograms.root")
    outfile = ROOT.TFile(outfile_path, "RECREATE")

    if args.ml :
        var_dict = VARIABLES_DICT["tot"]
    else :
        var_dict = VARIABLES_DICT["part"]

    variables = var_dict.keys()

    # Loop over the possible selections
    for selection, tree_name in SELECTIONS.items():

        # Loop through skimmed datasets and final states 
        # to produce histograms of all variables.
        for sample, final_states in SAMPLES.items():
            for final_state in final_states:
                logger.info(">>> Process sample {sample} and final state  \
                            {final_state} with {selection}")
                
                start_time = time.time()

                # Create dataframe of the skimmed dataset.
                complete_name = os.path.join(path, args.output, "skim_data",
                                             f"{sample}{final_state}Skim.root")
                rdf = ROOT.RDataFrame(tree_name, complete_name)

                # Book histograms and write them to output file.
                histos = {}
                for variable in variables:
                    if variable != "Weight":
                        histos[variable] = histogramming_functions.book_histogram_1d \
                                                (rdf, variable, var_dict[variable])
                        histogramming_functions.write_histogram(histos[variable],
                                                f"{sample}_{final_state}_{variable}_{selection}")

                        #logger.info(type(histos[variable]))
                logger.info(">>> Execution time: %s s \n", (time.time() - start_time))
                
    outfile.Close()


if __name__ == "__main__":

    # General configuration
    parser = argparse.ArgumentParser( description = 'Analysis Tool' )
    parser.add_argument('-p', '--parallel',   default=False,   action='store_const',
                        const=True, help='enables running in parallel')
    parser.add_argument('-n', '--nWorkers',   default=0,
                        type=int,   help='number of workers' )
    parser.add_argument('-m', '--ml', default=False,   action='store_const', const=True,
                        help='enables machine learning algorithm')
    parser.add_argument('-o', '--output',     default="Output", type=str,
                        help='name of the output directory')
    parser.add_argument('-l', '--logLevel',   default=20, type=int,   
                            help='integer representing the level of the logger:\
                             DEBUG=10, INFO = 20, WARNING = 30, ERROR = 40' )
    args_main = parser.parse_args()

    # Create and configure logger
    logging.basicConfig( format='\n%(asctime)s %(message)s')
    # Create an object
    logger_main=logging.getLogger()
    # Set the threshold of logger
    logger_main.setLevel(args_main.logLevel)

    make_histo(args_main, logger_main, "..")
