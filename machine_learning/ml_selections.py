""" 
This step consists in the selection of the events for which
the discriminant created by the DNN is above the 0.5 threshold.
A new set of files is created for this purpose.
"""

import time
import os
import sys
import ROOT

sys.path.append('../')
from definitions.samples_def import  SAMPLES
from definitions.variables_def import VARIABLES_COMPLETE

def DiscriminantSelection(rdf):
    return rdf.Filter("Discriminant>0.1",
                      "Select only events with above threshold discriminat")


def main():
    """Main function for the selection of the events for which
    the discriminant created by the DNN is above the 0.5 threshold
    """

    """Enamble multi-threading
    """
    ROOT.ROOT.EnableImplicitMT()
    thread_size = ROOT.ROOT.GetThreadPoolSize()
    print(">>> Thread pool size for parallel processing: {}".format(thread_size))

    """Loop over the various samples and final states
    """
    for sample_name, final_states in SAMPLES.items():
        for final_state in final_states:
            print(">>> Process sample: {} and final state {}".format(sample_name, final_state))
            rdf = ROOT.RDataFrame("Events", f"../skim_data/{sample_name}{final_state}Skim.root")
            start_time = time.time()

            rdf_final = DiscriminantSelection(rdf)

            report = rdf_final.Report()
            report.Print()
            #print(rdf_final.GetColumnNames())
            #print("")   
                     
            """Create the directory and save the selected samples.
            """
            """file_name =f"{sample_name}{final_state}MLSelection.root"
            dir_name = "ML_selection_data"
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
                print(f"Directory {dir_name} Created")
            complete_name = os.path.join(dir_name, file_name)"""
            
            option = ROOT.RDF.RSnapshotOptions("UPDATE", ROOT.kZLIB, 1, 0, 99, False, True)
            rdf_final.Snapshot("EventsDNNSelection", f"../skim_data/{sample_name}{final_state}Skim.root", VARIABLES_COMPLETE.keys(), option)

            print("Execution time: %s s" %(time.time() - start_time))

        
if __name__ == "__main__":
    main()