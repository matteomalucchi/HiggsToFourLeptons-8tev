import argparse
import sys
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

import ROOT

sys.path.append('../')
from definitions.samples_def import SAMPLES
from definitions.variables_ml_def import VARIABLES_ML_DICT
#import definitions.variables_ml_def
#from definitions.variables_ml_def import VARIABLES_TOT_ML as variables

simulated_samples = {k: v for k, v in SAMPLES.items() if not k.startswith("Run")}

def main(args):
    """Main function """
    # Setup TMVA
    ROOT.TMVA.Tools.Instance()
    ROOT.TMVA.PyMethodBase.PyInitialize()

    output = ROOT.TFile.Open("TMVA.root", "RECREATE")
    factory = ROOT.TMVA.Factory("TMVAClassification", output,
                        "!V:!Silent:Color:DrawProgressBar:Transformations=D,G:AnalysisType=Classification")

    variables=VARIABLES_ML_DICT[args.mlVariables]
    #
    dataloader = ROOT.TMVA.DataLoader("dataset")
    for variable in variables:
        dataloader.AddVariable(variable)
        print(variable)


    signal_chain=ROOT.TChain("Events")
    bkg_chain=ROOT.TChain("Events")

    for sample_name, final_states in simulated_samples.items():
            for final_state in final_states:
                print(">>> Process sample {} and final state {}".format(sample_name, final_state))
                file_name="../skim_data/" + sample_name + final_state + "Skim.root"
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
    model.save("model.h5")
    model.summary()


    # Book methods
    factory.BookMethod(dataloader, ROOT.TMVA.Types.kPyKeras, "PyKeras",
                    "H:!V:VarTransform=D,G:FilenameModel=model.h5:NumEpochs=20:BatchSize=128")
                    
    # Run training, test and evaluation
    factory.TrainAllMethods()
    factory.TestAllMethods()
    factory.EvaluateAllMethods()

    # Print ROC curve
    c=factory.GetROCCurve(dataloader)
    c.Draw()
    c.Print("ml_roc.png")

if __name__ == "__main__":
    
    '''    # global configuration
    parser = argparse.ArgumentParser( description = 'Analysis Tool' )
    parser.add_argument('-n', '--nWorkers',   default=0,                                 type=int,   help='number of workers' )  
    parser.add_argument('-p', '--parallel',   default=False,   action='store_const',     const=True, help='enables running in parallel')
    parser.add_argument('-c', '--configfile', default="Configurations/HZZConfiguration.py", type=str,   help='files to be analysed')
    parser.add_argument('-s', '--samples',    default=""                               , type=str,   help='string with comma separated list of samples to analyse')
    parser.add_argument('-o', '--output',     default=""                               , type=str,   help='name of the output directory')
    parser.add_argument('-m', '--mlVariables',     default="tot"                               , type=str,   help='name of the set of variables to be used in the ML algorithm')
    args = parser.parse_args()'''
    
    main()
    
#root[] TMVA::TMVAGui("TMVA.root")