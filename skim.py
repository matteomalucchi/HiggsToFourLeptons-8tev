#skimming process

import ROOT
import time


import skim_tools

#base path

#base_path = "root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/ForHiggsTo4Leptons/"

base_path = "data/"

#various datasets

samples={
    "SMHiggsToZZTo4L": ["FourMuons", "FourElectrons", "TwoMuonsTwoElectrons"],
    "ZZTo4mu": ["FourMuons"],
    "ZZTo4e": ["FourElectrons"],
    "ZZTo2e2mu": ["TwoMuonsTwoElectrons"],
    "Run2012B_DoubleMuParked": ["FourMuons", "TwoMuonsTwoElectrons"],
    "Run2012C_DoubleMuParked": ["FourMuons", "TwoMuonsTwoElectrons"],
    "Run2012B_DoubleElectron": ["FourElectrons", "TwoMuonsTwoElectrons"],
    "Run2012C_DoubleElectron": ["FourElectrons", "TwoMuonsTwoElectrons"]
}

finalVariables = ROOT.vector("std::string")()
finalVariables.push_back("run")
finalVariables.push_back("Weight")
finalVariables.push_back("theta_star")
finalVariables.push_back("Phi")
finalVariables.push_back("Phi1")
finalVariables.push_back("theta1")
finalVariables.push_back("theta2")
finalVariables.push_back("Higgs_mass")
finalVariables.push_back("Z1_mass")
finalVariables.push_back("Z2_mass")
finalVariables.push_back("Higgs_pt")
finalVariables.push_back("Z1_pt")
finalVariables.push_back("Z2_pt")


if __name__ == "__main__":
    ROOT.ROOT.EnableImplicitMT()
    thread_size = ROOT.ROOT.GetThreadPoolSize()
    print(">>> Thread pool size for parallel processing: {}".format(thread_size))

    for sample_name, final_states in samples.items():
        rdf = ROOT.RDataFrame("Events",base_path + sample_name +".root")
        for final_state in final_states:
            print(">>> Process sample: {} and final state {}".format(sample_name, final_state))
            start_time = time.time()

            rdf2 = skim_tools.EventSelection(rdf, final_state)
            rdf3 = skim_tools.FourVec(rdf2, final_state)
            rdf4 = skim_tools.OrderFourVec(rdf3, final_state)
            rdf5 = skim_tools.DefMassPt(rdf4)
            rdf6 = skim_tools.FourvecBoost(rdf5)
            rdf7 = skim_tools.DefAngles(rdf6)
            rdf_final = skim_tools.AddEventWeight(rdf7, sample_name)
            
            report = rdf_final.Report()
            rdf_final.Snapshot("Events", "skim_data/" + sample_name + final_state + "Skim.root", finalVariables)
            report.Print()
            print("Execution time: %s s" %(time.time() - start_time))
            print(rdf_final.GetColumnNames())