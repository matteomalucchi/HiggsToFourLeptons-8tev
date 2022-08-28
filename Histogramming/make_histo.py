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
from typing import Type

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
    :param path: Optional base path where the directories ``Skim_data/``
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
    dir_name = os.path.join(path, args.output, "Histograms")
    try:
        os.makedirs(dir_name)
        logger.debug("Directory %s/ Created", dir_name)
    except FileExistsError:
        logger.debug("The directory %s/ already exists", dir_name)
        
    outfile_path = os.path.join(dir_name, "Histograms.root")
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
        for sample_name, final_states in SAMPLES.items():
            for final_state in final_states:
                # Check if the final state is one of those requested by the user
                if final_state not in args.finalState and args.finalState != "all":
                    continue
                logger.info(">>> Process sample %s and final state %s with %s",
                            sample_name, final_state, selection)
                
                start_time = time.time()

                file_name = os.path.join(path, args.output, "Skim_data",
                                             f"{sample_name}{final_state}Skim.root")
                
                # Check if file exists or not 
                try:
                    if not os.path.exists(file_name):
                        raise FileNotFoundError
                    rdf = ROOT.RDataFrame(tree_name, file_name)
                except FileNotFoundError as not_fund_err:
                    logger.debug("Sample %s final state %s: File %s can't be found %s",
                                    sample_name, final_state, file_name, not_fund_err,  stack_info=True)
                    continue

                # Book histograms and write them to output file.
                histos = {}
                try:
                    for variable in variables:
                        if variable != "Weight":
                                histos[variable] = histogramming_functions.book_histogram_1d\
                                                        (rdf, variable, var_dict[variable])
                                histogramming_functions.write_histogram(histos[variable],
                                                        f"{sample_name}_{final_state}_{variable}_{selection}")
                except TypeError:
                    logger.debug("Sample %s final state %s is empty", sample_name, final_state)
                    
                logger.info(">>> Execution time: %s s \n", (time.time() - start_time))
                
    outfile.Close()


if __name__ == "__main__":

    # General configuration
    parser = argparse.ArgumentParser( description = 'Analysis Tool' )
    parser.add_argument('-p', '--parallel',   default=True,   action='store_const',
                        const=False, help='disables running in parallel')
    parser.add_argument('-n', '--nWorkers',   default=0,
                        type=int,   help='number of workers' )
    parser.add_argument('-m', '--ml', default=True,   action='store_const', const=False,
                        help='disables machine learning algorithm')
    parser.add_argument('-o', '--output',     default="Output", type=str,
                        help='name of the output directory')
    parser.add_argument('-l', '--logLevel',   default=20, type=int,   
                            help='integer representing the level of the logger:\
                             DEBUG=10, INFO = 20, WARNING = 30, ERROR = 40' )
    parser.add_argument('-f', '--finalState',   default="all", type=str,   
                            help='comma separated list of the final states to analyse: \
                            FourMuons,FourElectrons,TwoMuonsTwoElectrons' )
    args_main = parser.parse_args()

    # Create and configure logger
    logging.basicConfig( format='\n%(asctime)s %(message)s')
    # Create an object
    logger_main=logging.getLogger()
    
    # Check if logLevel valid           
    try:
        if args_main.logLevel not in [10, 20, 30, 40]:
            raise argparse.ArgumentTypeError(f"the value for logLevel {args_main.logLevel} is invalid: it must be either 10, 20, 30 or 40")
    except argparse.ArgumentTypeError as arg_err:
        args_main.logLevel = 20
        logger_main.exception("%s \nlogLevel is set to 20 \n", arg_err, stack_info=True)
        
    # Set the threshold of logger
    logger_main.setLevel(args_main.logLevel)

    # Check if finalState is valid
    try:
        if not any(final_state in args_main.finalState for final_state 
               in ["all", "FourMuons", "FourElectrons", "TwoMuonsTwoElectrons"]):
            raise argparse.ArgumentTypeError(f"the final state {args_main.finalState} is invalid: \
                it must be either all,FourMuons,FourElectrons,TwoMuonsTwoElectrons")
    except argparse.ArgumentTypeError as arg_err:
        logger_main.exception("%s \n finalState is set to all \n", arg_err, stack_info=True)
        args_main.finalState = "all"  

    make_histo(args_main, logger_main, "..")
