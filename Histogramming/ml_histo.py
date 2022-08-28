"""
In this step 2D histograms of Higgs_mass vs Discriminant
are created, one for the combination of all the simulated background,
one for all the simulated signal and one for each possible final state
of the data.
"""

import sys
import os
import argparse
import logging

import ROOT

sys.path.append('../')
from Definitions.samples_def import SAMPLES
from Histogramming import histogramming_functions


def ml_histo(args, logger, path = ""):
    """Main function of the histogramming step that plots Higgs_mass vs DNN Discriminant.
    The function produces the required histogram for the final plotting step.

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
    outfile_path = os.path.join(dir_name, "Histograms_discriminant.root")
    outfile = ROOT.TFile(outfile_path, "RECREATE")

    sig_chain= ROOT.TChain("Events")
    bkg_chain= ROOT.TChain("Events")
    data_el_chain= ROOT.TChain("Events")
    data_mu_chain= ROOT.TChain("Events")
    data_elmu_chain= ROOT.TChain("Events")

    for sample_name, final_states in SAMPLES.items():
        for final_state in final_states:
            # Check if the final state is one of those requested by the user
            if final_state not in args.finalState and args.finalState != "all":
                continue            
            logger.info(">>> Process sample %s and final state %s", sample_name, final_state)

            # Get the input file name
            file_name = os.path.join(path, args.output, "Skim_data", 
                                     f"{sample_name}{final_state}Skim.root")
 
            # Check if file exists or not 
            try:
                if not os.path.exists(file_name):
                    raise FileNotFoundError
            except FileNotFoundError as not_fund_err:
                logger.debug("Sample %s final state %s: File %s can't be found %s",
                                sample_name, final_state, file_name, not_fund_err,  stack_info=True)
                continue
            
            if sample_name.startswith("SM"):
                sig_chain.Add(file_name)

            elif sample_name.startswith("ZZ"):
                bkg_chain.Add(file_name)

            elif sample_name.startswith("Run"):
                if final_state == "FourElectrons":
                    data_el_chain.Add(file_name)
                elif final_state == "FourMuons":
                    data_mu_chain.Add(file_name)
                elif final_state == "TwoMuonsTwoElectrons":
                    data_elmu_chain.Add(file_name)

    sig_rdf = ROOT.ROOT.RDataFrame(sig_chain)
    bkg_rdf = ROOT.RDataFrame(bkg_chain)
    data_el_rdf = ROOT.RDataFrame(data_el_chain)
    data_mu_rdf = ROOT.RDataFrame(data_mu_chain)
    data_elmu_rdf = ROOT.RDataFrame(data_elmu_chain)

    rdfs = {
        "signal" : sig_rdf,
        "background" : bkg_rdf,
        "data_el" : data_el_rdf,
        "data_mu" : data_mu_rdf,
        "data_elmu" :  data_elmu_rdf
    }

    histos = {}
    variables = ["Higgs_mass", "Discriminant"]
    ranges_x = [40, 100., 180.]
    ranges_y = [40, -0.03, 1]
    for dataset, rdf in rdfs.items():
        logger.info(">>> Process sample: %s", dataset)
        try:
            histos[dataset] = histogramming_functions.book_histogram_2d(dataset,
                                                    rdf, variables, ranges_x, ranges_y)
            histogramming_functions.write_histogram(histos[dataset], dataset)
        except TypeError:
            logger.debug("Dataset %s is empty", dataset)
        
    outfile.Close()


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

    ml_histo(args_main, logger_main, "..")
