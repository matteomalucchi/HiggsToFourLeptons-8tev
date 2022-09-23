""" In this step the trained DNN is evaluated on the various datasets
and the resulting disciminant is saved in a new branch of the "Events" tree.
"""


from array import array
import sys
import time
import os
import argparse

import ROOT

sys.path.append(os.path.join("..","..", ""))

from Analysis.Definitions.samples_def import SAMPLES
from Analysis.Definitions.variables_ml_def import VARIABLES_ML_DICT

from Analysis import set_up

def modify_weights_file(output, file_path, log):
    """ Function that modifies in the file ``TMVAClassification_PyKeras.weights.xml``
        the path to the model according to the directory where the file is executed.
        This allows the reader to correctly find the needed files containing the model.

    :param output: Path to the output folder
    :type output: str
    :param file_path: Path to TMVAClassification_PyKeras.weights.xml
    :type file_path: str
    :param log: Configurated logger for printing messages.
    :type log: logging.RootLogger
    """

    with open(file_path, "r") as file:
        # Read the list of lines
        data = file.readlines()

    # Change the lines
    data[20] = f'    <Option name="FilenameModel" modified="Yes">{output}/ML_output/DNNmodel.h5</Option>\n'
    data[21] = f'    <Option name="FilenameTrainedModel" modified="No">{output}/ML_output/dataset/weights/TrainedModel_PyKeras.h5</Option>\n'

    # and write everything back
    with open(file_path, "w") as file:
        file.writelines( data )

    log.debug("Path changed correctly")

def ml_evaluation(args, logger):
    """ Main function that evaluates the DNN on the whole dataset.

    :param args: Global configuration of the analysis.
    :type args: argparse.Namespace
    :param logger: Configurated logger for printing messages.
    :type logger: logging.RootLogger
    """

    logger.info(">>> Executing %s \n", os.path.basename(__file__))

    start_time_tot = time.time()

    # Enamble multi-threading
    if args.parallel:
        ROOT.ROOT.EnableImplicitMT()
        thread_size = ROOT.ROOT.GetThreadPoolSize()
        logger.info(">>> Thread pool size for parallel processing: %s", thread_size)

    # Setup TMVA
    ROOT.TMVA.Tools.Instance()
    ROOT.TMVA.PyMethodBase.PyInitialize()
    reader = ROOT.TMVA.Reader("Color:Silent:!V")

    # Variables used in the ML algorithm
    variables=VARIABLES_ML_DICT[args.MLVariables]

    branches = {}
    for branch_name in variables:
        logger.debug(branch_name)
        branches[branch_name] = array("f", [-999])
        reader.AddVariable(branch_name, branches[branch_name])

    weights_path=os.path.join(args.output, "ML_output", "dataset", "weights", "TMVAClassification_PyKeras.weights.xml")

    modify_weights_file(args.output, weights_path, logger)

    try:
        # Book methods
        reader.BookMVA("PyKeras", ROOT.TString(weights_path))
    except TypeError as type_err:
        logger.exception("Unable too open weights %s",
                        type_err, stack_info=True)
        logger.exception("Exit the program")
        return

    # Define a counter
    j=1

    # Loop over the various samples
    for sample_name, final_states in SAMPLES.items():
        # Check if the sample to plot is one of those requested by the user
        if sample_name not in args.sample and args.sample != "all":
            continue
        # Loop over the possible final states
        for final_state in final_states:
            # Check if the final state is one of those requested by the user
            if final_state not in args.finalState and args.finalState != "all":
                continue

            logger.info(">>> Process sample: %s and final state %s", sample_name, final_state)
            start_time = time.time()

            # Check if file exists or not
            try:
                in_file_path=os.path.join(args.output,
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
            n_entries = tree.GetEntries()
            for i in range(n_entries):
                new_tree.GetEntry(i)

                if args.MLVariables == "tot":
                    discr_array[0] = reader.EvaluateMVA([new_tree.Z1_mass,
                                        new_tree.Z2_mass, new_tree.cos_theta_star,
                                        new_tree.Phi, new_tree.Phi1, new_tree.cos_theta1,
                                        new_tree.cos_theta2], "PyKeras")
                elif args.MLVariables == "higgs":
                    discr_array[0] = reader.EvaluateMVA([new_tree.Higgs_mass], "PyKeras")

                #discr_array[0]= rand.Rndm()
                branch.Fill()
                if i % 300 == 0:
                    logger.info(f"Processed {i} events out of {n_entries} in sample {sample_name} and final state {final_state} ({j} / 14 in total) \n")

            new_tree.Write("", ROOT.TObject.kOverwrite)

            j += 1

            #in_file.Close()
            logger.info(">>> Execution time for %s %s: %s s \n", sample_name, final_state, (time.time() - start_time))

    logger.info(">>> Total Execution time: %s s \n", (time.time() - start_time_tot))

if __name__ == "__main__":

    # General configuration
    parser = argparse.ArgumentParser( description = "Analysis Tool" )
    parser.add_argument("-p", "--parallel",   default=True,   action="store_const",
                        const=False, help="disables running in parallel")
    parser.add_argument("-n", "--nWorkers",   default=0,
                        type=int,   help="number of workers for multi-threading" )
    parser.add_argument("-a", "--MLVariables",     default="tot",
                         type=str,   help="name of the set of variables to be used in the ML \
                            algorithm defined 'variables_ml_def.py': tot, higgs")
    parser.add_argument("-o", "--output",     default=os.path.join("..", "..", "Output"), type=str,
                        help="name of the output directory")
    parser.add_argument("-l", "--logLevel",   default=20, type=int,
                            help="integer representing the level of the logger:\
                             DEBUG=10, INFO = 20, WARNING = 30, ERROR = 40" )
    parser.add_argument("-f", "--finalState",   default="all", type=str,
                            help="comma separated list of the final states to analyse: \
                            FourMuons,FourElectrons,TwoMuonsTwoElectrons" )
    parser.add_argument("-s", "--sample",    default="all", type=str,
                        help="string with comma separated list of samples to analyse: \
                        Run2012B_DoubleElectron, Run2012B_DoubleMuParked, Run2012C_DoubleElectron, \
                        Run2012C_DoubleMuParked, SMHiggsToZZTo4L, ZZTo2e2mu, ZZTo4e, ZZTo4mu")
    args_main = parser.parse_args()

    logger_main=set_up.set_up(args_main)


    ml_evaluation(args_main, logger_main)
