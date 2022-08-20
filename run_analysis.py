import argparse
import os 
import sys
import ROOT

from skimming import skim
from machine_learning import  ml_training, ml_application, ml_selections
from plotting import make_plot, ml_plot
from histogramming import make_histo, ml_histo



def main ():
    
    
    # global configuration
    parser = argparse.ArgumentParser( description = 'Analysis Tool' )
    parser.add_argument('-n', '--nWorkers',   default=0,                                 type=int,   help='number of workers' )  
    parser.add_argument('-p', '--parallel',   default=False,   action='store_const',     const=True, help='enables running in parallel')
    parser.add_argument('-c', '--configfile', default="Configurations/HZZConfiguration.py", type=str,   help='files to be analysed')
    parser.add_argument('-s', '--samples',    default=""                               , type=str,   help='string with comma separated list of samples to analyse')
    parser.add_argument('-o', '--output',     default=""                               , type=str,   help='name of the output directory')
    parser.add_argument('-m', '--mlVariables',     default="tot"                               , type=str,   help='name of the set of variables to be used in the ML algorithm')
    args = parser.parse_args()
    
    
    #skim.main(args)
    ml_training.main(args)
    #ml_application.main()


if __name__ == "__main__":
    main()
    #main( sys.argv[1:] )


