"""
Running of the whole analysis. Various possible arguments
can be provided in order to customize the process.
"""

import argparse
import logging
import os
from re import A
import sys
import time
import shutil


from Skimming import skim
from Machine_Learning import  ml_training, ml_application, ml_selection
from Plotting import make_plot, ml_plot
from Histogramming import make_histo, ml_histo
import fit_mass

import set_up

def run_analysis (argv):
    """ Main function that runs in order the whole analysis.

    :param argv: Global configuration of the analysis.
    :type argv: list(str)
    """
    start_time = time.time()
    
    # Global configuration
    parser = argparse.ArgumentParser( description = 'Analysis Tool' )
    
    parser.add_argument('-c', '--clearOutput',  nargs='?', default="", const="Output", type=str,
                            help='name of output folder to be deleted')
    
    parser.add_argument('-r', '--range',  nargs='?', default=0, const=10000000, type=int,
                            help='number of events on which the analysis \
                            is ran over (does not work in parallel)')
    
    parser.add_argument('-p', '--parallel',   default=True,   action='store_const',
                        const=False, help='disables running in parallel')
    
    parser.add_argument('-n', '--nWorkers',   default=0, type=int,   help='number of workers' )
    
    parser.add_argument('-l', '--logLevel',   default=20, type=int,   
                            help='integer representing the level of the logger:\
                             DEBUG=10, INFO = 20, WARNING = 30, ERROR = 40' )
    
    parser.add_argument('-f', '--finalState',   default="all", type=str,   
                            help='comma separated list of the final states to analyse: \
                            FourMuons,FourElectrons,TwoMuonsTwoElectrons' ) 
    
    parser.add_argument('-m', '--ml', default=True,   action='store_const', const=False,
                        help='disables machine learning algorithm')
    
    parser.add_argument('-v', '--variablesML',     default="tot" , type=str,
                            help='name of the set of variables to be used in the ML \
                            algorithm defined "variables_ml_def.py" (tot, part, higgs)')#
    
    parser.add_argument('-i', '--invariantMassFit', default=True,   action='store_const', const=False,
                        help='disables fit of the Higgs mass')
    
    parser.add_argument('-d', '--distribution',   default=True,
                            action='store_const',     const=False,
                            help='disables the histogramming and \
                                plotting of the variable distributions')
    
    parser.add_argument('-t', '--typeDistribution',   default="all", type=str,   
                            help='comma separated list of the type of distributions to plot: \
                            data,background,signal,sig_bkg_normalized,total' )
    
    parser.add_argument('-s', '--sample',    default="all", type=str,
                        help='string with comma separated list of samples to analyse')
    
    parser.add_argument('-o', '--output',     default="Output", type=str,
                            help='name of the output directory')

    
    #parser.add_argument('-c', '--configfile', default="Configurations/HZZConfiguration.py",
     #                   type=str,   help='files to be analysed')
    
    
    args_global = parser.parse_args()
    
    
    """# Create and configure logger
    logging.basicConfig( format='\n%(asctime)s - %(filename)s - %(message)s')
    # Create an object
    logger_global=logging.getLogger() """
       
    logger_global=set_up.set_up(args_global)
    logger_global.info("a")
    """  
    # Check if logLevel valid
    try:
        if args_global.logLevel not in [10, 20, 30, 40]:
            raise argparse.ArgumentTypeError(f"the value for logLevel {args_global.logLevel} is invalid: it must be either 10, 20, 30 or 40")
    except argparse.ArgumentTypeError as arg_err:
        logger_global.exception("%s \n logLevel is set to 20 \n", arg_err, stack_info=True)
        args_global.logLevel = 20
        
    # Set the threshold of logger_global
    logger_global.setLevel(args_global.logLevel)   
    
    
    # Check if typeDistribution is valid
    try:
        if not any(type_distribution in args_global.typeDistribution.split(",") for type_distribution 
               in ["all", "data", "background", "signal", "sig_bkg_normalized", "total"]):
            raise argparse.ArgumentTypeError(f"the type of distribution {args_global.typeDistribution} is invalid: \
                it must be either all,data,background,signal,sig_bkg_normalized,total")
    except argparse.ArgumentTypeError as arg_err:
        logger_global.exception("%s \n typeDistribution is set to all \n", arg_err, stack_info=True)
        args_global.typeDistribution = "all"       
    
    
    # Check if finalState is valid
    try:
        if not any(final_state in args_global.finalState.split(",") for final_state 
               in ["all", "FourMuons", "FourElectrons", "TwoMuonsTwoElectrons"]):
            raise argparse.ArgumentTypeError(f"the final state {args_global.finalState} is invalid: \
                it must be either all,FourMuons,FourElectrons,TwoMuonsTwoElectrons")
    except argparse.ArgumentTypeError as arg_err:
        logger_global.exception("%s \n finalState is set to all \n", arg_err, stack_info=True)
        args_global.finalState = "all"  
        
    
    # Check if variablesML is valid
    try:
        if not any(var_ml in args_global.variablesML for var_ml 
               in ["tot", "part", "higgs"]):
            raise argparse.ArgumentTypeError(f"the set of ML variables {args_global.variablesML} is invalid: \
                it must be either tot, part, higgs")
    except argparse.ArgumentTypeError as arg_err:
        logger_global.exception("%s \n variablesML is set to tot \n", arg_err, stack_info=True)
        args_global.variablesML = "tot"    

    # Check if sample is valid
    try:
        if not any(sample in args_global.sample.split(",") for sample 
               in ["all", "Run2012B_DoubleElectron", "Run2012B_DoubleMuParked", "Run2012C_DoubleElectron", 
                   "Run2012C_DoubleMuParked", "SMHiggsToZZTo4L", "ZZTo2e2mu", "ZZTo4e", "ZZTo4mu"]):
            raise argparse.ArgumentTypeError(f"the sample {args_global.sample} is invalid: \
                it must be either all, Run2012B_DoubleElectron, Run2012B_DoubleMuParked, Run2012C_DoubleElectron, \
                Run2012C_DoubleMuParked, SMHiggsToZZTo4L, ZZTo2e2mu, ZZTo4e, ZZTo4mu")
    except argparse.ArgumentTypeError as arg_err:
        logger_global.exception("%s \n sample is set to all \n", arg_err, stack_info=True)
        args_global.sample = "all"    
        
        
    # Clear the output folder
    if args_global.clearOutput != "":
        try:
            shutil.rmtree(args_global.clearOutput)
        except OSError as os_err:
            logger_global.debug("ERROR directory %s/ could not be deleted: \n %s", args_global.clearOutput, os_err)
        else:
            logger_global.debug("Directory %s/ has been succesfully deleted", args_global.clearOutput)


    # Create the directory to save the outputs if doesn't already exist
    try:
        os.makedirs(args_global.output)
        logger_global.debug("Directory %s/ Created", args_global.output)
    except FileExistsError:
        logger_global.debug("The directory %s/ already exists", args_global.output)"""
        
    
    skim.skim(args_global, logger_global)
    
    if args_global.ml:
        ml_training.ml_training(args_global, logger_global)
        ml_application.ml_application(args_global, logger_global)
        ml_selection.ml_selection(args_global, logger_global)
        ml_histo.ml_histo(args_global, logger_global)
        ml_plot.ml_plot(args_global, logger_global)

    if args_global.distribution:
        make_histo.make_histo(args_global, logger_global)
        make_plot.make_plot(args_global, logger_global)
        
    if args_global.invMassFit:
        fit_mass.fit_mass(args_global, logger_global)

    logger_global.info(">>> Execution time: %s s \n", (time.time() - start_time))


if __name__ == "__main__":

    run_analysis( sys.argv[1:] )
