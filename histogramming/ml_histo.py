"""
In this step 2D histograms of Higgs_mass vs Discriminant 
are created, one for the combination of all the simulated background,
one for all the simulated signal and one for each possible final state
of the data.
"""

import sys
import os
import argparse

import ROOT

sys.path.append('../')
from definitions.samples_def import SAMPLES
from histogramming import histogramming_functions


def ml_histo(args, path = ""):
    """Main function of the histogramming step that plots Higgs_mass vs DNNDiscriminant.
    
    The function produces the required histogram for the final plotting step.
    """

    print(f"\n>>> Executing {os.path.basename(__file__)}\n")

    #Enamble multi-threading
    if args.parallel:
        ROOT.ROOT.EnableImplicitMT(args.nWorkers)
        thread_size = ROOT.ROOT.GetThreadPoolSize()
        print(f">>> Thread pool size for parallel processing: {thread_size}")


    # Create the directory and the output file to store the histograms
    dir_name = os.path.join(path, "histograms")
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        print("Directory " , dir_name ,  " Created ")
    outfile_path = os.path.join(dir_name, "histograms_discriminant.root")

    outfile = ROOT.TFile(outfile_path, "RECREATE")

    sig_chain= ROOT.TChain("Events")
    bkg_chain= ROOT.TChain("Events")
    data_el_chain= ROOT.TChain("Events")
    data_mu_chain= ROOT.TChain("Events")
    data_elmu_chain= ROOT.TChain("Events")

    for sample_name, final_states in SAMPLES.items():
        for final_state in final_states:
            print(f">>> Process sample {sample_name} and final state {final_state}")

            # Get the input file name
            infile_name=f"{sample_name}{final_state}Skim.root"
            infile_path = os.path.join(path, "skim_data", infile_name)

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
    
    # General configuration
    parser = argparse.ArgumentParser( description = 'Analysis Tool' )
    parser.add_argument('-p', '--parallel',   default=False,   action='store_const',     const=True, help='enables running in parallel')
    parser.add_argument('-n', '--nWorkers',   default=0,                                 type=int,   help='number of workers' )  
    args = parser.parse_args()
    
    ml_histo(args, "..")