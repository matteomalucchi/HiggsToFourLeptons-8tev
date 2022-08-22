import argparse
import os 
import sys
import ROOT

from skimming import skim
from machine_learning import  ml_training, ml_application, ml_selections
from plotting import make_plot, ml_plot
from histogramming import make_histo, ml_histo
import fit_mass



def main (argv):
    
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
    parser.add_argument('-c', '--configfile', default="Configurations/HZZConfiguration.py", type=str,   help='files to be analysed')
    parser.add_argument('-s', '--samples',    default="", type=str,   help='string with comma separated list of samples to analyse')
    parser.add_argument('-o', '--output',     default="", type=str,   help='name of the output directory')
    args = parser.parse_args()
    
    
    #skim.main(args)
    
    if args.ml:
        #ml_training.main(args)
        ml_application.main(args)
        ml_selections.main(args)
        #ml_histo.main(args)
        #ml_plot.main(args)
        
    if args.fitMass:
        fit_mass.main(args)
        
    make_histo.main(args)
    make_plot.main(args)


if __name__ == "__main__":
    main( sys.argv[1:] )


