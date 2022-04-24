# Implementation of the plotting step of the analysis
#
# The plotting combines the histograms to plots which allow us to study the
# inital dataset based on observables motivated through physics.

import os
import ROOT
ROOT.gROOT.SetBatch(True)


# Declare a human-readable label for each variable on the plot axis
variable_labels = {
        "Higgs_mass": "Mass 4 leptons / GeV",
        "Z1_mass": "Mass Z_{1} / GeV",
        "Z2_mass": "Mass Z_{2} / GeV",
        "Z_close_mass": "Mass Z_{close} / GeV",
        "Z_far_mass": "Mass Z_{far} / GeV",
        "Higgs_pt": "Pt 4 leptons / GeV",
        "Z1_pt": "Pt Z_{1} / GeV",
        "Z2_pt": "Pt Z_{2} / GeV",
        "Z_close_pt": "Pt Z_{close} / GeV",
        "Z_far_pt": "Pt Z_{far} / GeV",
        "theta_star": "#theta*",
        "cos_theta_star": "cos #theta*",
        "Phi": "#Phi",
        "Phi1": "#Phi_{1}",
        "theta1": "#theta_{1}",
        "cos_theta1": "cos #theta_{1}",
        "theta2": "#theta_{2}",
        "cos_theta2": "cos #theta_{2}",
        }

# Retrieve a histogram from the input file based on the sample, the final state
# and the variable name
def GetHistogram(tfile, sample, final_state, variable):
    name = "{}_{}_{}".format(sample, final_state, variable)
    h = tfile.Get(name)
    if not h:
        raise Exception("Failed to load histogram {}.".format(name))
    return h

def CombineFinalStates(d):
    d["combined"] = d["FourMuons"].Clone()
    d["combined"].Add(d["FourElectrons"])
    d["combined"].Add(d["TwoMuonsTwoElectrons"])

def SetStyle():
    # Styles
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
        input.SetTitleSize(0.04, "XYZ")
        input.SetTitleOffset(1.2, "XYZ")

def AddTitle(input):
    input.GetXaxis().SetTitle(variable_labels[variable])
    input.GetYaxis().SetTitle("N_{Events}")

def AddLegend(legend, input_type, input):
    if input_type == "data": 
        legend.AddEntry(input, "Data", "lep")
    elif input_type == "background": 
        legend.AddEntry(input, "Z#gamma*, ZZ", "f")   
    elif input_type == "signal": 
        legend.AddEntry(input, "m_{H} = 125 GeV", "l")             
    legend.SetBorderSize(0)
    return legend


# Main function of the plotting step

# The plotting takes for each variable the histograms for each final state and sample
# and combines all signal and background processes, respectively. Then, the histgrams
# are plotted in a stacked manner overlain by the data points.
# This procedure is repeated with all final states combined to make the Higgs peak visible.



# Loop over all variable names and make a plot for each
if __name__ == "__main__":

    tfile = ROOT.TFile("histograms.root", "READ")
    SetStyle()

    for variable in variable_labels.keys():

        # Simulations
        signals = {}
        for final_state in ["FourMuons", "FourElectrons", "TwoMuonsTwoElectrons"]:
            signals[final_state] = GetHistogram(tfile, "SMHiggsToZZTo4L", final_state, variable)

        CombineFinalStates(signals)

        backgrounds = {}
        backgrounds["FourMuons"] = GetHistogram(tfile, "ZZTo4mu", "FourMuons", variable)
        backgrounds["FourElectrons"] = GetHistogram(tfile, "ZZTo4e", "FourElectrons", variable)
        backgrounds["TwoMuonsTwoElectrons"] = GetHistogram(tfile, "ZZTo2e2mu", "TwoMuonsTwoElectrons", variable)

        CombineFinalStates(backgrounds)

        # Data
        data = {}
        for final_state, samples in [
                    ["FourMuons", ["Run2012B_DoubleMuParked", "Run2012C_DoubleMuParked"]],
                    ["FourElectrons", ["Run2012B_DoubleElectron", "Run2012C_DoubleElectron"]],
                    ["TwoMuonsTwoElectrons", ["Run2012B_DoubleMuParked", "Run2012C_DoubleMuParked",
                                            "Run2012B_DoubleElectron", "Run2012C_DoubleElectron"]]
                ]:
            for sample in samples:
                h = GetHistogram(tfile, sample, final_state, variable)
                if not final_state in data:
                    data[final_state] = h
                else:
                    data[final_state].Add(h)

        CombineFinalStates(data)

        inputs_dict = {
            "data" : data,
            "background" : backgrounds,
            "signal" : signals,
            "total" : ["data", "background", "signal"]
        }

        for input_type, inputs in inputs_dict.items():        
            for final_state in ["FourMuons", "FourElectrons", "TwoMuonsTwoElectrons", "combined"]: 
                c = ROOT.TCanvas("", "", 600, 600)
                legend = ROOT.TLegend(0.6, 0.66, 0.90, 0.86)

                if input_type != "total":                 
                    input = inputs[final_state]       
                    InputStyle(input_type, input)
                    AddTitle(input)
                    input.SetMaximum(input.GetMaximum() * 1.4)
                    if input_type == "data": 
                        input.Draw("E1P")
                    elif input_type in ("background", "signal"): 
                        input.Draw("HIST")
                    legend=AddLegend(legend, input_type, input)
                    legend.Draw()
                
                else: 
                    signals[final_state].Add(backgrounds[final_state])
                    for input_key in inputs:
                        InputStyle(input_key, inputs_dict[input_key][final_state])
                        legend=AddLegend(legend, input_key, inputs_dict[input_key][final_state])

                    AddTitle(signals[final_state])
                    signals[final_state].SetMaximum(max(backgrounds[final_state].GetMaximum(),\
                                                     data[final_state].GetMaximum()) * 1.4)
                    signals[final_state].Draw("HIST")
                    backgrounds[final_state].Draw("HIST SAME")
                    data[final_state].Draw("E1P SAME")
                    legend.Draw()

                latex = ROOT.TLatex()
                latex.SetNDC()
                latex.SetTextSize(0.04)
                latex.SetTextFont(42)
                latex.DrawLatex(0.6, 0.935, "11.6 fb^{-1} (2012, 8 TeV)")
                latex.DrawLatex(0.16, 0.935, "#bf{CMS Open Data}")

                dir_name = os.path.join("plots", input_type)
                if not os.path.exists(dir_name):
                    os.makedirs(dir_name)
                    print("Directory " , dir_name ,  " Created ")
                c.SaveAs("{}/{}_{}_{}.png".format(dir_name, input_type, final_state, variable))
                
                

                    










