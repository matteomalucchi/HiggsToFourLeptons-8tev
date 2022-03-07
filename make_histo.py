# Implementation of the histogramming step of the analysis
#
# The histogramming step produces histograms for each variable in the dataset
# and for each physics process resulting into the final state with a combination
# of muons and a electrons. Then, the resulting histograms are passed to the plotting
# step, which combines the histograms so that we can study the physics of the decay.


import ROOT
import math

import skim 

ROOT.gROOT.SetBatch(True)


# Declare the range of the histogram for each variable
#
# Each entry in the dictionary contains of the variable name as key and a tuple
# specifying the histogram layout as value. The tuple sets the number of bins,
# the lower edge and the upper edge of the histogram.
ranges = {
        "Higgs_mass": (36, 70, 180),
        "Z1_mass": (36, 40, 160),
        "Z2_mass": (36, 12, 160),
        "Higgs_pt": (36, 0, 100),
        "Z1_pt": (36, 0, 100),
        "Z2_pt": (36, 0, 100),
        "theta_star": (36, 0, math.pi),
        "Phi": (36, -math.pi, math.pi),
        "Phi1": (36, -math.pi, math.pi),
        "theta1": (36, 0, math.pi),
        "theta2": (36, 0, math.pi),
        }

"""ranges = {
        "Higgs_mass": (36, 70, 180),
        "Z1_mass": (36, 40, 160),
        "Z2_mass": (36, 12, 160),
        "Higgs_pt": (36, 0, 100),
        "Z1_pt": (36, 0, 100),
        "Z2_pt": (36, 0, 100),
        "theta_star": (64, -4, 4),
        "Phi": (64, -4, 4),
        "Phi1": (64, -4, 4),
        "theta1": (64, -4, 4),
        "theta2": (64, -4, 4),
        }"""

# Book a histogram for a specific variable
def BookHistogram(df, variable, range_):
    return df.Histo1D(ROOT.ROOT.RDF.TH1DModel(variable, variable, range_[0], range_[1], range_[2]),\
                      variable, "Weight")


# Write a histogram with a given name to the output ROOT file
def WriteHistogram(h, name):
    h.SetName(name)
    h.Write()

# Main function of the histogramming step
#
# The function loops over the outputs from the skimming step and produces the
# required histograms for the final plotting.
def main():
    # Set up multi-threading capability of ROOT
    ROOT.ROOT.EnableImplicitMT()
    poolSize = ROOT.ROOT.GetThreadPoolSize()
    print(">>> Thread pool size for parallel processing: {}".format(poolSize))

    # Create output file
    tfile = ROOT.TFile("histograms.root", "RECREATE")
    variables = ranges.keys()

    # Loop through skimmed datasets and final states to produce histograms of all variables
    for sample, final_states in skim.samples.items():
        for final_state in final_states:
            print(">>> Process skimmed sample {} and final state {}".format(sample, final_state))

            # Make dataframe of the skimmed dataset
            rdf = ROOT.ROOT.RDataFrame("Events", "skim_data/" + sample + final_state + "Skim.root")
            # Book histograms
            hists = {}
            for variable in variables:
                hists[variable] = BookHistogram(rdf, variable, ranges[variable])

            # Write histograms to output file
            for variable in variables:
                WriteHistogram(hists[variable], "{}_{}_{}".format(sample, final_state, variable))

    tfile.Close()


if __name__ == "__main__":
    main()
