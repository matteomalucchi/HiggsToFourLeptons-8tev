"""
In this step the trained DNN is evaluated on the various datasets
and the resulting disciminant is saved in a new branch of the "Events" tree.
"""


import ROOT
from array import array
import sys
import time
import os

sys.path.append('../')
from definitions.samples_def import SAMPLES
from definitions.variables_ml_def import VARIABLES_ML_DICT

def main(args, path_d="machine_learning", path_i=""):

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

            """file_name =f"{sample_name}{final_state}ML.root"
            dir_name = "ML_data"
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
                print("Directory " , dir_name ,  " Created ")
            out_file_name = os.path.join(dir_name, file_name)
            out_file = ROOT.TFile(out_file_name,"RECREATE")"""

            tree = in_file.Get("Events")
            #new_tree = tree.Clone()
            #in_file.Close()

            
            print(tree.GetNbranches())
            br = tree.GetListOfBranches().FindObject("Discriminant")
            if br != None:
               tree.SetBranchStatus("Discriminant", 0)
               #tree.SetBranchStatus("Discrminant", 1)
               
            #out_file_path=os.path.join(path_i, "skim_data", f"{sample_name}{final_state}Skim.root")

            #out_file = ROOT.TFile(in_file_path,"RECREATE")          

            new_tree = tree.CloneTree()
            
            print(new_tree.GetNbranches())
            
            
            #br = tree.GetListOfBranches().FindObject("Discriminant")
            '''if br != None:
                tree.GetListOfBranches().Remove(br)
                print("\n f \n")'''


            discr_array = array("f", [-999])
            branch = new_tree.Branch("Discriminant", discr_array, "Discriminant/F")
            rand = ROOT.TRandom2()
            for i in range(tree.GetEntries()):
                    new_tree.GetEntry(i)
                    
                    # qua devi modificare e mettere che è possiobile valutare solo su variabili part e higgs
                    
                    #discr_array[0] = reader.EvaluateMVA([tree.Z1_mass, tree.Z2_mass, tree.cos_theta_star,
                     #                     tree.Phi, tree.Phi1, tree.cos_theta1, tree.cos_theta2], "PyKeras")
                    discr_array[0]= rand.Rndm()
                    branch.Fill()

            new_tree.Write("", ROOT.TObject.kOverwrite)
            
            #in_file.Close()
            print("Execution time: %s s" %(time.time() - start_time))
            
if __name__ == "__main__":
    main()