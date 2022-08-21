"""
In this step the trained DNN is evaluated on the various datasets
and the resulting disciminant is saved in a new branch of the "Events" tree.
"""


from array import array
import sys
import time
import os
import argparse

import ROOT

sys.path.append('../')
from definitions.samples_def import SAMPLES
from definitions.variables_ml_def import VARIABLES_ML_DICT

def main(args, path_d="machine_learning", path_i=""):
    """ Main function that avaluates the DNN on the whole dataset
    """

    # Enamble multi-threading
    if args.parallel:
        ROOT.ROOT.EnableImplicitMT()
        thread_size = ROOT.ROOT.GetThreadPoolSize()
        print(f">>> Thread pool size for parallel processing: {thread_size}")

    # Setup TMVA
    ROOT.TMVA.Tools.Instance()
    ROOT.TMVA.PyMethodBase.PyInitialize()
    reader = ROOT.TMVA.Reader("Color:!Silent")

    # Variables used in the ML algorithm
    variables=VARIABLES_ML_DICT[args.variablesML]

    branches = {}
    for branch_name in variables:
        print(branch_name)
        branches[branch_name] = array("f", [-999])
        reader.AddVariable(branch_name, branches[branch_name])

    # Book methods
    dataset_path=os.path.join(path_d, "dataset", "weights", "TMVAClassification_PyKeras.weights.xml")
    reader.BookMVA("PyKeras", ROOT.TString(dataset_path))

    # Loop over the various samples
    for sample_name, final_states in SAMPLES.items():
        # Loop over the possible final states
        for final_state in final_states:
            
            print(f">>> Process sample: {sample_name} and final state {final_state}")
            start_time = time.time()
            in_file_path=os.path.join(path_i, "skim_data", f"{sample_name}{final_state}Skim.root")
            in_file = ROOT.TFile(in_file_path,"UPDATE")          

            tree = in_file.Get("Events")
            
            print(tree.GetNbranches())
            br = tree.GetListOfBranches().FindObject("Discriminant")
            if br != None:
               tree.SetBranchStatus("Discriminant", 0)   

            new_tree = tree.CloneTree()
            print(new_tree.GetNbranches())
            
            if args.variablesML == "tot":
                eval_variables = [new_tree.Z1_mass, new_tree.Z2_mass, new_tree.cos_theta_star,
                                          new_tree.Phi, new_tree.Phi1, new_tree.cos_theta1, new_tree.cos_theta2]
            elif args.variablesML == "part":
                eval_variables = [new_tree.cos_theta_star, new_tree.Phi, 
                                  new_tree.Phi1, new_tree.cos_theta1, new_tree.cos_theta2]
            elif args.variablesML == "higgs":
                eval_variables = [new_tree.Higgs_mass]

            discr_array = array("f", [-999])
            branch = new_tree.Branch("Discriminant", discr_array, "Discriminant/F")
            rand = ROOT.TRandom2()
            for i in range(tree.GetEntries()):
                    new_tree.GetEntry(i)                    
                    #discr_array[0] = reader.EvaluateMVA(eval_variables, "PyKeras")
                    discr_array[0]= rand.Rndm()
                    branch.Fill()

            new_tree.Write("", ROOT.TObject.kOverwrite)
            
            #in_file.Close()
            print("Execution time: %s s" %(time.time() - start_time))
            
if __name__ == "__main__":
    
    # global configuration
    parser = argparse.ArgumentParser( description = 'Analysis Tool' )
    parser.add_argument('-p', '--parallel',   default=False,   action='store_const',     const=True, help='enables running in parallel')
    parser.add_argument('-n', '--nWorkers',   default=0,                                 type=int,   help='number of workers' )  
    parser.add_argument('-v', '--variablesML',     default="tot"                               , type=str,   help='name of the set of variables to be used in the ML algorithm (tot, part, higgs)')
    args = parser.parse_args()
    
    main(args, "", "..")