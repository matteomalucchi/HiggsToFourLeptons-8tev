""" In this step the DNN is trained on the Monte Carlo samples
of signal and background. The training is done thanks to
keras API. To take a look at the output of the training run 
``$ TMVA::TMVAGui("TMVA.root")`` from the ROOT prompt.
The training is done using as variables the masses of the Z bosons
and the five angles described in detail in `[Phys.Rev.D86:095031,2012]
<https://journals.aps.org/prd/abstract/10.1103/PhysRevD.86.095031>`_.
"""

import time
import argparse

import sys
import os

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

import ROOT

sys.path.append("../../")

from Analysis.Definitions.samples_def import SAMPLES
from Analysis.Definitions.variables_ml_def import VARIABLES_ML_DICT

import Analysis.set_up as set_up


def ml_training(args, logger):
    """Main function for the training of the DNN. The DNN is
    trained on the simulated Monte Carlo samples.

    :param args: Global configuration of the analysis.
    :type args: argparse.Namespace
    :param logger: Configurated logger for printing messages.
    :type logger: logging.RootLogger
    """

    logger.info(">>> Executing %s \n", os.path.basename(__file__))

    start_time = time.time()

    # Setup TMVA
    ROOT.TMVA.Tools.Instance()
    ROOT.TMVA.PyMethodBase.PyInitialize()

    # Create the directory to save the outputs of the ml algorithm if doesn't already exist
    dir_name = os.path.join(args.output, "ML_output")
    try:
        os.makedirs(dir_name)
        logger.debug("Directory %s/ Created", dir_name)
    except FileExistsError:
        logger.debug("The directory %s/ already exists", dir_name)

    # Create file to save the results
    tmva_path=os.path.join(dir_name, "TMVA.root")
    output = ROOT.TFile.Open(tmva_path, "RECREATE")
    logger.debug("File %s Created", tmva_path)
    
    factory = ROOT.TMVA.Factory("TMVAClassification", output,
                        "!V:!Silent:Color:DrawProgressBar:Transformations=D,G:AnalysisType=Classification")

    # Variables used in the ML algorithm
    variables=VARIABLES_ML_DICT[args.algorithmMLVar]
    
    # Directory where the weights are saved
    dataset_path=os.path.join(dir_name, "dataset")
    dataloader = ROOT.TMVA.DataLoader(dataset_path)
    for variable in variables:
        dataloader.AddVariable(variable)
        logger.debug(variable)


    signal_chain=ROOT.TChain("Events")
    bkg_chain=ROOT.TChain("Events")

    simulated_samples = {k: v for k, v in SAMPLES.items() if not k.startswith("Run")}

    for sample_name, final_states in simulated_samples.items():
        # Check if the sample to plot is one of those requested by the user
        if sample_name not in args.sample and args.sample != "all":
            continue
        for final_state in final_states:
            # Check if the final state is one of those requested by the user
            if final_state not in args.finalState and args.finalState != "all":
                continue
            logger.debug(">>> Process sample %s and final state %s", sample_name, final_state)
            # Check if file exists or not
            try: 
                file_name=os.path.join(args.output, "Skim_data",
                                   f"{sample_name}{final_state}Skim.root")
                if not os.path.exists(file_name):
                    raise FileNotFoundError
            except FileNotFoundError as not_found_err:
                logger.debug("Sample %s final state %s: File %s can't be found %s",
                                sample_name, final_state, file_name, not_found_err,  stack_info=True)
                continue
            
            if sample_name == "SMHiggsToZZTo4L":
                signal_chain.Add(file_name)
            else:
                bkg_chain.Add(file_name)
    
    try:
        dataloader.AddSignalTree(signal_chain, 1.0)
        dataloader.AddBackgroundTree(bkg_chain, 1.0)
    except TypeError as type_err:
        logger.exception("Unable to train the DNN on the simulated samples %s", 
                        type_err, stack_info=True)
        logger.exception("Exit the program")                        
        return

    
    dataloader.PrepareTrainingAndTestTree(ROOT.TCut(""),"SplitMode=Random:NormMode=NumEvents:!V")

    # Generate model

    # Define model
    model = Sequential()
    model.add(Dense(64, activation="relu", input_dim=len(variables)))
    model.add(Dense(12, activation="relu"))
    model.add(Dense(12, activation="relu"))
    model.add(Dense(12, activation="relu"))
    #model.add(Dense(12, activation="relu"))
    model.add(Dense(2, activation="sigmoid"))


    # Set loss and optimizer
    model.compile(loss="binary_crossentropy",
                optimizer="adam", metrics=["accuracy", ], weighted_metrics=[])

    # Store model to file
    mod_path=os.path.join(dir_name, "model.h5")
    model.save(mod_path)
    model.summary()


    # Book methods
    factory.BookMethod(dataloader, ROOT.TMVA.Types.kPyKeras, "PyKeras",
                    f"H:!V:VarTransform=D,G:FilenameModel={mod_path}:NumEpochs=30:BatchSize=128")

    # Run training, test and evaluation
    factory.TrainAllMethods()
    factory.TestAllMethods()
    factory.EvaluateAllMethods()

    # Print ROC curve
    c_roc=factory.GetROCCurve(dataloader)
    c_roc.Draw()
    c_roc.Print(os.path.join(dir_name, "ml_roc.png"))

    logger.info(">>> Execution time: %s s \n", (time.time() - start_time))

if __name__ == "__main__":
    
    # General configuration
    parser = argparse.ArgumentParser( description = "Analysis Tool" )
    parser.add_argument("-a", "--algorithmMLVar",     default="tot"  , type=str,
                        help="name of the set of variables to be used \
                            in the ML algorithm (tot, part, higgs)")
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
    
                
    ml_training(args_main, logger_main)
