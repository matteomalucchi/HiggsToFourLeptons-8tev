import os 
import sys
import ROOT

from skimming import skim
from plotting import make_plot, ml_plot
from histogramming import make_histo, ml_histo
from machine_learning import  ml_training, ml_application, ml_selections



'''files = [#"skim",
         #"machine_learning/ml_training",
         #"ml_application",
         #"machine_learning/ml_histo",
         #"machine_learning/ml_plot",
         "ml/ml_selections",
         "make_histo",
         "make_plot"
         ]
for file in files:
    print(f"\n _________________ Process {file}.py _________________")
    os.system(f"python {file}.py")
'''

def main (argv):
    ml_histo.main()


if __name__ == "__main__":

    main( sys.argv[1:] )


