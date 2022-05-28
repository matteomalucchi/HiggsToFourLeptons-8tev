import os 
import sys
import ROOT

from skimming import skim
from plotting import make_plot, ml_plot
from histogramming import make_histo, ml_histo
from machine_learning import  ml_training, ml_application, ml_selections



def main (argv):
    
    
    """Enamble multi-threading
    """
    ROOT.ROOT.EnableImplicitMT()
    thread_size = ROOT.ROOT.GetThreadPoolSize()
    print(">>> Thread pool size for parallel processing: {}".format(thread_size))
    
    
    ml_histo.main()


if __name__ == "__main__":

    main( sys.argv[1:] )


