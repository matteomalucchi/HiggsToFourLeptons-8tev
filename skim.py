#skimming process

import time

import ROOT


import skim_tools

#base path

#BASE_PATH = "root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/ForHiggsTo4Leptons/"

BASE_PATH = "data/"

#various datasets

SAMPLES={
    "SMHiggsToZZTo4L": ["FourMuons", "FourElectrons", "TwoMuonsTwoElectrons"],
    "ZZTo4mu": ["FourMuons"],
    "ZZTo4e": ["FourElectrons"],
    "ZZTo2e2mu": ["TwoMuonsTwoElectrons"],
    "Run2012B_DoubleMuParked": ["FourMuons", "TwoMuonsTwoElectrons"],
    "Run2012C_DoubleMuParked": ["FourMuons", "TwoMuonsTwoElectrons"],
    "Run2012B_DoubleElectron": ["FourElectrons", "TwoMuonsTwoElectrons"],
    "Run2012C_DoubleElectron": ["FourElectrons", "TwoMuonsTwoElectrons"]
}

FINAL_VARIABLES = ROOT.vector("std::string")()
FINAL_VARIABLES.push_back("run")
FINAL_VARIABLES.push_back("Weight")
FINAL_VARIABLES.push_back("Higgs_mass")
FINAL_VARIABLES.push_back("Z1_mass")
FINAL_VARIABLES.push_back("Z2_mass")
FINAL_VARIABLES.push_back("Z_close_mass")
FINAL_VARIABLES.push_back("Z_far_mass")
FINAL_VARIABLES.push_back("Higgs_pt")
FINAL_VARIABLES.push_back("Z1_pt")
FINAL_VARIABLES.push_back("Z2_pt")
FINAL_VARIABLES.push_back("Z_close_pt")
FINAL_VARIABLES.push_back("Z_far_pt")
FINAL_VARIABLES.push_back("theta_star")
FINAL_VARIABLES.push_back("cos_theta_star")
FINAL_VARIABLES.push_back("Phi")
FINAL_VARIABLES.push_back("Phi1")
FINAL_VARIABLES.push_back("theta1")
FINAL_VARIABLES.push_back("cos_theta1")
FINAL_VARIABLES.push_back("theta2")
FINAL_VARIABLES.push_back("cos_theta2")


if __name__ == "__main__":
    ROOT.ROOT.EnableImplicitMT()
    thread_size = ROOT.ROOT.GetThreadPoolSize()
    print(">>> Thread pool size for parallel processing: {}".format(thread_size))

    for sample_name, final_states in SAMPLES.items():
        rdf = ROOT.RDataFrame("Events", BASE_PATH + sample_name +".root")
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
            rdf_final.Snapshot("Events", "skim_data/" + sample_name +\
                               final_state + "Skim.root", FINAL_VARIABLES)
            report.Print()
            print("Execution time: %s s" %(time.time() - start_time))
            #print(rdf_final.GetColumnNames())