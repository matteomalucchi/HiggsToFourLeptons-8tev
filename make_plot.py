"""Implementation of the plotting step of the analysis

The plotting combines the histograms to plots which allow to study the
inital dataset based on observables motivated through physics.
"""
import os
import ROOT

from definitions.variables_def import VARIABLES
from definitions.selections_def import  SELECTIONS

ROOT.gROOT.SetBatch(True)

def GetHistogram(tfile, sample, final_state, variable, selection):
    """Retrieve a histogram from the input file based on the sample, the final state
    and the variable name
    """
    name = f"{sample}_{final_state}_{variable}_{selection}"
    h = tfile.Get(name)
    if not h:
        raise Exception("Failed to load histogram {}.".format(name))
    return h

def CombineFinalStates(d):
    """Combine the various final states
    """
    d["combined"] = d["FourMuons"].Clone()
    d["combined"].Add(d["FourElectrons"])
    d["combined"].Add(d["TwoMuonsTwoElectrons"])

def SetStyle():
    """Set the style of the plots.
    """
    ROOT.gStyle.SetOptStat(0)

    ROOT.gStyle.SetCanvasBorderMode(0)
    ROOT.gStyle.SetCanvasColor(ROOT.kWhite)
    ROOT.gStyle.SetCanvasDefH(600)
    ROOT.gStyle.SetCanvasDefW(600)
    ROOT.gStyle.SetCanvasDefX(0)
    ROOT.gStyle.SetCanvasDefY(0)

    ROOT.gStyle.SetPadTopMargin(0.08)
    ROOT.gStyle.SetPadBottomMargin(0.13)
    ROOT.gStyle.SetPadLeftMargin(0.16)
    ROOT.gStyle.SetPadRightMargin(0.05)

    ROOT.gStyle.SetHistLineColor(1)
    ROOT.gStyle.SetHistLineStyle(0)
    ROOT.gStyle.SetHistLineWidth(1)
    ROOT.gStyle.SetEndErrorSize(2)
    ROOT.gStyle.SetMarkerStyle(20)

    ROOT.gStyle.SetOptTitle(0)
    ROOT.gStyle.SetTitleFont(42)
    ROOT.gStyle.SetTitleColor(1)
    ROOT.gStyle.SetTitleTextColor(1)
    ROOT.gStyle.SetTitleFillColor(10)
    ROOT.gStyle.SetTitleFontSize(0.05)

    ROOT.gStyle.SetTitleColor(1, "XYZ")
    ROOT.gStyle.SetTitleFont(42, "XYZ")
    ROOT.gStyle.SetTitleSize(0.05, "XYZ")
    ROOT.gStyle.SetTitleXOffset(1.00)
    ROOT.gStyle.SetTitleYOffset(1.60)

    ROOT.gStyle.SetLabelColor(1, "XYZ")
    ROOT.gStyle.SetLabelFont(42, "XYZ")
    ROOT.gStyle.SetLabelOffset(0.007, "XYZ")
    ROOT.gStyle.SetLabelSize(0.04, "XYZ")

    ROOT.gStyle.SetAxisColor(1, "XYZ")
    ROOT.gStyle.SetStripDecimals(True)
    ROOT.gStyle.SetTickLength(0.03, "XYZ")
    ROOT.gStyle.SetNdivisions(510, "XYZ")
    ROOT.gStyle.SetPadTickX(1)
    ROOT.gStyle.SetPadTickY(1)

    ROOT.gStyle.SetPaperSize(20., 20.)
    ROOT.gStyle.SetHatchesLineWidth(5)
    ROOT.gStyle.SetHatchesSpacing(0.05)

    ROOT.TGaxis.SetExponentOffset(-0.08, 0.01, "Y")

def InputStyle(input_type, input):
    """Set style of the histograms for each type of dataset.
    """
    input.SetTitleSize(0.04, "XYZ")
    input.SetTitleOffset(1.3, "XYZ") 
    if input_type == "data": 
        input.SetMarkerStyle(20)
        input.SetLineColor(ROOT.kBlack)
    elif input_type == "background": 
        input.SetLineWidth(3)
        input.SetFillColor(ROOT.TColor.GetColor(100, 192, 232))
        input.SetLineColor(ROOT.TColor.GetColor(100, 192, 232))
    elif input_type == "signal": 
        input.SetLineColor(ROOT.kRed)
        input.SetLineWidth(3)

def AddTitle(input, variable):
    """Add the title to the plot.
    """
    input.GetXaxis().SetTitle(f"{VARIABLES[variable][3]}{VARIABLES[variable][4]}")
    bin_width=(VARIABLES[variable][2]-VARIABLES[variable][1])/VARIABLES[variable][0]
    input.GetYaxis().SetTitle(f"N_{{Events}} / {float(f'{bin_width:.1g}'):g}{VARIABLES[variable][4]}")

def AddLegend(legend, input_type, input):
    """Add the legend to the plot.
    """
    if input_type == "data": 
        legend.AddEntry(input, "Data", "lep")
    elif input_type == "background": 
        legend.AddEntry(input, "Z#gamma*, ZZ", "f")   
    elif input_type == "signal": 
        legend.AddEntry(input, "m_{H} = 125 GeV", "l")             
    legend.SetBorderSize(0)
    return legend

def AddLatex():
    """Write details on the plot.
    """
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.04)
    latex.SetTextFont(42)
    latex.DrawLatex(0.6, 0.935, "11.6 fb^{-1} (2012, 8 TeV)")
    latex.DrawLatex(0.16, 0.935, "#bf{CMS Open Data}")


def main ():
    """Main function of the plotting step.

    The plotting takes for each variable the histograms for each final state and sample.
    Then, the histograms are plotted with just the background, just the signal, just the data
    and finally, by combining all signal and background processes, in a stacked manner overlain
    by the data points. This procedure is repeated with all final states combined. 
    """   
    tfile = ROOT.TFile("histograms.root", "READ")

    SetStyle()

    for selection in SELECTIONS.keys():

        for variable in VARIABLES.keys():
            if variable != "Weight":
                    
                """Get histograms for the signal
                """
                signals = {}
                for final_state in ["FourMuons", "FourElectrons", "TwoMuonsTwoElectrons"]:
                    signals[final_state] = GetHistogram(tfile, "SMHiggsToZZTo4L", final_state, variable, selection)
                CombineFinalStates(signals)

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
                backgrounds["FourMuons"] = GetHistogram(tfile, "ZZTo4mu", "FourMuons", variable, selection)
                backgrounds["FourElectrons"] = GetHistogram(tfile, "ZZTo4e", "FourElectrons", variable, selection)
                backgrounds["TwoMuonsTwoElectrons"] = GetHistogram(tfile, "ZZTo2e2mu", "TwoMuonsTwoElectrons", variable, selection)
                CombineFinalStates(backgrounds)

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
                        h = GetHistogram(tfile, sample, final_state, variable, selection)
                        if not final_state in data:
                            data[final_state] = h
                        else:
                            data[final_state].Add(h)

                CombineFinalStates(data)

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
                        legend = ROOT.TLegend(0.66, 0.7, 0.9, 0.9)

                        if input_type in ["data", "background", "signal"]:                 
                            input = inputs[final_state]       
                            InputStyle(input_type, input)
                            AddTitle(input, variable)
                            input.SetMaximum(input.GetMaximum() * 1.4)
                            if input_type == "data": 
                                input.Draw("E1P")
                            elif input_type in ("background", "signal"): 
                                input.Draw("HIST")
                            legend=AddLegend(legend, input_type, input)
                            legend.Draw()

                        elif input_type == "sig_bkg_normalized":                 
                            bkg_norm = inputs[0][final_state]       
                            sig_norm = inputs[1][final_state]       
                            InputStyle("background", bkg_norm)
                            InputStyle("signal", sig_norm)
                            AddTitle(bkg_norm, variable)
                            bkg_norm.SetMaximum(max(bkg_norm.GetMaximum(), sig_norm.GetMaximum()) * 1.5)
                            bkg_norm.Draw("HIST")
                            sig_norm.Draw("HIST SAME")
                            legend=AddLegend(legend, "background", bkg_norm)
                            legend=AddLegend(legend, "signal", sig_norm)
                            legend.Draw()

                        elif input_type == "total":
                            """Add the background to the signal in order to compare it with the data.
                            """
                            signals[final_state].Add(backgrounds[final_state])
                            for input_key in inputs:
                                input=inputs_dict[input_key][final_state]
                                InputStyle(input_key, input)
                                legend=AddLegend(legend, input_key, input)

                            AddTitle(signals[final_state], variable)
                            signals[final_state].SetMaximum(max(backgrounds[final_state].GetMaximum(),\
                                                            data[final_state].GetMaximum()) * 1.4)
                            signals[final_state].Draw("HIST")
                            backgrounds[final_state].Draw("HIST SAME")
                            data[final_state].Draw("E1P SAME")
                            legend.Draw()

                        AddLatex()

                        """Create the directory and save the images.
                        """
                        dir_name = os.path.join("plots", selection, input_type)
                        if not os.path.exists(dir_name):
                            os.makedirs(dir_name)
                            print("Directory " , dir_name ,  " Created ")
                        file_name = f"{input_type}_{final_state}_{variable}.png"
                        complete_name = os.path.join(dir_name, file_name)
                        c.SaveAs(complete_name)


if __name__ == "__main__":
    main()
