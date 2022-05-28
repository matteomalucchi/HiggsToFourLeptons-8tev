"""In this step two 2D scatter plots of Higgs_mass vs Discriminant 
are created, one for the simulated background and one for the 
simulated signal. Each plot contains both the combination 
of all background/signal datasets and the real data 
separated in the three possible final states.
"""

import os
import ROOT

#ROOT.gROOT.SetBatch(True)
import sys

sys.path.append('../')
from plotting import plotting_functions


'''def GetHistogram(infile, dataset):
    """Retrieve a histogram from the input file based on the sample, the final state
    and the variable name
    """
    h = infile.Get(dataset)
    if not h:
        raise Exception(f"Failed to load histogram {dataset}.")
    return h


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
    ROOT.gStyle.SetPadLeftMargin(0.13)
    ROOT.gStyle.SetPadRightMargin(0.13)

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

def InputStyle(dataset, histo):
    """Set style of the histograms for each type of dataset.
    """
    histo.SetTitleSize(0.04, "XYZ")
    histo.SetTitleOffset(1.2, "XYZ")

    if dataset == "data_el": 
        histo.SetMarkerStyle(22)
    elif dataset == "data_mu": 
        histo.SetMarkerStyle(20)
    elif dataset == "data_elmu": 
        histo.SetMarkerStyle(21)


def AddTitle(histo):
    """Add the title to the plot.
    """
    histo.GetYaxis().SetTitle("K_{D}")
    histo.GetXaxis().SetTitle("m_{4l} [GeV]")

def AddLegend(legend, histos):
    """Add the legend to the plot.
    """
    legend.AddEntry(histos["data_el"], "4e", "p")
    legend.AddEntry(histos["data_mu"], "4#mu", "p")
    legend.AddEntry(histos["data_elmu"], "2e2#mu", "p")            
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
'''

def main ():
    """Main function of the plotting step.

    The plotting takes for each variable the histograms for each final state and sample.
    Then, the histograms are plotted with just the background, just the signal, just the data
    and finally, by combining all signal and background processes, in a stacked manner overlain
    by the data points. This procedure is repeated with all final states combined. 
    """   

    infile_path = os.path.join("..", "histograms_discriminant.root")
    infile = ROOT.TFile(infile_path, "READ")

    datasets = ["signal", "background", "data_el", "data_mu", "data_elmu"]
        
    plotting_functions.SetStyle()
    histos = {}

    for dataset in datasets:
        """Get histograms for the signal
        """
        histos[dataset] = plotting_functions.GetHistogram(infile, dataset)
        plotting_functions.InputStyle(dataset, histos[dataset])

    for type in ["signal", "background"]:

        c = ROOT.TCanvas("", "", 600, 600)
        legend = ROOT.TLegend(0.75, 0.8, 0.85, 0.9)

        plotting_functions.AddTitle(histos[type])
        histos[type].Scale(1/histos[type].GetMaximum())
        histos[type].Draw("COLZ")
        histos["data_el"].Draw("SAME P") 
        histos["data_mu"].Draw("SAME P") 
        histos["data_elmu"].Draw("SAME P") 

        legend=plotting_functions.AddLegend(legend, histos)
        legend.Draw()

        plotting_functions.AddLatex()

        """Create the directory and save the images.
        """
        dir_name = os.path.join("..", "discriminant_plots")
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print("Directory " , dir_name ,  " Created ")
        file_name = f"discriminant_{type}.png"
        complete_name = os.path.join(dir_name, file_name)
        input()
        c.SaveAs(complete_name)

if __name__ == "__main__":
    main()

                    
                

                    










