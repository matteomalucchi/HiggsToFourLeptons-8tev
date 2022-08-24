import argparse
import logging
import os 
import sys

from skimming import skim
from machine_learning import  ml_training, ml_application, ml_selection
from plotting import make_plot, ml_plot
from histogramming import make_histo, ml_histo
import fit_mass


def run_analysis (argv):
    
    # global configuration
    parser = argparse.ArgumentParser( description = 'Analysis Tool' )
    parser.add_argument('-r', '--range',  nargs='?', default=0, const=10000000, type=int, 
                            help='run the analysis only on a finite range of events (does not work in parallel)')
    parser.add_argument('-p', '--parallel',   default=False,   action='store_const',     const=True, help='enables running in parallel')
    parser.add_argument('-n', '--nWorkers',   default=0, type=int,   help='number of workers' )  
    parser.add_argument('-m', '--ml', default=False,   action='store_const', const=True,   help='enables machine learning algorithm')
    parser.add_argument('-v', '--variablesML',     default="tot" , type=str,   
                            help='name of the set of variables to be used in the ML algorithm defined "variables_ml_def.py" (tot, part, higgs)')
    parser.add_argument('-f', '--fitMass', default=False,   action='store_const', const=True,   help='enables fit of the Higgs mass')
    parser.add_argument('-o', '--output',     default="Output", type=str,   help='name of the output directory')
    parser.add_argument('-c', '--configfile', default="Configurations/HZZConfiguration.py", type=str,   help='files to be analysed')
    parser.add_argument('-s', '--samples',    default="", type=str,   help='string with comma separated list of samples to analyse')
    args = parser.parse_args()
    
    # Create the directory to save the outputs if doesn't already exist
    if not os.path.exists(args.output):
        os.makedirs(args.output)
        logger.debug("Directory " , args.output ,  " Created ")
    
    # Create and configure logger     
    logging.basicConfig( format='\n%(asctime)s %(message)s') 
    # Create an object 
    logger=logging.getLogger() 
    # Set the threshold of logger
    logger.setLevel(logging.INFO) 
    
    skim.skim(args, logger)
    
    if args.ml:
        ml_training.ml_training(args, logger)
        ml_application.ml_application(args, logger)
        ml_selection.ml_selection(args, logger)
        ml_histo.ml_histo(args, logger)
        ml_plot.ml_plot(args, logger)
        
    if args.fitMass:
        fit_mass.fit_mass(args, logger)
        
    make_histo.make_histo(args, logger)
    make_plot.make_plot(args, logger)


if __name__ == "__main__":
    # Create and configure logger 
    logging.basicConfig( format='\n%(asctime)s %(message)s') 
    # Create an object 
    logger=logging.getLogger() 
    # Set the threshold of logger
    logger.setLevel(logging.INFO)     run_analysis( sys.argv[1:] )


