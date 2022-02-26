import ROOT

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import SGD


sim_samples={
    "SMHiggsToZZTo4L": ["FourMuons", "FourElectrons", "TwoMuonsTwoElectrons"],
    "ZZTo4mu": ["FourMuons"],
    "ZZTo4e": ["FourElectrons"],
    "ZZTo2e2mu": ["TwoMuonsTwoElectrons"],
}

"""sim_samples={
    "SMHiggsToZZTo4L": ["FourMuons"],
    "ZZTo4mu": ["FourMuons"],
}"""

integrated_luminosity = 11.58 * 1000.0
scale_factor_ZZ_4l = 1.386
event_weights = {
	"SMHiggsToZZTo4L": 1 / 299973.0 * 1000000000,
	"ZZTo4mu": 1 / 1499064.0  * 1000000000,
	"ZZTo4e": 1 / 1499093.0 * 1000000000,
	"ZZTo2e2mu": 1 / 1497445.0  * 1000000000,
}

branches = ROOT.vector("std::string")()
branches.push_back("theta_star")
branches.push_back("Phi")
branches.push_back("Phi1")
branches.push_back("theta1")
branches.push_back("theta2")

if __name__ == "__main__":
    ROOT.ROOT.EnableImplicitMT()
    thread_size = ROOT.ROOT.GetThreadPoolSize()
    print(">>> Thread pool size for parallel processing: {}".format(thread_size))

    # Setup TMVA
    ROOT.TMVA.Tools.Instance()
    ROOT.TMVA.PyMethodBase.PyInitialize()

    output = ROOT.TFile.Open("TMVA.root", "RECREATE")
    factory = ROOT.TMVA.Factory("TMVAClassification", output,
                       "!V:!Silent:Color:DrawProgressBar:Transformations=D,G:AnalysisType=Classification")
    """factory = ROOT.TMVA.Factory("TMVAClassification", output,
                       "!V:!Silent:Color:!DrawProgressBar:AnalysisType=Classification" )"""

    dataloader = ROOT.TMVA.DataLoader("dataset")

    for branch in branches:
        dataloader.AddVariable(branch)

    for sample_name, final_states in sim_samples.items():
        for final_state in final_states:
            print(">>> Process sample {} and final state {}".format(sample_name, final_state))
            input = ROOT.TFile.Open( "../angles/" + sample_name + final_state + "Angles.root")
            if sample_name == "SMHiggsToZZTo4L":
                signal = input.Get("Events")
                dataloader.AddSignalTree(signal, event_weights[sample_name])

            else: 
                background = input.Get("Events")
                dataloader.AddBackgroundTree(background, event_weights[sample_name])
    




    dataloader.PrepareTrainingAndTestTree(ROOT.TCut(""),
                                      "nTrain_Signal=35000:nTrain_Background=35000:SplitMode=Random:NormMode=NumEvents:!V")
    
        
    """dataloader.PrepareTrainingAndTestTree(ROOT.TCut(""),
                                      "SplitMode=Random:NormMode=NumEvents:!V")"""
    
    
    # Define model
    model = Sequential()
    model.add(Dense(12, activation="relu", input_dim=5))
    model.add(Dense(12, activation="relu"))
    model.add(Dense(12, activation="relu"))
    model.add(Dense(12, activation="relu"))    
    model.add(Dense(12, activation="relu"))    
    model.add(Dense(12, activation="relu"))               
    model.add(Dense(2, activation="softmax"))


    #model.compile(loss="binary_crossentropy", optimizer= "adam", metrics=["accuracy"])
    model.compile(loss="categorical_crossentropy", optimizer=SGD(lr=0.01), metrics=["accuracy"])

    # Store model to file
    model.save("model_ml.h5")
    model.summary()

        # Book methods
    factory.BookMethod(dataloader, ROOT.TMVA.Types.kFisher, "Fisher",
                    "!H:!V:Fisher:VarTransform=D,G")
    factory.BookMethod(dataloader, ROOT.TMVA.Types.kPyKeras, "PyKeras",
                    "H:!V:VarTransform=D,G:FilenameModel=model_ml.h5:NumEpochs=100:BatchSize=32")
    

    # Configure Network Layout

    # General layout
    layoutString = ROOT.TString("Layout=TANH|128,TANH|128,TANH|128,LINEAR")

    # Training strategies
    training0 = ROOT.TString("LearningRate=1e-1,Momentum=0.9,Repetitions=10,"
                            "ConvergenceSteps=2,BatchSize=256,TestRepetitions=10,"
                            "WeightDecay=1e-4,Regularization=L2,"
                            "DropConfig=0.0+0.5+0.5+0.5, Multithreading=True")

    training1 = ROOT.TString("LearningRate=1e-2,Momentum=0.9,Repetitions=10,"
                            "ConvergenceSteps=2,BatchSize=256,TestRepetitions=10,"
                            "WeightDecay=1e-4,Regularization=L2,"
                            "DropConfig=0.0+0.0+0.0+0.0, Multithreading=True")

    trainingStrategyString = ROOT.TString("TrainingStrategy=")
    trainingStrategyString += training0 + ROOT.TString("|") + training1

    # General Options
    dnnOptions = ROOT.TString("!H:!V:ErrorStrategy=CROSSENTROPY:VarTransform=N:"
            "WeightInitialization=XAVIERUNIFORM")
    dnnOptions.Append(":")
    dnnOptions.Append(layoutString)
    dnnOptions.Append(":")
    dnnOptions.Append(trainingStrategyString)

    # Booking Methods
    # Standard implementation, no dependencies.
    stdOptions =  dnnOptions + ":Architecture=CPU"
    factory.BookMethod(dataloader, ROOT.TMVA.Types.kDNN, "DNN", stdOptions)


    #print(dataloader.GetDataSetInfo())

    # Run training, test and evaluation
    factory.TrainAllMethods()
    factory.TestAllMethods()
    factory.EvaluateAllMethods()

    c=factory.GetROCCurve(dataloader)
    c.Draw()
    c.Print("ml_roc.png")