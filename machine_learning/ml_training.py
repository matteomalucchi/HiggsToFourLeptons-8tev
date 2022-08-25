"""
In this step the DNN is trained on the Monte Carlo samples
of signal and background. The training is done thanks to
keras API.
"""
import time
import argparse
import logging
import sys
import os

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

import ROOT

sys.path.append('../')

from Definitions.samples_def import SAMPLES
from Definitions.variables_ml_def import VARIABLES_ML_DICT


def ml_training(args, logger, path_o="", path_sd=""):
    """Main function for the training of the DNN. The DNN is
    trained on the simulated Monte Carlo samples.

    :param args: Global configuration of the analysis.
    :type args: argparse.Namespace
    :param logger: Configurated logger for printing messages.
    :type logger: logging.RootLogger
    :param path_o: Optional base path to save the output of the training.
    :type path_o: str
    :param path_sd: Optional base path to find the directory ``skim_data/``.
    :type path_sd: str
    """

    logger.info(">>> Executing %s \n", os.path.basename(__file__))

    start_time = time.time()

    # Setup TMVA
    ROOT.TMVA.Tools.Instance()
    ROOT.TMVA.PyMethodBase.PyInitialize()

    # Create the directory to save the outputs of the ml algorithm if doesn't already exist
    dir_name = os.path.join(path_o, args.output, "ml_output")
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        logger.debug("Directory %s Created", dir_name)

    # Create file to save the results
    tmva_path=os.path.join(dir_name, "TMVA.root")
    output = ROOT.TFile.Open(tmva_path, "RECREATE")

    factory = ROOT.TMVA.Factory("TMVAClassification", output,
                        "!V:!Silent:Color:DrawProgressBar:\
                        Transformations=D,G:AnalysisType=Classification")

    # Variables used in the ML algorithm
    variables=VARIABLES_ML_DICT[args.variablesML]
    #
    dataset_path=os.path.join(dir_name, "dataset")
    dataloader = ROOT.TMVA.DataLoader(dataset_path)
    for variable in variables:
        dataloader.AddVariable(variable)
        logger.debug(variable)


    signal_chain=ROOT.TChain("Events")
    bkg_chain=ROOT.TChain("Events")

    simulated_samples = {k: v for k, v in SAMPLES.items() if not k.startswith("Run")}

    for sample_name, final_states in simulated_samples.items():
        for final_state in final_states:
            logger.info(">>> Process sample %s and final state %s", sample_name, final_state)
            file_name=os.path.join(path_sd, args.output, "skim_data",
                                   f"{sample_name}{final_state}Skim.root")
            if sample_name == "SMHiggsToZZTo4L":
                signal_chain.Add(file_name)
            else:
                bkg_chain.Add(file_name)

    dataloader.AddSignalTree(signal_chain, 1.0)
    dataloader.AddBackgroundTree(bkg_chain, 1.0)

    #dataloader.PrepareTrainingAndTestTree(TCut(""),"nTrain_Signal=13354:nTrain_Background=95961:\
    #                                                    SplitMode=Block:NormMode=NumEvents:!V")
    dataloader.PrepareTrainingAndTestTree(ROOT.TCut(""),"SplitMode=Random:NormMode=NumEvents:!V")

    # Generate model

    # Define model
    model = Sequential()
    model.add(Dense(64, activation="relu", input_dim=len(variables)))
    model.add(Dense(12, activation="relu"))
    model.add(Dense(12, activation="relu"))
    #model.add(Dense(12, activation="relu"))
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
                    f"H:!V:VarTransform=D,G:FilenameModel={mod_path}:NumEpochs=10:BatchSize=128")

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

    # Create and configure logger
    logging.basicConfig( format='\n%(asctime)s %(message)s')
    # Create an object
    logger_main=logging.getLogger()
    # Set the threshold of logger
    logger_main.setLevel(logging.INFO)

    # General configuration
    parser = argparse.ArgumentParser( description = 'Analysis Tool' )
    parser.add_argument('-v', '--variablesML',     default="tot"  , type=str,
                        help='name of the set of variables to be used \
                            in the ML algorithm (tot, part, higgs)')
    parser.add_argument('-o', '--output',     default="Output", type=str,
                        help='name of the output directory')
    args_main = parser.parse_args()

    ml_training(args_main, logger_main, "..", "..")

#root[] TMVA::TMVAGui("TMVA.root")
