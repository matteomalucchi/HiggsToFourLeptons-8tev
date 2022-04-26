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

import time
import os

import ROOT

import skim_tools
from variables_def import  BASE_PATH, SAMPLES, VARIABLES_FEATURES

def main():
    """Main function of the skimming step
    
    The function loops over the datasets and distinguishes the possible
    final states. It creates for each one of them a RDataFrame which allows 
    to apply cuts and define new useful abservables.
    """

    """Enamble multi-threading
    """
    ROOT.ROOT.EnableImplicitMT()
    thread_size = ROOT.ROOT.GetThreadPoolSize()
    print(">>> Thread pool size for parallel processing: {}".format(thread_size))

    """Loop over the various samples
    """
    for sample_name, final_states in SAMPLES.items():
        rdf = ROOT.RDataFrame("Events", BASE_PATH + sample_name +".root")

        """Loop over the possible final states
        """
        for final_state in final_states:
            print(">>> Process sample: {} and final state {}".format(sample_name, final_state))
            start_time = time.time()

            rdf2 = skim_tools.EventSelection(rdf, final_state)
            rdf3 = skim_tools.FourVec(rdf2, final_state)
            rdf4 = skim_tools.OrderFourVec(rdf3, final_state)
            rdf5 = skim_tools.DefMassPt(rdf4)
            rdf6 = skim_tools.FourvecBoost(rdf5)
            rdf7 = skim_tools.DefAngles(rdf6)
            rdf_final = skim_tools.AddEventWeight(rdf7, sample_name)
            
            report = rdf_final.Report()
            rdf_final.Snapshot("Events", "skim_data/" + sample_name +\
                               final_state + "Skim.root", VARIABLES_FEATURES.keys())
            #report.Print()
            print("Execution time: %s s" %(time.time() - start_time))
            #print(rdf_final.GetColumnNames())

        
if __name__ == "__main__":
    main()