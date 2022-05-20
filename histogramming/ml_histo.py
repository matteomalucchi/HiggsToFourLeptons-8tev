"""
In this step 2D histograms of Higgs_mass vs Discriminant 
are created, one for the combination of all the simulated background,
one for all the simulated signal and one for each possible final state
of the data.
"""
import sys
import os
import ROOT

sys.path.append('../')
from definitions.samples_def import SAMPLES

from histogramming import histogramming_functions

ROOT.gROOT.SetBatch(True)


def main(base_directory = ""):

    """Enamble multi-threading
    """
    ROOT.ROOT.EnableImplicitMT()
    poolSize = ROOT.ROOT.GetThreadPoolSize()
    print(">>> Thread pool size for parallel processing: {}".format(poolSize))

    # Create output file to store the histograms
    #outfile_path = os.path.join("..", "histograms_discriminant.root")
    outfile_path = f"{base_directory}histograms_discriminant.root"

    outfile = ROOT.TFile(outfile_path, "RECREATE")

    sig_chain= ROOT.TChain("Events")
    bkg_chain= ROOT.TChain("Events")
    data_el_chain= ROOT.TChain("Events")
    data_mu_chain= ROOT.TChain("Events")
    data_elmu_chain= ROOT.TChain("Events")

    for sample_name, final_states in SAMPLES.items():
        for final_state in final_states:
            print(">>> Process sample {} and final state {}".format(sample_name, final_state))

            # Get the input file name
            infile_name=f"{sample_name}{final_state}Skim.root"
            infile_directory = f"{base_directory}skim_data"
            infile_path = os.path.join(infile_directory, infile_name)

            if sample_name.startswith("SM"):
                sig_chain.Add(infile_path)

            elif sample_name.startswith("ZZ"):
                bkg_chain.Add(infile_path)

            elif sample_name.startswith("Run"):
                if final_state == "FourElectrons":
                    data_el_chain.Add(infile_path)
                elif final_state == "FourMuons":
                    data_mu_chain.Add(infile_path)
                elif final_state == "TwoMuonsTwoElectrons":
                    data_elmu_chain.Add(infile_path)

    sig_rdf = ROOT.ROOT.RDataFrame(sig_chain)
    bkg_rdf = ROOT.RDataFrame(bkg_chain)
    data_el_rdf = ROOT.RDataFrame(data_el_chain)
    data_mu_rdf = ROOT.RDataFrame(data_mu_chain)
    data_elmu_rdf = ROOT.RDataFrame(data_elmu_chain)
    
    rdfs = {
        "signal" : sig_rdf, 
        "background" : bkg_rdf, 
        "data_el" : data_el_rdf, 
        "data_mu" : data_mu_rdf,
        "data_elmu" :  data_elmu_rdf
    }

    histos = {}
    variables = ["Higgs_mass", "Discriminant"]
    ranges_x = [40, 100., 180.]
    ranges_y = [40, -0.03, 1]
    for dataset, rdf in rdfs.items():
        print(f">>> Process sample: {dataset}")
        histos[dataset] = histogramming_functions.BookHistogram2D(dataset, rdf, variables, ranges_x, ranges_y)
        histogramming_functions.WriteHistogram(histos[dataset], dataset)

    outfile.Close()
    
  
if __name__ == "__main__":
    
    base_directory = "../"
    main(base_directory)