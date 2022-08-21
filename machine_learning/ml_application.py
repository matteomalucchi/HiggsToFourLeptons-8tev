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
#from definitions.variables_ml_def import VARIABLES_TOT_ML as variables
from definitions.variables_ml_def import VARIABLES_ML_DICT

def main(args, path_o="machine_learning"):

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
    dataset_path=os.path.join(path_o, "dataset", "weights", "TMVAClassification_PyKeras.weights.xml")
    reader.BookMVA("PyKeras", ROOT.TString(dataset_path))

    # Loop over the various samples
    for sample_name, final_states in SAMPLES.items():
        
        # Loop over the possible final states
        for final_state in final_states:
            print(f">>> Process sample: {sample_name} and final state {final_state}")
            start_time = time.time()
            in_file_name = f"../skim_data/{sample_name}{final_state}Skim.root"
            in_file = ROOT.TFile(in_file_name,"UPDATE")          

            """file_name =f"{sample_name}{final_state}ML.root"
            dir_name = "ML_data"
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
                print("Directory " , dir_name ,  " Created ")
            out_file_name = os.path.join(dir_name, file_name)
            out_file = ROOT.TFile(out_file_name,"RECREATE")"""

            tree = in_file.Get("Events")
            #tree = tree.Clone()

            discr_array = array("f", [-999])
            branch = tree.Branch("Discriminant", discr_array, "Discriminant/F")
            rand = ROOT.TRandom2()
            for i in range(tree.GetEntries()):
                    tree.GetEntry(i)
                    '''discr_array[0] = reader.EvaluateMVA([tree.Z1_mass, tree.Z2_mass, tree.cos_theta_star,
                                            tree.Phi, tree.Phi1, tree.cos_theta1, tree.cos_theta2], "PyKeras")'''
                    discr_array[0]= rand.Rndm()
                    branch.Fill()

            tree.Write("", ROOT.TObject.kOverwrite)
            #out_file.Close()

            print("Execution time: %s s" %(time.time() - start_time))
            
if __name__ == "__main__":
    main()