""" Definitions of the functions used in the plotting step of the analysis.
"""

import ROOT


def get_histogram(tfile, dataset):
    """Retrieve a histogram from the histo file based on the sample,
    the final state and the variable name.

    :param tfile: File containing the histogram
    :type tfile: ROOT.TFile
    :param dataset: Name of the histogram
    :type dataset: str
    :raises RuntimeError: Raised when the histogram can't be loaded
    :return: Retrieved histogram
    :rtype: ROOT.TH1D
    """

    histo = tfile.Get(dataset)
    if not histo:
        raise RuntimeError(f"Failed to load histogram {dataset}")
    return histo

def combine_final_states(dict_comb):
    """Combine the various final states in a unique histogram.

    :param dict_comb: Dictionary in which the values are the histograms to be combined
    :type dict_comb: dict(str, ROOT.TH1D)
    """

    dict_comb["Combined"] = dict_comb["FourMuons"].Clone()
    dict_comb["Combined"].Add(dict_comb["FourElectrons"])
    dict_comb["Combined"].Add(dict_comb["TwoMuonsTwoElectrons"])


def set_style():
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
    ROOT.gStyle.SetPadRightMargin(0.12)

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
    ROOT.gStyle.SetTitleYOffset(1.00)

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

    ROOT.gROOT.ForceStyle()

def input_style(input_type, histo):
    """Set style of the histograms for each type of dataset.

    :param input_type: Type of input dataset
    :type input_type: str
    :param histo: Histogram of which the style is set
    :type histo: ROOT.TH1D
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

def add_title(histo, variable_specs=None):
    """Add the title to the plot axes.

    :param histo: Histogram of which the plot axes need to be titled
    :type histo: ROOT.TH1D
    :param variable_specs: Specifics of the variable to be plotted
    :type variable_specs: str
    """

    if variable_specs is None:
        histo.GetYaxis().SetTitle("DNN Discriminant")
        histo.GetXaxis().SetTitle("m_{4l} [GeV]")
    else:
        histo.GetXaxis().SetTitle(f"{variable_specs[3]}{variable_specs[4]}")
        bin_width=(variable_specs[2]-variable_specs[1])/variable_specs[0]
        histo.GetYaxis().SetTitle(f"N_{{Events}} / {float(f'{bin_width:.1g}'):g}{variable_specs[4]}")

def add_legend(legend, input_type, histo=None):
    """Add the legend to the plot.

    :param legend: Legend to be added
    :type legend: ROOT.TLegend
    :param input_type: Type of input dataset
    :type input_type: str
    :param histo: Histogram of which the plot
        needs to have added te legend
    :type histo: ROOT.TH1D
    :return: Completed legend
    :rtype: ROOT.TLegend
    """

    if input_type == "discriminant":
        try:
            legend.AddEntry(histo["data_el"], "4e", "p")
        except KeyError:
            pass
        try:
            legend.AddEntry(histo["data_mu"], "4#mu", "p")
        except KeyError:
            pass
        try:
            legend.AddEntry(histo["data_elmu"], "2e2#mu", "p")
        except KeyError:
            pass

    elif input_type == "data":
        legend.AddEntry(histo, "Data", "lep")

    elif input_type == "background":
        legend.AddEntry(histo, "Z#gamma*, ZZ", "f")

    elif input_type == "signal":
        legend.AddEntry(histo, "m_{H} = 125 GeV", "l")

    elif input_type == "fit":
        legend.AddEntry("bkg_kde","Background KDE", "l")
        legend.AddEntry("CBHiggs_data","Data CB", "l")
        legend.AddEntry("totPDF","Data CB + Background KDE", "l")
        legend.AddEntry("data","Data", "lep")

    return legend

def add_latex():
    """Write details on the plot.
    """
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.04)
    latex.SetTextFont(42)
    latex.DrawLatex(0.6, 0.935, "11.6 fb^{-1} (2012, 8 TeV)")
    latex.DrawLatex(0.16, 0.935, "#bf{CMS Open Data}")
