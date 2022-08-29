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
from Definitions.samples_def import SAMPLES
from Definitions.variables_ml_def import VARIABLES_ML_DICT

import set_up

def ml_application(args, logger, path_d="", path_sd=""):
    """ Main function that avaluates the DNN on the whole dataset.

    :param args: Global configuration of the analysis.
    :type args: argparse.Namespace
    :param logger: Configurated logger for printing messages.
    :type logger: logging.RootLogger
    :param path_d: Optional base path where the ``dataset/`` directory can be found
    :type path_d: str
    :param path_sd: Optional base path to find the directory ``Skim_data/``.
    :type path_sd: str
    """

    logger.info(">>> Executing %s \n", os.path.basename(__file__))

    # Enamble multi-threading
    if args.parallel:
        ROOT.ROOT.EnableImplicitMT()
        thread_size = ROOT.ROOT.GetThreadPoolSize()
        logger.info(">>> Thread pool size for parallel processing: %s", thread_size)

    # Setup TMVA
    ROOT.TMVA.Tools.Instance()
    ROOT.TMVA.PyMethodBase.PyInitialize()
    reader = ROOT.TMVA.Reader("Color:!Silent")

    # Variables used in the ML algorithm
    variables=VARIABLES_ML_DICT[args.variablesML]

    branches = {}
    for branch_name in variables:
        logger.debug(branch_name)
        branches[branch_name] = array("f", [-999])
        reader.AddVariable(branch_name, branches[branch_name])

    # Book methods
    dataset_path=os.path.join(path_d, args.output, "ML_output",
                              "dataset", "weights", "TMVAClassification_PyKeras.weights.xml")
    reader.BookMVA("PyKeras", ROOT.TString(dataset_path))

    # Loop over the various samples
    for sample_name, final_states in SAMPLES.items():
        # Loop over the possible final states
        for final_state in final_states:
            # Check if the final state is one of those requested by the user
            if final_state not in args.finalState and args.finalState != "all":
                continue

            logger.info(">>> Process sample: %s and final state %s", sample_name, final_state)
            start_time = time.time()

            # Check if file exists or not
            try: 
                in_file_path=os.path.join(path_sd, args.output,
                                "Skim_data", f"{sample_name}{final_state}Skim.root")
                if not os.path.exists(in_file_path):
                    raise FileNotFoundError
            except FileNotFoundError as not_found_err:
                logger.debug("Sample %s final state %s: File %s can't be found %s",
                                sample_name, final_state, in_file_path, not_found_err,  stack_info=True)
                continue

            in_file = ROOT.TFile(in_file_path,"UPDATE")
            tree = in_file.Get("Events")
            
            br_discr = tree.GetListOfBranches().FindObject("Discriminant")
            if br_discr:
                logger.debug("Found preexisting branch Discriminant")                
                tree.SetBranchStatus("Discriminant", 0)
                logger.debug("Preexisting branch Discriminant dactivated")


            new_tree = tree.CloneTree()

            discr_array = array("f", [-999])
            branch = new_tree.Branch("Discriminant", discr_array, "Discriminant/F")
            logger.debug("Created branch Discriminant")
            
            rand = ROOT.TRandom2()
            for i in range(tree.GetEntries()):
                new_tree.GetEntry(i)
                
                '''if args.variablesML == "tot":
                    discr_array[0] = reader.EvaluateMVA([new_tree.Z1_mass,
                                        new_tree.Z2_mass, new_tree.cos_theta_star,
                                        new_tree.Phi, new_tree.Phi1, new_tree.cos_theta1,
                                        new_tree.cos_theta2], "PyKeras")
                elif args.variablesML == "part":
                    discr_array[0] = reader.EvaluateMVA([new_tree.cos_theta_star,
                                                         new_tree.Phi, new_tree.Phi1,
                                                         new_tree.cos_theta1,
                                                         new_tree.cos_theta2], "PyKeras")
                elif args.variablesML == "higgs":
                    discr_array[0] = reader.EvaluateMVA([new_tree.Higgs_mass], "PyKeras")'''
                    
                discr_array[0]= rand.Rndm()
                branch.Fill()

            new_tree.Write("", ROOT.TObject.kOverwrite)

            #in_file.Close()
            logger.info(">>> Execution time: %s s \n", (time.time() - start_time))
            
            
if __name__ == "__main__":    
    
    # General configuration
    parser = argparse.ArgumentParser( description = 'Analysis Tool' )
    parser.add_argument('-p', '--parallel',   default=True,   action='store_const',
                        const=False, help='disables running in parallel')
    parser.add_argument('-n', '--nWorkers',   default=0,
                        type=int,   help='number of workers' )
    parser.add_argument('-v', '--variablesML',     default="tot",
                         type=str,   help='name of the set of variables \
                         to be used in the ML algorithm (tot, part, higgs)')
    parser.add_argument('-o', '--output',     default="Output", type=str,
                        help='name of the output directory')
    parser.add_argument('-l', '--logLevel',   default=20, type=int,   
                            help='integer representing the level of the logger:\
                             DEBUG=10, INFO = 20, WARNING = 30, ERROR = 40' )
    parser.add_argument('-f', '--finalState',   default="all", type=str,   
                            help='comma separated list of the final states to analyse: \
                            FourMuons,FourElectrons,TwoMuonsTwoElectrons' )
    args_main = parser.parse_args()

    logger_main=set_up.set_up(args_main)
    
        
    ml_application(args_main, logger_main, "..", "..")
