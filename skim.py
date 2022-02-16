#skimming process

import ROOT
import time


import func

#base path

#base_path = "root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/ForHiggsTo4Leptons/"

base_path = "../HiggsToFourLeptonsNanoAODOutreachAnalysis/data/"

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
finalVariables.push_back("Higgs_fourvec")
finalVariables.push_back("Z1_fourvec")
finalVariables.push_back("Z2_fourvec")
finalVariables.push_back("Lep11_fourvec")
finalVariables.push_back("Lep12_fourvec")
finalVariables.push_back("Lep21_fourvec")
finalVariables.push_back("Lep22_fourvec")

if __name__ == "__main__":
    ROOT.ROOT.EnableImplicitMT()
    thread_size = ROOT.ROOT.GetThreadPoolSize()
    print(">>> Thread pool size for parallel processing: {}".format(thread_size))

    for sample_name, final_states in samples.items():
        rdf = ROOT.RDataFrame("Events",base_path + sample_name +".root")
        for final_state in final_states:
            print(">>> Process sample: {} and final state {}".format(sample_name, final_state))
            start_time = time.time()

            rdf2 = func.EventSelection(rdf, final_state)
            rdf3 = func.FourVec(rdf2, final_state)
            rdf4 = func.OrderFourVec(rdf3, final_state)
            rdf_final = func.AddEventWeight(rdf4, sample_name)
            
            report = rdf_final.Report()
            rdf_final.Snapshot("Events", "skim_data/" + sample_name + final_state + "Skim.root", finalVariables)
            report.Print()
            print("Execution time: %s s" %(time.time() - start_time))
            #print(rdf_final.GetColumnNames())