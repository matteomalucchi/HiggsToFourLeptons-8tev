"""Implementation of the plotting step of the analysis

The plotting combines the histograms to plots which allow to study the
inital dataset based on observables motivated through physics.
"""
import os
import sys
import argparse

import ROOT

sys.path.append('../')

from definitions.variables_def import VARIABLES_DICT
from definitions.selections_def import  SELECTIONS
from plotting import plotting_functions

ROOT.gROOT.SetBatch(True)


def make_plot (args, path=""):
    """Main function of the plotting step.

    The plotting takes for each variable the histograms for each final state and sample.
    Then, the histograms are plotted with just the background, just the signal, just the data
    and finally, by combining all signal and background processes, in a stacked manner overlain
    by the data points. This procedure is repeated with all final states combined. 
    """   
    
    print(f"\n>>> Executing {os.path.basename(__file__)}\n")

    infile_path = os.path.join(path, "histograms", "histograms.root")
    infile = ROOT.TFile(infile_path, "READ")

    plotting_functions.SetStyle()
    
    if args.ml :
        var_dict = VARIABLES_DICT["tot"]
    else : 
        var_dict = VARIABLES_DICT["part"]
        
    variables = var_dict.keys()

    for selection in SELECTIONS.keys():

        for variable in variables:
            if variable != "Weight":
                    
                """Get histograms for the signal
                """
                signals = {}
                for final_state in ["FourMuons", "FourElectrons", "TwoMuonsTwoElectrons"]:
                    signals[final_state] = plotting_functions.GetHistogram(infile, f"SMHiggsToZZTo4L_{final_state}_{variable}_{selection}")
                plotting_functions.CombineFinalStates(signals)

                """Get the normalized histograms for the signal
                """
                signals_norm = {}
                for final_state in signals.keys():
                    histo = signals[final_state].Clone()
                    histo.Scale(1/histo.Integral())
                    signals_norm[final_state] = histo

                """Get histograms for the background
                """
                backgrounds = {}
                backgrounds["FourMuons"] = plotting_functions.GetHistogram(infile, f"ZZTo4mu_FourMuons_{variable}_{selection}")
                backgrounds["FourElectrons"] = plotting_functions.GetHistogram(infile, f"ZZTo4e_FourElectrons_{variable}_{selection}")
                backgrounds["TwoMuonsTwoElectrons"] = plotting_functions.GetHistogram(infile, f"ZZTo2e2mu_TwoMuonsTwoElectrons_{variable}_{selection}")
                plotting_functions.CombineFinalStates(backgrounds)

                """Get the normalized histograms for the background
                """
                backgrounds_norm = {}
                for final_state in backgrounds.keys():
                    histo = backgrounds[final_state].Clone()
                    histo.Scale(1/histo.Integral())
                    backgrounds_norm[final_state] = histo

                """Get histograms for the data
                """
                data = {}
                for final_state, samples in [
                            ["FourMuons", ["Run2012B_DoubleMuParked", "Run2012C_DoubleMuParked"]],
                            ["FourElectrons", ["Run2012B_DoubleElectron", "Run2012C_DoubleElectron"]],
                            ["TwoMuonsTwoElectrons", ["Run2012B_DoubleMuParked", "Run2012C_DoubleMuParked",
                                                    "Run2012B_DoubleElectron", "Run2012C_DoubleElectron"]]
                        ]:
                    for sample in samples:
                        h = plotting_functions.GetHistogram(infile, f"{sample}_{final_state}_{variable}_{selection}")
                        if not final_state in data:
                            data[final_state] = h
                        else:
                            data[final_state].Add(h)

                plotting_functions.CombineFinalStates(data)

                """ Dictionary for the different types of datasets
                """
                inputs_dict = {
                    "data" : data,
                    "background" : backgrounds,
                    "signal" : signals,
                    "sig_bkg_normalized" : [backgrounds_norm, signals_norm],
                    "total" : ["data", "background", "signal"]
                }
                
                """Loop over the types of datasets and the final states
                """
                for input_type, inputs in inputs_dict.items():        
                    for final_state in ["FourMuons", "FourElectrons", "TwoMuonsTwoElectrons", "combined"]: 
                        c = ROOT.TCanvas("", "", 600, 600)
                        legend = ROOT.TLegend(0.5, 0.7, 0.8, 0.9)
                        legend.SetBorderSize(0)

                        if input_type in ["data", "background", "signal"]:                 
                            input = inputs[final_state]       
                            plotting_functions.InputStyle(input_type, input)
                            plotting_functions.AddTitle(input, variable)
                            input.SetMaximum(input.GetMaximum() * 1.4)
                            if input_type == "data": 
                                input.Draw("E1P")
                            elif input_type in ("background", "signal"): 
                                input.Draw("HIST")
                            legend=plotting_functions.AddLegend(legend, input_type, input)
                            legend.Draw()

                        elif input_type == "sig_bkg_normalized":                 
                            bkg_norm = inputs[0][final_state]       
                            sig_norm = inputs[1][final_state]       
                            plotting_functions.InputStyle("background", bkg_norm)
                            plotting_functions.InputStyle("signal", sig_norm)
                            plotting_functions.AddTitle(bkg_norm, variable)
                            bkg_norm.SetMaximum(max(bkg_norm.GetMaximum(), sig_norm.GetMaximum()) * 1.5)
                            bkg_norm.Draw("HIST")
                            sig_norm.Draw("HIST SAME")
                            legend=plotting_functions.AddLegend(legend, "background", bkg_norm)
                            legend=plotting_functions.AddLegend(legend, "signal", sig_norm)
                            legend.Draw()

                        elif input_type == "total":
                            """Add the background to the signal in order to compare it with the data.
                            """
                            signals[final_state].Add(backgrounds[final_state])
                            for input_key in inputs:
                                input=inputs_dict[input_key][final_state]
                                plotting_functions.InputStyle(input_key, input)
                                legend=plotting_functions.AddLegend(legend, input_key, input)

                            plotting_functions.AddTitle(signals[final_state], variable)
                            signals[final_state].SetMaximum(max(backgrounds[final_state].GetMaximum(),\
                                                            data[final_state].GetMaximum()) * 1.4)
                            signals[final_state].Draw("HIST")
                            backgrounds[final_state].Draw("HIST SAME")
                            data[final_state].Draw("E1P SAME")
                            legend.Draw()

                        plotting_functions.AddLatex()

                        # Create the directory and save the images.
                        dir_name = os.path.join(path, "plots", selection, input_type)
                        if not os.path.exists(dir_name):
                            os.makedirs(dir_name)
                            print("Directory " , dir_name ,  " Created ")
                        file_name = f"{input_type}_{final_state}_{variable}.pdf"
                        complete_name = os.path.join(dir_name, file_name)
                        c.SaveAs(complete_name)


if __name__ == "__main__":
    # global configuration
    parser = argparse.ArgumentParser( description = 'Analysis Tool' )
    parser.add_argument('-p', '--parallel',   default=False,   action='store_const',     const=True, help='enables running in parallel')
    parser.add_argument('-n', '--nWorkers',   default=0,                                 type=int,   help='number of workers' )  
    args = parser.parse_args()
    
    make_plot(args, "..")
