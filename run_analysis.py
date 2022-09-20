""" Running of the whole analysis. Various possible arguments
can be provided in order to customize the process.
"""

import argparse
import sys
import time

from Analysis.Definitions.eos_link_def import  EOS_LINK
from Analysis import set_up
from Analysis.Skimming import skim
from Analysis.Machine_Learning import  ml_training, ml_application, ml_selection
from Analysis.Plotting import make_plot, ml_plot
from Analysis.Histogramming import make_histo, ml_histo
from Analysis import download_dataset
from Analysis import fit_mass

def run_analysis (argv):
    """ Main function that runs the whole analysis.

    :param argv: Global configuration of the analysis.
    :type argv: list(str)
    """
    start_time = time.time()
    
    # Global configuration
    parser = argparse.ArgumentParser( description = "Analysis Tool" )
    
    parser.add_argument("-d", "--download",  nargs="?", default="",  const="Input",
                            type=str, help="enables the download of input data. \
                            If not specified otherwise the files are saved in the 'Input/' directory")

    parser.add_argument("-e", "--typeOfParallel", default="thread",   action="store_const",
                         const="process",  help="parallel type for the downloads: \
                         default is multi-thread, if activated is multi-process" )        

    parser.add_argument("-c", "--clearOutput",  nargs="?", default="", const="Output", type=str,
                            help="name of output folder to be deleted. \
                            If not specified otherwise the 'Output/' directory is deleted")
    
    parser.add_argument("-q", "--skim",   default=True,   action="store_const",
                            const=False, help="disables the skimming step") 

    parser.add_argument("-r", "--range",  nargs="?", default=0, const=10000000, type=int,
                            help="number of events on which the analysis \
                            is ran over (does not work in parallel)")
    
    parser.add_argument("-p", "--parallel",   default=True,   action="store_const",
                            const=False, help="disables running in parallel")
    
    parser.add_argument("-n", "--nWorkers",   default=0, type=int,   
                                help="number of workers for multi-threading" )
    
    parser.add_argument("-l", "--logLevel",   default=20, type=int,   
                            help="integer representing the level of the logger:\
                            DEBUG=10, INFO = 20, WARNING = 30, ERROR = 40" )
    
    parser.add_argument("-f", "--finalState",   default="all", type=str,   
                            help="comma separated list of the final states to analyse: \
                            FourMuons,FourElectrons,TwoMuonsTwoElectrons" ) 
    
    parser.add_argument("-m", "--ml", default=True,   action="store_const", const=False,
                            help="disables machine learning algorithm")
    
    parser.add_argument("-a", "--algorithmMLVar",     default="tot" , type=str,
                            help="name of the set of variables to be used in the ML \
                            algorithm defined 'variables_ml_def.py': tot, part, higgs")
    
    parser.add_argument("-i", "--invariantMassFit", default=True,   
                            action="store_const", const=False,
                            help="disables fit of the Higgs mass")
    
    parser.add_argument("-g", "--graphPlots",   default=True,
                            action="store_const",     const=False,
                            help="disables the graphing of the distribution plots")
    
    parser.add_argument("-t", "--typeDistribution",   default="all", type=str,   
                            help="comma separated list of the type of distributions to plot: \
                            data, background, signal, sig_bkg_normalized, total" )
    
    parser.add_argument("-s", "--sample",    default="all", type=str,
                            help="string with comma separated list of samples to analyse: \
                            Run2012B_DoubleElectron, Run2012B_DoubleMuParked, Run2012C_DoubleElectron, \
                            Run2012C_DoubleMuParked, SMHiggsToZZTo4L, ZZTo2e2mu, ZZTo4e, ZZTo4mu")
    
    parser.add_argument("-v", "--variableDistribution",    default="all", type=str,
                            help="string with comma separated list of the variables to plot. \
                            The complete list is defined in 'variables_def.py'")   
     
    parser.add_argument("-b", "--basePath",  nargs="?", default="Input",  const=EOS_LINK,
                            type=str, help="base path where to find the input data. \
                            If enabled it automatically gets the input data from EOS \
                            unless a local directory is specified")
    
    parser.add_argument("-o", "--output",     default="Output", type=str,
                            help="name of the output directory")
    
    args_global = parser.parse_args()
       
    logger_global=set_up.set_up(args_global)
    
    if args_global.download != "":
        download_dataset.download(args_global, logger_global)

    if args_global.skim:
        skim.skim(args_global, logger_global)
    
    if args_global.ml:
        ml_training.ml_training(args_global, logger_global)
        ml_application.ml_application(args_global, logger_global)
        ml_selection.ml_selection(args_global, logger_global)
        ml_histo.ml_histo(args_global, logger_global)
        ml_plot.ml_plot(args_global, logger_global)

    if args_global.graphPlots:
        make_histo.make_histo(args_global, logger_global)
        make_plot.make_plot(args_global, logger_global)
        
    if args_global.invariantMassFit:
        fit_mass.fit_mass(args_global, logger_global)

    logger_global.info(">>> Execution time: %s s \n", (time.time() - start_time))

    
if __name__ == "__main__":

    run_analysis(sys.argv[1:])
