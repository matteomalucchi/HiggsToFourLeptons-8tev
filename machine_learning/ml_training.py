import sys
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

import ROOT

sys.path.append('../')
from definitions.samples_def import SAMPLES
from definitions.variables_ml_def import VARIABLES_TOT_ML as variables

simulated_samples = {k: v for k, v in SAMPLES.items() if not k.startswith("Run")}

def main():
    """Main function """
    # Setup TMVA
    ROOT.TMVATools.Instance()
    ROOT.TMVAPyMethodBase.PyInitialize()

    output = ROOT.TFile.Open("TMVA.root", "RECREATE")
    factory = ROOT.TMVAFactory("TMVAClassification", output,
                        "!V:!Silent:Color:DrawProgressBar:Transformations=D,G:AnalysisType=Classification")

    #
    dataloader = ROOT.TMVADataLoader("dataset")
    for variable in variables:
        dataloader.AddVariable(variable)


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
                optimizer="adam", metrics=["accuracy", ])

    # Store model to file
    model.save("model.h5")
    model.summary()


    # Book methods
    factory.BookMethod(dataloader, ROOT.TMVATypes.kPyKeras, "PyKeras",
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

    main()
    
#root[] TMVA::TMVAGui("TMVA.root")
