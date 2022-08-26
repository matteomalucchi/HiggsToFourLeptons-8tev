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
    :param path_sd: Optional base path to find the directory ``skim_data/``.
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
            logger.info(">>> Process sample: %s and final state %s", sample_name, final_state)
            file_name=os.path.join(path_sd, args.output, "skim_data",
                                f"{sample_name}{final_state}Skim.root")
            rdf = ROOT.RDataFrame("Events", file_name)
            start_time = time.time()

            rdf_final = rdf.Filter("Discriminant>0.5",
                                    "Select only events with above threshold discriminat")

            report = rdf_final.Report()
            report.Print()
            logger.debug("%s\n", rdf_final.GetColumnNames())


            option = ROOT.RDF.RSnapshotOptions("UPDATE", ROOT.kZLIB, 1, 0, 99, False, True)
            rdf_final.Snapshot("EventsDNNSelection", file_name, VARIABLES_COMPLETE.keys(), option)

            logger.info(">>> Execution time: %s s \n", (time.time() - start_time))

if __name__ == "__main__":

    # General configuration
    parser = argparse.ArgumentParser( description = 'Analysis Tool' )
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

    ml_selection(args_main, logger_main, "..")
