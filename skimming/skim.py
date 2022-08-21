""" 
Implementation of the skimming process 
 
This consists in reducing the initial samples to a dataset 
specific for this analysis. The skimming removes all events 
which are not of interest for the reconstruction of Z bosons
from combinations of leptons, which may originate from the 
decay of a Higgs boson. Furthermore, all the variables used 
later on are defined. This includes mass and Pt of Z and Higgs 
bosons, as well as five dacay angles defined in [Phys.Rev.D86:095031,2012] 
which are later used for a machine learning algorithm.
"""

import argparse
import time
import os
import sys
import ROOT

sys.path.append('../')

from skimming import skim_tools

from definitions.base_path_def import  BASE_PATH
from definitions.samples_def import  SAMPLES
from definitions.variables_def import  VARIABLES


def main(args, path_sf="skimming", path_sd=""):
    """Main function of the skimming step
    
    The function loops over the datasets and distinguishes the possible
    final states. It creates for each one of them a RDataFrame which allows 
    to apply cuts and define new useful observables.
    """
    
    skim_func_path = os.path.join(path_sf, "skim_functions.h")

    ROOT.gInterpreter.ProcessLine(f'#include "{skim_func_path}"' )

    #Enamble multi-threading
    if args.parallel:
        ROOT.ROOT.EnableImplicitMT(args.nWorkers)
        thread_size = ROOT.ROOT.GetThreadPoolSize()
        print(">>> Thread pool size for parallel processing: {}".format(thread_size))

    #Loop over the various samples
    for sample_name, final_states in SAMPLES.items():
        infile_path = os.path.join( BASE_PATH, f"{sample_name}.root")
        rdf = ROOT.RDataFrame("Events", infile_path)
        
        if args.range != 0:
            rdf=rdf.Range(args.range)
            
        """Loop over the possible final states
        """
        for final_state in final_states:
            print("\n>>> Process sample: {} and final state {}".format(sample_name, final_state))
            start_time = time.time()

            rdf2 = skim_tools.EventSelection(rdf, final_state)
            rdf3 = skim_tools.FourVec(rdf2, final_state)
            rdf4 = skim_tools.OrderFourVec(rdf3, final_state)
            rdf5 = skim_tools.DefMassPt(rdf4)
            rdf6 = skim_tools.FourvecBoost(rdf5)
            rdf7 = skim_tools.DefAngles(rdf6)
            rdf_final = skim_tools.AddEventWeight(rdf7, sample_name)
            #print(rdf_final.GetColumnNames())

            report = rdf_final.Report()
            report.Print()
            #print(rdf_final.GetColumnNames())
            #print("")   
                     
            """Create the directory and save the skimmed samples.
            """
            file_name =f"{sample_name}{final_state}Skim.root"
            dir_name = os.path.join(path_sd, "skim_data")
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
                print("Directory " , dir_name ,  " Created ")
            complete_name = os.path.join(dir_name, file_name)

            rdf_final.Snapshot("Events", complete_name, VARIABLES.keys())

            print("Execution time: %s s" %(time.time() - start_time))

        
if __name__ == "__main__":
    
    # global configuration
    parser = argparse.ArgumentParser( description = 'Analysis Tool' )
    parser.add_argument('-r', '--range',  nargs='?', default=0, const=10000000, type=int, help='run the analysis only on a finite range of events')
    parser.add_argument('-p', '--parallel',   default=False,   action='store_const',     const=True, help='enables running in parallel')
    parser.add_argument('-n', '--nWorkers',   default=0,                                 type=int,   help='number of workers' )  
    parser.add_argument('-o', '--output',     default=""                               , type=str,   help='name of the output directory')
    args = parser.parse_args()
    
    main(args, "", "..")