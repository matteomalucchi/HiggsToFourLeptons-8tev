"""
Running of the whole analysis. Various possible arguments
can be provided in order to customize the process.
"""

import argparse
import logging
import os
import sys
import time


from Skimming import skim
from Machine_Learning import  ml_training, ml_application, ml_selection
from Plotting import make_plot, ml_plot
from Histogramming import make_histo, ml_histo
import fit_mass


def run_analysis (argv):
    """ Main function that runs in order the whole analysis.

    :param argv: Global configuration of the analysis.
    :type argv: list(str)
    """
    start_time = time.time()
    
    # Global configuration
    parser = argparse.ArgumentParser( description = 'Analysis Tool' )
    parser.add_argument('-r', '--range',  nargs='?', default=0, const=10000000, type=int,
                            help='run the analysis only on a finite \
                                range of events (does not work in parallel)')
    parser.add_argument('-p', '--parallel',   default=False,   action='store_const',
                        const=True, help='enables running in parallel')
    parser.add_argument('-n', '--nWorkers',   default=0, type=int,   help='number of workers' )
    parser.add_argument('-l', '--logLevel',   default=20, type=int,   
                            help='integer representing the level of the logger:\
                             DEBUG=10, INFO = 20, WARNING = 30, ERROR = 40' )
    parser.add_argument('-m', '--ml', default=False,   action='store_const', const=True,
                        help='enables machine learning algorithm')
    parser.add_argument('-v', '--variablesML',     default="tot" , type=str,
                            help='name of the set of variables to be used in the ML \
                            algorithm defined "variables_ml_def.py" (tot, part, higgs)')
    parser.add_argument('-f', '--fitMass', default=False,   action='store_const', const=True,
                        help='enables fit of the Higgs mass')
    parser.add_argument('-d', '--distribution',   default=False,
                            action='store_const',     const=True,
                            help='enables the histogramming and \
                                plotting of the variable distributions')
    parser.add_argument('-t', '--typeDistribution',   default="all", type=str,   
                            help='Type of distributions to plot: \
                            all, data, background, signal, sig_bkg_normalized, total' )
    parser.add_argument('-o', '--output',     default="Output", type=str,
                            help='name of the output directory')

    parser.add_argument('-c', '--configfile', default="Configurations/HZZConfiguration.py",
                        type=str,   help='files to be analysed')
    parser.add_argument('-s', '--samples',    default="", type=str,
                        help='string with comma separated list of samples to analyse')
    args_global = parser.parse_args()

    # Create and configure logger
    logging.basicConfig( format='\n%(asctime)s - %(filename)s - %(message)s')
    # Create an object
    logger_global=logging.getLogger()
    # Set the threshold of logger_global
    logger_global.setLevel(args_global.logLevel)

    # Create the directory to save the outputs if doesn't already exist
    try:
        os.makedirs(args_global.output)
        logger_global.debug("Directory %s/ Created", args_global.output)
    except FileExistsError:
        logger_global.debug("The directory %s/ already exists", args_global.output)

    skim.skim(args_global, logger_global)
    
    if args_global.ml:
        ml_training.ml_training(args_global, logger_global)
        ml_application.ml_application(args_global, logger_global)
        ml_selection.ml_selection(args_global, logger_global)
        ml_histo.ml_histo(args_global, logger_global)
        ml_plot.ml_plot(args_global, logger_global)

    if args_global.fitMass:
        fit_mass.fit_mass(args_global, logger_global)

    if args_global.distribution:
        make_histo.make_histo(args_global, logger_global)
        make_plot.make_plot(args_global, logger_global)

    logger_global.info(">>> Execution time: %s s \n", (time.time() - start_time))


if __name__ == "__main__":

    run_analysis( sys.argv[1:] )
