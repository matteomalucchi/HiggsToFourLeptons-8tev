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


#event weights for MC
integrated_luminosity = 11.58 * 1000.0
scale_factor_ZZ_4l = 1.386
event_weights = {
	"SMHiggsToZZTo4L", 0.0065 / 299973.0 * integrated_luminosity,
	"ZZTo4mu", 0.077 / 1499064.0 * scale_factor_ZZ_4l * integrated_luminosity,
	"ZZTo4e", 0.077 / 1499093.0 * scale_factor_ZZ_4l * integrated_luminosity,
	"ZZTo2e2mu", 0.18 / 1497445.0 * scale_factor_ZZ_4l * integrated_luminosity,
	"Run2012B_DoubleMuParked", 1.0,
	"Run2012C_DoubleMuParked", 1.0,
	"Run2012B_DoubleElectron", 1.0,
	"Run2012C_DoubleElectron", 1.0
}





if __name__ == "__main__":

	"""	ROOT.ROOT.EnableImplicitMT()
	thread_size = ROOT.ROOT.GetThreadPoolSize()
	print(">>> Thread pool size for parallel processing: {}".format(thread_size))"""

	for sample_name, final_states in samples.items():
		rdf = ROOT.RDataFrame("Events",base_path + sample_name +".root").Range(1000)

		for final_state in final_states:
			if sample_name== "SMHiggsToZZTo4L" : print(">>> Process sample: {} and final state {}".format(sample_name, final_state))
			start_time = time.time()

			rdf2 = func.eventSelection(rdf, final_state)
			report = rdf2.Report()
			rdf3 = func.fourVec(rdf2, final_state)
			#print(rdf3.GetColumnNames())

			if sample_name== "SMHiggsToZZTo4L" : 
				report.Print()
				print("Execution time: %s s" %(time.time() - start_time))