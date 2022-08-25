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

    logger.info(f">>> Executing {os.path.basename(__file__)}\n")

    ROOT.gInterpreter.ProcessLine(f'#include "{os.path.join(path_sf, "skim_functions.h")}"' )

    #Enamble multi-threading if range is not active
    if args.parallel and args.range ==0:
        ROOT.ROOT.EnableImplicitMT(args.nWorkers)
        thread_size = ROOT.ROOT.GetThreadPoolSize()
        logger.info(f">>> Thread pool size for parallel processing: {thread_size}")

    # Create the directory to save the skimmed data if doesn't already exist
    dir_name = os.path.join(path_sd, args.output, "skim_data")
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        logger.debug("Directory " , dir_name ,  " Created ")

    #Loop over the various samples
    for sample_name, final_states in SAMPLES.items():
        rdf = ROOT.RDataFrame("Events", os.path.join( BASE_PATH, f"{sample_name}.root"))

        if args.range != 0:
            rdf=rdf.Range(args.range)

        # Loop over the possible final states
        for final_state in final_states:
            logger.info(f">>> Process sample: {sample_name} and final state {final_state}\n")
            start_time = time.time()

            rdf2 = skim_tools.event_selection(rdf, final_state)
            rdf3 = skim_tools.four_vec(rdf2, final_state)
            rdf4 = skim_tools.order_four_vec(rdf3, final_state)
            rdf5 = skim_tools.def_mass_pt_eta_phi(rdf4)
            rdf6 = skim_tools.four_vec_boost(rdf5)
            rdf7 = skim_tools.def_angles(rdf6)
            rdf_final = skim_tools.add_event_weight(rdf7, sample_name)

            rdf_final.Report().Print()
            logger.debug(f"{rdf_final.GetColumnNames()}\n")

            # Save the skimmed samples
            complete_name = os.path.join(dir_name, f"{sample_name}{final_state}Skim.root")

            rdf_final.Snapshot("Events", complete_name, VARIABLES.keys())

            logger.info(f">>> Execution time: {(time.time() - start_time)} s \n")


if __name__ == "__main__":

    # Create and configure logger
    logging.basicConfig( format='\n%(asctime)s %(message)s')
    # Create an object
    logger_main=logging.getLogger()
    # Set the threshold of logger
    logger_main.setLevel(logging.INFO)

    # global configuration
    parser = argparse.ArgumentParser( description = 'Analysis Tool' )
    parser.add_argument('-r', '--range',  nargs='?', default=0, const=10000000, type=int,
                            help='run the analysis only on a finite range of events')
    parser.add_argument('-p', '--parallel',   default=False,   action='store_const',
                            const=True, help='enables running in parallel')
    parser.add_argument('-n', '--nWorkers',   default=0,
                            type=int,   help='number of workers' )
    parser.add_argument('-o', '--output',     default="Output", type=str,
                            help='name of the output directory')
    args_main = parser.parse_args()

    skim(args_main, logger_main, "", "..")
