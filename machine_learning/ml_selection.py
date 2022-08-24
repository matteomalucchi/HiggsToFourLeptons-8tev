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
from definitions.samples_def import  SAMPLES
from definitions.variables_def import VARIABLES_COMPLETE


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
    
    logger.info(f">>> Executing {os.path.basename(__file__)}\n")

    # Enamble multi-threading
    if args.parallel:
        ROOT.ROOT.EnableImplicitMT()
        thread_size = ROOT.ROOT.GetThreadPoolSize()
        logger.info(f">>> Thread pool size for parallel processing: {thread_size}")

    #Loop over the various samples and final states
    for sample_name, final_states in SAMPLES.items():
        for final_state in final_states:
            logger.info(f">>> Process sample: {sample_name} and final state {final_state}")
            file_name=os.path.join(path_sd, args.output, "skim_data", f"{sample_name}{final_state}Skim.root")
            rdf = ROOT.RDataFrame("Events", file_name)
            start_time = time.time()

            rdf_final = rdf.Filter("Discriminant>0.5",
                                    "Select only events with above threshold discriminat")

            report = rdf_final.Report()
            report.Print()
            logger.debug(f"{rdf_final.GetColumnNames()}\n")
  
                                 
            option = ROOT.RDF.RSnapshotOptions("UPDATE", ROOT.kZLIB, 1, 0, 99, False, True)
            rdf_final.Snapshot("EventsDNNSelection", file_name, VARIABLES_COMPLETE.keys(), option)

            logger.info("Execution time: %s s" %(time.time() - start_time))

        
if __name__ == "__main__":
    
    # Create and configure logger 
    logging.basicConfig( format='\n%(asctime)s %(message)s') 
    # Create an object 
    logger=logging.getLogger() 
    # Set the threshold of logger
    logger.setLevel(logging.INFO)     
    # General configuration
    
    parser = argparse.ArgumentParser( description = 'Analysis Tool' )
    parser.add_argument('-p', '--parallel',   default=False,   action='store_const',     const=True, help='enables running in parallel')
    parser.add_argument('-n', '--nWorkers',   default=0,                                 type=int,   help='number of workers' )  
    parser.add_argument('-o', '--output',     default="Output", type=str,   help='name of the output directory')
    args = parser.parse_args()
    
    ml_selection(args, logger, "..")