import ROOT

from definitions.variables_def import VARIABLES_COMPLETE


def GetHistogram(tfile, dataset):
    """Retrieve a histogram from the histo file based on the sample, the final state
    and the variable name
    """
    h = tfile.Get(dataset)
    if not h:
        raise Exception(f"Failed to load histogram {dataset}.")
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

def InputStyle(input_type, histo):
    """Set style of the histograms for each type of dataset.
    """
    histo.SetTitleSize(0.04, "XYZ")
    histo.SetTitleOffset(1.3, "XYZ") 
    if input_type == "data": 
        histo.SetMarkerStyle(20)
        histo.SetLineColor(ROOT.kBlack)
    elif input_type == "background": 
        histo.SetLineWidth(3)
        histo.SetFillColor(ROOT.TColor.GetColor(100, 192, 232))
        histo.SetLineColor(ROOT.TColor.GetColor(100, 192, 232))
    elif input_type == "signal": 
        histo.SetLineColor(ROOT.kRed)
        histo.SetLineWidth(3)
    elif input_type == "data_el": 
        histo.SetMarkerStyle(22)
    elif input_type == "data_mu": 
        histo.SetMarkerStyle(20)
    elif input_type == "data_elmu": 
        histo.SetMarkerStyle(21)

def AddTitle(histo, variable=""):
    """Add the title to the plot.
    """
    if variable == "":
        histo.GetYaxis().SetTitle("K_{D}")
        histo.GetXaxis().SetTitle("m_{4l} [GeV]")    
    else:
        histo.GetXaxis().SetTitle(f"{VARIABLES_COMPLETE[variable][3]}{VARIABLES_COMPLETE[variable][4]}")
        bin_width=(VARIABLES_COMPLETE[variable][2]-VARIABLES_COMPLETE[variable][1])/VARIABLES_COMPLETE[variable][0]
        histo.GetYaxis().SetTitle(f"N_{{Events}} / {float(f'{bin_width:.1g}'):g}{VARIABLES_COMPLETE[variable][4]}")

def AddLegend(legend, histo, input_type="Discriminant"):
    """Add the legend to the plot.
    """

    if input_type == "Discriminant": 
        legend.AddEntry(histo["data_el"], "4e", "p")
        legend.AddEntry(histo["data_mu"], "4#mu", "p")
        legend.AddEntry(histo["data_elmu"], "2e2#mu", "p")

    elif input_type == "data": 
        legend.AddEntry(histo, "Data", "lep")

    elif input_type == "background": 
        legend.AddEntry(histo, "Z#gamma*, ZZ", "f")

    elif input_type == "signal": 
        legend.AddEntry(histo, "m_{H} = 125 GeV", "l")

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
