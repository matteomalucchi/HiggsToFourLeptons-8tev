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
import time
import os
import sys

import ROOT

sys.path.append('../')

from Definitions.eos_link_def import  EOS_LINK
from Definitions.samples_def import  SAMPLES
from Definitions.variables_def import  VARIABLES
from Definitions.weights_def import  WEIGHTS

from Skimming import skim_tools

import set_up


def skim(args, logger, path_sf="Skimming"):
    """ Main function of the skimming step.
    The function loops over the datasets and distinguishes the possible
    final states. It creates for each one of them a RDataFrame which allows
    to apply cuts and define new useful observables. Finally, it creates files
    containing the new skimmed data in the directory ``Skim_data/``.

    :param args: Global configuration of the analysis.
    :type args: argparse.Namespace
    :param logger: Configurated logger for printing messages.
    :type logger: logging.RootLogger
    :param path_sf: Optional base path to find the header file ``skim_functions.h``.
    :type path_sf: str
    """

    logger.info(">>> Executing %s \n", os.path.basename(__file__))

    ROOT.gInterpreter.ProcessLine(f'#include "{os.path.join(path_sf, "skim_functions.h")}"' )

    #Enamble multi-threading if range is not active
    if args.parallel and args.range == 0:
        ROOT.ROOT.EnableImplicitMT(args.nWorkers)
        thread_size = ROOT.ROOT.GetThreadPoolSize()
        logger.info(">>> Thread pool size for parallel processing: %s", thread_size)

    # Create the directory to save the skimmed data if doesn't already exist
    dir_name = os.path.join(args.output, "Skim_data")
    try:
        os.makedirs(dir_name)
        logger.debug("Directory %s/ Created", dir_name)
    except FileExistsError:
        logger.debug("The directory %s/ already exists", dir_name)
        
    #Loop over the various samples
    for sample_name, final_states in SAMPLES.items():
        file_name=os.path.join(args.basePath, f"{sample_name}.root")
        
        # Check if the sample is one of those requested by the user
        if sample_name not in args.sample and args.sample != "all":
            continue

        # Check if file exists or not 
        try:
            if not os.path.exists(file_name):
                raise FileNotFoundError
        except FileNotFoundError as not_fund_err:
            logger.debug("File %s.root can't be found locally %s",
                            sample_name, not_fund_err,  stack_info=True)
            logger.debug("File %s.root is obtained from the following EOS link: \n %s",
                            sample_name, EOS_LINK,  stack_info=True)
            file_name=os.path.join(EOS_LINK, f"{sample_name}.root")
        finally:
            rdf = ROOT.RDataFrame("Events", file_name)

        # Analysis only part of the data if the range option is active
        if args.range != 0:
            rdf=rdf.Range(args.range)

        # Loop over the possible final states
        for final_state in final_states:
            
            # Check if the final state is one of those requested by the user
            if final_state not in args.finalState and args.finalState != "all":
                continue
            
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
            rdf_final = skim_tools.add_event_weight(rdf7, WEIGHTS[sample_name])
            
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
                            help='number of events on which the analysis \
                            is ran over (does not work in parallel)')
    parser.add_argument('-p', '--parallel',   default=True,   action='store_const',
                            const=False, help='disables running in parallel')
    parser.add_argument('-n', '--nWorkers',   default=0,
                            type=int,   help='number of workers' )
    parser.add_argument('-o', '--output',     default="../Output", type=str,
                            help='name of the output directory')
    parser.add_argument('-l', '--logLevel',   default=20, type=int,   
                            help='integer representing the level of the logger:\
                             DEBUG=10, INFO = 20, WARNING = 30, ERROR = 40' )
    parser.add_argument('-f', '--finalState',   default="all", type=str,   
                            help='comma separated list of the final states to analyse: \
                            FourMuons, FourElectrons, TwoMuonsTwoElectrons' )     
    parser.add_argument('-s', '--sample',    default="all", type=str,
                        help='string with comma separated list of samples to analyse: \
                        Run2012B_DoubleElectron, Run2012B_DoubleMuParked, Run2012C_DoubleElectron, \
                        Run2012C_DoubleMuParked, SMHiggsToZZTo4L, ZZTo2e2mu, ZZTo4e, ZZTo4mu')
    parser.add_argument("-b", "--basePath",  nargs="?", default="../Input",  const=EOS_LINK,
                            type=str, help="base path where to find the input data. \
                            If enabled it automatically gets the input data from EOS")
    args_main = parser.parse_args()


    logger_main=set_up.set_up(args_main)
    

    skim(args_main, logger_main, "")
