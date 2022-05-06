"""
Implementation of the histogramming step of the analysis

The histogramming step produces histograms for each variable in each dataset.
Then, the resulting histograms are passed to the plotting
step, which combines them so that the physics of the decay can be studied.
"""

import ROOT

from definitions.variables_def import VARIABLES_FEATURES 
from definitions.samples_def import  SAMPLES

ROOT.gROOT.SetBatch(True)

def BookHistogram(df, variable, range_):
    """Book a histogram for a specific variable
    """
    return df.Histo1D(ROOT.ROOT.RDF.TH1DModel(variable, variable, range_[0], range_[1], range_[2]),\
                      variable, "Weight")

def WriteHistogram(h, name):
    """Write a histogram with a given name in the output file
    """
    h.SetName(name)
    h.Write()


def main():
    """Main function of the histogramming step
    
    The function loops over the outputs from the skimming step and produces the
    required histograms for the final plotting step.
    """

    """Enamble multi-threading
    """
    ROOT.ROOT.EnableImplicitMT()
    poolSize = ROOT.ROOT.GetThreadPoolSize()
    print(">>> Thread pool size for parallel processing: {}".format(poolSize))

    """Create output file.
    """
    tfile = ROOT.TFile("histograms.root", "RECREATE")
    variables = VARIABLES_FEATURES.keys()

    """Loop through skimmed datasets and final states to produce histograms of all variables.
    """
    for sample, final_states in SAMPLES.items():
        for final_state in final_states:
            print(">>> Process skimmed sample {} and final state {}".format(sample, final_state))

            """Create dataframe of the skimmed dataset.
            """
            rdf = ROOT.ROOT.RDataFrame("Events", "skim_data/" + sample + final_state + "Skim.root")

            """Book histograms and write them to output file.
            """
            hists = {}
            for variable in variables:
                if len(VARIABLES_FEATURES[variable])>0:
                    hists[variable] = BookHistogram(rdf, variable, VARIABLES_FEATURES[variable])
                    WriteHistogram(hists[variable], "{}_{}_{}".format(sample, final_state, variable))

    tfile.Close()


if __name__ == "__main__":
    main()