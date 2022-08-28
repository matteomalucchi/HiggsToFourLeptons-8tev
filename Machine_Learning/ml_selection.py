"""
This step consists in the selection of the events for which
the discriminant created by the DNN is above the 0.5 threshold.
A new set of files is created for this purpose.
"""

import time
import os
import sys
import argparse
import logging

import ROOT

sys.path.append('../')
from Definitions.samples_def import  SAMPLES
from Definitions.variables_def import VARIABLES_COMPLETE


def ml_selection(args, logger, path_sd=""):
    """Main function for the selection of the events for which
    the discriminant created by the DNN is above the 0.5 threshold.

    :param args: Global configuration of the analysis.
    :type args: argparse.Namespace
    :param logger: Configurated logger for printing messages.
    :type logger: logging.RootLogger
    :param path_sd: Optional base path to find the directory ``Skim_data/``.
    :type path_sd: str
    """

    logger.info(">>> Executing %s \n", os.path.basename(__file__))

    # Enamble multi-threading
    if args.parallel:
        ROOT.ROOT.EnableImplicitMT()
        thread_size = ROOT.ROOT.GetThreadPoolSize()
        logger.info(">>> Thread pool size for parallel processing: %s", thread_size)

    #Loop over the various samples and final states
    for sample_name, final_states in SAMPLES.items():
        for final_state in final_states:
            # Check if the final state is one of those requested by the user
            if final_state not in args.finalState and args.finalState != "all":
                continue
            logger.info(">>> Process sample: %s and final state %s", sample_name, final_state)
            start_time = time.time()
            
            file_name=os.path.join(path_sd, args.output, "Skim_data",
                                f"{sample_name}{final_state}Skim.root")
            
            # Check if file exists or not 
            try:
                if not os.path.exists(file_name):
                    raise FileNotFoundError
                rdf = ROOT.RDataFrame("Events", file_name)
            except FileNotFoundError as not_fund_err:
                logger.debug("Sample %s final state %s: File %s can't be found %s",
                                    sample_name, final_state, file_name, not_fund_err,  stack_info=True)
                continue

            rdf_final = rdf.Filter("Discriminant>0.5",
                                    "Select only events with above threshold discriminat")
            
            if args.logLevel <= 10:
                rdf_final.Report().Print()
            logger.debug("%s\n", rdf_final.GetColumnNames())

            # Create another TTree of the selected events inside the preexisting file
            option = ROOT.RDF.RSnapshotOptions("UPDATE", ROOT.kZLIB, 1, 0, 99, False, True)
            try:
                rdf_final.Snapshot("EventsDNNSelection", file_name, VARIABLES_COMPLETE.keys(), option)
            except TypeError:
                logger.debug("Sample %s final state %s is empty", sample_name, final_state)

            logger.info(">>> Execution time: %s s \n", (time.time() - start_time))

if __name__ == "__main__":

    # General configuration
    parser = argparse.ArgumentParser( description = 'Analysis Tool' )
    parser.add_argument('-p', '--parallel',   default=True,   action='store_const',
                        const=False, help='disables running in parallel')
    parser.add_argument('-n', '--nWorkers',   default=0,
                        type=int,   help='number of workers' )
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

    ml_selection(args_main, logger_main, "..")
