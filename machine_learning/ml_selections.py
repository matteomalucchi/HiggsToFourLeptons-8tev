""" 
This step consists in the selection of the events for which
the discriminant created by the DNN is above the 0.5 threshold.
A new set of files is created for this purpose.
"""

import time
import os
import sys
import argparse

import ROOT

sys.path.append('../')
from definitions.samples_def import  SAMPLES
from definitions.variables_def import VARIABLES_COMPLETE

def DiscriminantSelection(rdf):
    return rdf.Filter("Discriminant>0.01",
                      "Select only events with above threshold discriminat")


def main(args, path_sd=""):
    """Main function for the selection of the events for which
    the discriminant created by the DNN is above the 0.5 threshold
    """
    
    print(f"\n>>> Executing {os.path.basename(__file__)}\n")

    # Enamble multi-threading
    if args.parallel:
        ROOT.ROOT.EnableImplicitMT()
        thread_size = ROOT.ROOT.GetThreadPoolSize()
        print(f">>> Thread pool size for parallel processing: {thread_size}")

    #Loop over the various samples and final states
    for sample_name, final_states in SAMPLES.items():
        for final_state in final_states:
            print(">>> Process sample: {} and final state {}".format(sample_name, final_state))
            file_name=os.path.join(path_sd,"skim_data", f"{sample_name}{final_state}Skim.root")
            rdf = ROOT.RDataFrame("Events", file_name)
            start_time = time.time()

            rdf_final = DiscriminantSelection(rdf)

            report = rdf_final.Report()
            report.Print()
            #print(rdf_final.GetColumnNames())
            #print("")   
                                 
            option = ROOT.RDF.RSnapshotOptions("UPDATE", ROOT.kZLIB, 1, 0, 99, False, True)
            rdf_final.Snapshot("EventsDNNSelection", file_name, VARIABLES_COMPLETE.keys(), option)

            print("Execution time: %s s" %(time.time() - start_time))

        
if __name__ == "__main__":
    
    # General configuration
    parser = argparse.ArgumentParser( description = 'Analysis Tool' )
    parser.add_argument('-p', '--parallel',   default=False,   action='store_const',     const=True, help='enables running in parallel')
    parser.add_argument('-n', '--nWorkers',   default=0,                                 type=int,   help='number of workers' )  
    args = parser.parse_args()
    
    main(args, "..")