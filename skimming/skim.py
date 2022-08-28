"""
Implementation of the skimming process

This consists in reducing the initial samples to a dataset
specific for this analysis. The skimming removes all events
which are not of interest for the reconstruction of Z bosons
from combinations of leptons, which may originate from the
decay of a Higgs boson. Furthermore, all the variables used
later on are defined. This includes mass and Pt of Z and Higgs
bosons, as well as five dacay angles defined in `[Phys.Rev.D86:095031,2012]
<https://journals.aps.org/prd/abstract/10.1103/PhysRevD.86.095031>`_
which are later used for a machine learning algorithm.
"""

import argparse
import logging
import time
import os
import sys

import ROOT

sys.path.append('../')

from Definitions.base_path_def import  BASE_PATH
from Definitions.samples_def import  SAMPLES
from Definitions.variables_def import  VARIABLES

from Skimming import skim_tools


def skim(args, logger, path_sf="skimming", path_sd=""):
    """ Main function of the skimming step.
    The function loops over the datasets and distinguishes the possible
    final states. It creates for each one of them a RDataFrame which allows
    to apply cuts and define new useful observables. Finally, it creates files
    containing the new skimmed data in the directory ``skim_data/``.

    :param args: Global configuration of the analysis.
    :type args: argparse.Namespace
    :param logger: Configurated logger for printing messages.
    :type logger: logging.RootLogger
    :param path_sf: Optional base path to find the header file ``skim_functions.h``.
    :type path_sf: str
    :param path_sd: Optional base path to find the directory ``skim_data/``.
    :type path_sd: str
    """

    logger.info(">>> Executing %s \n", os.path.basename(__file__))

    ROOT.gInterpreter.ProcessLine(f'#include "{os.path.join(path_sf, "skim_functions.h")}"' )

    #Enamble multi-threading if range is not active
    if args.parallel and args.range == 0:
        ROOT.ROOT.EnableImplicitMT(args.nWorkers)
        thread_size = ROOT.ROOT.GetThreadPoolSize()
        logger.info(">>> Thread pool size for parallel processing: %s", thread_size)

    # Create the directory to save the skimmed data if doesn't already exist
    dir_name = os.path.join(path_sd, args.output, "skim_data")
    try:
        os.makedirs(dir_name)
        logger.debug("Directory %s/ Created", dir_name)
    except FileExistsError:
        logger.debug("The directory %s/ already exists", dir_name)

    #Loop over the various samples
    for sample_name, final_states in SAMPLES.items():
        file_name=os.path.join( BASE_PATH, f"{sample_name}.root")

        # Check if file exists or not 
        try:
            if not os.path.exists(file_name):
                raise FileNotFoundError
            rdf = ROOT.RDataFrame("Events", file_name)
        except FileNotFoundError as not_fund_err:
            logger.debug("Sample %s: File %s can't be found %s",
                                sample_name, file_name, not_fund_err,  stack_info=True)
            continue

        # Analysis only part of the data if the range option is active
        if args.range != 0:
            rdf=rdf.Range(args.range)

        # Loop over the possible final states
        for final_state in final_states:
            logger.info(">>> Process sample: %s and final state %s \n", sample_name, final_state)

            start_time = time.time()

            try:
                rdf2 = skim_tools.event_selection(rdf, final_state)
                rdf3 = skim_tools.four_vec(rdf2, final_state)
                rdf4 = skim_tools.order_four_vec(rdf3, final_state)
            except RuntimeError as run_time_err:
                logger.exception("Sample %s ERROR: %s ", sample_name, run_time_err,  stack_info=True)
                continue

            rdf5 = skim_tools.def_mass_pt_eta_phi(rdf4)
            rdf6 = skim_tools.four_vec_boost(rdf5)
            rdf7 = skim_tools.def_angles(rdf6)
            rdf_final = skim_tools.add_event_weight(rdf7, sample_name)
            
            if args.logLevel <= 10:
                rdf_final.Report().Print()
            logger.debug("%s\n", rdf_final.GetColumnNames())
            
            # Save the skimmed samples
            complete_name = os.path.join(dir_name, f"{sample_name}{final_state}Skim.root")
            rdf_final.Snapshot("Events", complete_name, VARIABLES.keys())

            logger.info(">>> Execution time: %s s \n", (time.time() - start_time))


if __name__ == "__main__":    
    
    # General configuration
    parser = argparse.ArgumentParser( description = 'Analysis Tool' )
    parser.add_argument('-r', '--range',  nargs='?', default=0, const=10000000, type=int,
                            help='run the analysis only on a finite range of events')
    parser.add_argument('-p', '--parallel',   default=False,   action='store_const',
                            const=True, help='enables running in parallel')
    parser.add_argument('-n', '--nWorkers',   default=0,
                            type=int,   help='number of workers' )
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

    skim(args_main, logger_main, "", "..")
