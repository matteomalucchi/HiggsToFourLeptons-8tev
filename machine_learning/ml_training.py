import argparse
import sys
import os
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

import ROOT

sys.path.append('../')
from definitions.samples_def import SAMPLES
from definitions.variables_ml_def import VARIABLES_ML_DICT
#import definitions.variables_ml_def
#from definitions.variables_ml_def import VARIABLES_TOT_ML as variables

simulated_samples = {k: v for k, v in SAMPLES.items() if not k.startswith("Run")}

def main(args, path_o="machine_learning", path_sd=""):
    """Main function """
    # Setup TMVA
    ROOT.TMVA.Tools.Instance()
    ROOT.TMVA.PyMethodBase.PyInitialize()

    tmva_path=os.path.join(path_o, "TMVA.root")
    output = ROOT.TFile.Open(tmva_path, "RECREATE")
    
    factory = ROOT.TMVA.Factory("TMVAClassification", output,
                        "!V:!Silent:Color:DrawProgressBar:Transformations=D,G:AnalysisType=Classification")

    # Variables used in the ML algorithm
    variables=VARIABLES_ML_DICT[args.variablesML]
    #
    dataset_path=os.path.join(path_o, "dataset")
    dataloader = ROOT.TMVA.DataLoader(dataset_path)
    for variable in variables:
        dataloader.AddVariable(variable)
        print(variable)


    signal_chain=ROOT.TChain("Events")
    bkg_chain=ROOT.TChain("Events")

    for sample_name, final_states in simulated_samples.items():
            for final_state in final_states:
                print(">>> Process sample {} and final state {}".format(sample_name, final_state))
                file_name=os.path.join(path_sd,"skim_data", f"{sample_name}{final_state}Skim.root")
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
    model.add(Dense(12, activation="relu"))
    #model.add(Dense(12, activation="relu"))
    model.add(Dense(2, activation="sigmoid"))


    # Set loss and optimizer
    model.compile(loss="binary_crossentropy",
                optimizer="adam", metrics=["accuracy", ], weighted_metrics=[])

    # Store model to file
    mod_path=os.path.join(path_o, "model.h5")
    model.save(mod_path)
    model.summary()


    # Book methods
    factory.BookMethod(dataloader, ROOT.TMVA.Types.kPyKeras, "PyKeras",
                    f"H:!V:VarTransform=D,G:FilenameModel={mod_path}:NumEpochs=2:BatchSize=128")
                    
    # Run training, test and evaluation
    factory.TrainAllMethods()
    factory.TestAllMethods()
    factory.EvaluateAllMethods()

    # Print ROC curve
    c=factory.GetROCCurve(dataloader)
    c.Draw()
    roc_path=os.path.join(path_o, "ml_roc.png")
    c.Print(roc_path)

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser( description = 'Analysis Tool' )
    parser.add_argument('-n', '--nWorkers',   default=0,                                 type=int,   help='number of workers' )  
    parser.add_argument('-p', '--parallel',   default=False,   action='store_const',     const=True, help='enables running in parallel')
    parser.add_argument('-c', '--configfile', default="Configurations/HZZConfiguration.py", type=str,   help='files to be analysed')
    parser.add_argument('-s', '--samples',    default=""                               , type=str,   help='string with comma separated list of samples to analyse')
    parser.add_argument('-o', '--output',     default=""                               , type=str,   help='name of the output directory')
    parser.add_argument('-m', '--mlVariables',     default="tot"                               , type=str,   help='name of the set of variables to be used in the ML algorithm')
    args = parser.parse_args()
    
    main(args, "", "..")
    
#root[] TMVA::TMVAGui("TMVA.root")
