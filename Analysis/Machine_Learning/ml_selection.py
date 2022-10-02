""" This step consists in the selection of the events for which
the discriminant created by the DNN is above the threshold.
The events that pass this cut are saved in a new TTree.
"""

import argparse
import os
import sys
import time

import ROOT

sys.path.append(os.path.join("..","..", ""))
from Analysis import set_up
from Analysis.Definitions.samples_def import SAMPLES
from Analysis.Definitions.variables_def import VARIABLES_COMPLETE


def ml_selection(args, logger):
    """Main function for the selection of the events for which
    the discriminant created by the DNN is above the threshold.

    :param args: Global configuration of the analysis.
    :type args: argparse.Namespace
    :param logger: Configured logger for printing messages.
    :type logger: logging.RootLogger
    """

    logger.info(">>> Executing %s \n", os.path.basename(__file__))

    start_time_tot = time.time()

    # Enable multi-threading
    if args.parallel:
        ROOT.ROOT.EnableImplicitMT()
        thread_size = ROOT.ROOT.GetThreadPoolSize()
        logger.info(">>> Thread pool size for parallel processing: %s", thread_size)

    try:
        # Read the optimal threshold
        with open(os.path.join(args.output, "ML_output", "optimal_cut.txt"),
                                "r", encoding="utf8") as file:
            cut = file.readlines()
            if float(cut[0]) > 1:
                raise ValueError
    except (FileNotFoundError, ValueError):
        logger.exception("Couldn't find the optimal cut value. Set optimal cut to the default value 0.13")
        cut[0]=0.13


    #Loop over the various samples and final states
    for sample_name, final_states in SAMPLES.items():
        # Check if the sample to plot is one of those requested by the user
        if sample_name not in args.sample and args.sample != "all":
            continue
        for final_state in final_states:
            # Check if the final state is one of those requested by the user
            if final_state not in args.finalState and args.finalState != "all":
                continue
            logger.info(">>> Process sample: %s and final state %s", sample_name, final_state)
            start_time = time.time()

            file_name=os.path.join(args.output, "Skim_data",
                                f"{sample_name}{final_state}Skim.root")

            # Check if file exists or not
            try:
                if not os.path.exists(file_name):
                    raise FileNotFoundError
                rdf = ROOT.RDataFrame("Events", file_name)
            except FileNotFoundError as not_fund_err:
                logger.debug("Sample %s final state %s: File %s can't be found %s",
                                    sample_name, final_state, file_name,
                                    not_fund_err,  stack_info=True)
                continue

            file = ROOT.TFile(file_name,"READ")
            tree= file.Get("Events")
            branch = tree.GetListOfBranches().FindObject("Discriminant")
            if not branch:
                return

            rdf_final = rdf.Filter(f"Discriminant>{cut[0]}",
                                    "Select only events with discriminant above threshold")

            if args.logLevel <= 10:
                rdf_final.Report().Print()
            logger.debug("%s\n", rdf_final.GetColumnNames())

            # Create another TTree of the selected events inside the preexisting file
            option = ROOT.RDF.RSnapshotOptions("UPDATE", ROOT.kZLIB, 1, 0, 99, False, True)
            try:
                rdf_final.Snapshot("EventsDNNSelection", file_name,
                                    VARIABLES_COMPLETE.keys(), option)
            except TypeError:
                logger.debug("Sample %s final state %s is empty", sample_name, final_state)

            logger.info(">>> Execution time for %s %s: %s s \n", sample_name,
                        final_state, (time.time() - start_time))

    logger.info(">>> Total execution time: %s s \n",(time.time() - start_time_tot))


if __name__ == "__main__":

    # General configuration
    parser = argparse.ArgumentParser( description = "Analysis Tool" )
    parser.add_argument("-p", "--parallel",   default=True,   action="store_const",
                        const=False, help="disables running in parallel")
    parser.add_argument("-n", "--nWorkers",   default=0,
                        type=int,   help="number of workers for multi-threading" )
    parser.add_argument("-o", "--output",     default=os.path.join("..", "..", "Output"), type=str,
                        help="path to the output folder w.r.t. the current directory")
    parser.add_argument("-l", "--logLevel",   default=20, type=int,
                            help="integer representing the level of the logger:\
                             DEBUG=10, INFO = 20, WARNING = 30, ERROR = 40" )
    parser.add_argument("-f", "--finalState",   default="all", type=str,
                            help="comma separated list of the final states to analyse: \
                            FourMuons,FourElectrons,TwoMuonsTwoElectrons" )
    parser.add_argument("-s", "--sample",    default="all", type=str,
                        help="string with comma separated list of samples to analyse: \
                        Run2012B_DoubleElectron, Run2012B_DoubleMuParked, Run2012C_DoubleElectron, \
                        Run2012C_DoubleMuParked, SMHiggsToZZTo4L, ZZTo2e2mu, ZZTo4e, ZZTo4mu")
    args_main = parser.parse_args()

    logger_main=set_up.set_up(args_main)


    ml_selection(args_main, logger_main)
