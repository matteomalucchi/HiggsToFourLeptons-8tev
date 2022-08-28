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
    :param path_sd: Optional base path to find the directory ``Skim_data/``.
    :type path_sd: str
    """

    logger.info(">>> Executing %s \n", os.path.basename(__file__))

    start_time = time.time()

    # Setup TMVA
    ROOT.TMVA.Tools.Instance()
    ROOT.TMVA.PyMethodBase.PyInitialize()

    # Create the directory to save the outputs of the ml algorithm if doesn't already exist
    dir_name = os.path.join(path_o, args.output, "ML_output")
    try:
        os.makedirs(dir_name)
        logger.debug("Directory %s/ Created", dir_name)
    except FileExistsError:
        logger.debug("The directory %s/ already exists", dir_name)

    # Create file to save the results
    tmva_path=os.path.join(dir_name, "TMVA.root")
    output = ROOT.TFile.Open(tmva_path, "RECREATE")

    factory = ROOT.TMVA.Factory("TMVAClassification", output,
                        "!V:!Silent:Color:DrawProgressBar:Transformations=D,G:AnalysisType=Classification")

    # Variables used in the ML algorithm
    variables=VARIABLES_ML_DICT[args.variablesML]
    
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
        for final_state in final_states:
            # Check if the final state is one of those requested by the user
            if final_state not in args.finalState and args.finalState != "all":
                continue
            logger.debug(">>> Process sample %s and final state %s", sample_name, final_state)
            # Check if file exists or not
            try: 
                file_name=os.path.join(path_sd, args.output, "Skim_data",
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
    
    # General configuration
    parser = argparse.ArgumentParser( description = 'Analysis Tool' )
    parser.add_argument('-v', '--variablesML',     default="tot"  , type=str,
                        help='name of the set of variables to be used \
                            in the ML algorithm (tot, part, higgs)')
    parser.add_argument('-o', '--output',     default="Output", type=str,
                        help='name of the output directory')
    parser.add_argument('-l', '--logLevel',   default=20, type=int,   
                            help='integer representing the level of the logger:\
                             DEBUG=10, INFO = 20, WARNING = 30, ERROR = 40' )
    parser.add_argument('-f', '--finalState',   default="all", type=str,   
                            help='comma separated list of the final states to analyse: \
                            FourMuons,FourElectrons,TwoMuonsTwoElectrons' )
    args_main = parser.parse_args()

    # Create and configure logger
    logging.basicConfig( format='\n%(asctime)s %(message)s')
    # Create an object
    logger_main=logging.getLogger()
    
    # Check if logLevel valid           
    try:
        if args_main.logLevel not in [10, 20, 30, 40]:
            raise argparse.ArgumentTypeError(f"the value for logLevel {args_main.logLevel} is invalid: it must be either 10, 20, 30 or 40")
    except argparse.ArgumentTypeError as arg_err:
        args_main.logLevel = 20
        logger_main.exception("%s \nlogLevel is set to 20 \n", arg_err, stack_info=True)
        
    # Set the threshold of logger
    logger_main.setLevel(args_main.logLevel)

    # Check if finalState is valid
    try:
        if not any(final_state in args_main.finalState for final_state 
               in ["all", "FourMuons", "FourElectrons", "TwoMuonsTwoElectrons"]):
            raise argparse.ArgumentTypeError(f"the final state {args_main.finalState} is invalid: \
                it must be either all,FourMuons,FourElectrons,TwoMuonsTwoElectrons")
    except argparse.ArgumentTypeError as arg_err:
        logger_main.exception("%s \n finalState is set to all \n", arg_err, stack_info=True)
        args_main.finalState = "all"  

    # Check if variablesML is valid
    try:
        if not any(var_ml in args_main.variablesML for var_ml 
               in ["tot", "part", "higgs"]):
            raise argparse.ArgumentTypeError(f"the set of ML variables {args_main.variablesML} is invalid: \
                it must be either tot, part, higgs")
    except argparse.ArgumentTypeError as arg_err:
        logger_main.exception("%s \n variablesML is set to tot \n", arg_err, stack_info=True)
        args_main.variablesML = "all"    
                
    ml_training(args_main, logger_main, "..", "..")

#root[] TMVA::TMVAGui("TMVA.root")