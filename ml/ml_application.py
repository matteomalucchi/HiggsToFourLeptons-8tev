from ROOT import TMVA, TString, TChain, TH1F, TCanvas
from array import array
import sys

sys.path.append('../')
from definitions.samples_def import SAMPLES
from definitions.variables_ml_def import VARIABLES_ANGLES_ML as variables


simulated_samples = {k: v for k, v in SAMPLES.items() if not k.startswith("Run")}
data_samples = {k: v for k, v in SAMPLES.items() if k.startswith("Run")}


if __name__ == "__main__":
    # Setup TMVA
    TMVA.Tools.Instance()
    TMVA.PyMethodBase.PyInitialize()
    reader = TMVA.Reader("Color:!Silent")

    signal_chain=TChain("Events")
    bkg_chain=TChain("Events")

    for sample_name, final_states in simulated_samples.items():
        for final_state in final_states:
            print(">>> Process sample {} and final state {}".format(sample_name, final_state))
            file_name="../skim_data/" + sample_name + final_state + "Skim.root"
            if sample_name == "SMHiggsToZZTo4L":
                signal_chain.Add(file_name)
            else:
                bkg_chain.Add(file_name)


    branches = {}
    for branch in signal_chain.GetListOfBranches():
        branchName = branch.GetName()
        if (branchName in variables):
            print(branchName)
            branches[branchName] = array("f", [-999])
            reader.AddVariable(branchName, branches[branchName])
            signal_chain.SetBranchAddress(branchName, branches[branchName])
            bkg_chain.SetBranchAddress(branchName, branches[branchName])

    # Book methods
    reader.BookMVA("PyKeras", TString("dataset/weights/TMVAClassification_PyKeras.weights.xml"))

    histo_s=TH1F("signal", "signal", 1000, 0,1)
    histo_b=TH1F("bkg", "bkg", 1000, 0,1)

    # Print some example classifications
    print("Some signal example classifications:")
    for i in range(50000):
        signal_chain.GetEntry(i)
        histo_s.Fill(reader.EvaluateMVA("PyKeras"))
        #print(signal_chain.Higgs_mass)
        if i%1000 == 0:
            print(reader.EvaluateMVA("PyKeras"))
    
    print("")

    s = TCanvas("s", "s", 600, 600)
    histo_s.Draw() 

    print("Some background example classifications:")
    for i in range(50000):
        bkg_chain.GetEntry(i)
        histo_b.Fill(reader.EvaluateMVA("PyKeras"))
        #print(bkg_chain.Higgs_mass)
        if i%1000 == 0:
            print(reader.EvaluateMVA("PyKeras"))


    b = TCanvas("b", "b", 600, 600)
    histo_b.Draw()