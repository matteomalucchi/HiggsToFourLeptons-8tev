"""
Implementation of the histogramming step of the analysis

The histogramming step produces histograms for each variable in each dataset.
Then, the resulting histograms are passed to the plotting
step, which combines them so that the physics of the decay can be studied.
"""
import os
import ROOT

from definitions.variables_def import VARIABLES 
from definitions.samples_def import  SAMPLES
from definitions.selections_def import  SELECTIONS

ROOT.gROOT.SetBatch(True)

def BookHistogram1D(rdf, variable, range_):
    """Book a histogram for a specific variable
    """
    return rdf.Histo1D(ROOT.ROOT.RDF.TH1DModel(variable, variable, range_[0], range_[1], range_[2]),\
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
    variables = VARIABLES.keys()

    for selection, names in SELECTIONS.items():
        """Loop through skimmed datasets and final states to produce histograms of all variables.
        """
        for sample, final_states in SAMPLES.items():
            for final_state in final_states:
                print(f">>> Process sample {sample} and final state {final_state} with {selection}")

                """Create dataframe of the skimmed dataset.
                """
                complete_name = os.path.join(names[0], f"{sample}{final_state}{names[1]}.root")
                rdf = ROOT.RDataFrame("Events", complete_name)

                """Book histograms and write them to output file.
                """
                histos = {}
                for variable in variables:
                    if len(VARIABLES[variable])>0:
                        histos[variable] = BookHistogram1D(rdf, variable, VARIABLES[variable])
                        WriteHistogram(histos[variable], f"{sample}_{final_state}_{variable}_{selection}")

    tfile.Close()


if __name__ == "__main__":
    main()