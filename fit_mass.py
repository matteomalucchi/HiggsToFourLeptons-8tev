import os
import ROOT
from definitions.samples_def import SAMPLES


def main ():

    sig_chain= ROOT.TChain("Events")
    bkg_chain= ROOT.TChain("Events")
    data_chain= ROOT.TChain("Events")

    for sample_name, final_states in SAMPLES.items():
        for final_state in final_states:
            print(">>> Process sample {} and final state {}".format(sample_name, final_state))

            # Get the input file name
            infile_name=f"{sample_name}{final_state}Skim.root"
            infile_directory = f"skim_data"
            infile_path = os.path.join(infile_directory, infile_name)

            if sample_name.startswith("SM"):
                sig_chain.Add(infile_path)

            elif sample_name.startswith("ZZ"):
                bkg_chain.Add(infile_path)

            elif sample_name.startswith("Run"):
                data_chain.Add(infile_path)

    m4l = ROOT.RooRealVar("Higgs_mass","4 leptons invariant mass", 110, 140,"GeV")
    weight = ROOT.RooRealVar("Weight","Weight", 0, 1,"GeV")

    sig = ROOT.RooDataSet("signal", "", sig_chain, ROOT.RooArgSet(m4l, weight) )
    bkg = ROOT.RooDataSet("background", "", bkg_chain, ROOT.RooArgSet(m4l, weight) )
    data = ROOT.RooDataSet("data", "", data_chain, ROOT.RooArgSet(m4l, weight) )

    #Calculate signal fraction
    sig_frac_count = sig.sumEntries()/(sig.sumEntries()+bkg.sumEntries())
    bkg_frac_count = bkg.sumEntries()/(sig.sumEntries()+bkg.sumEntries())
    
    #KDE for background. In this configuration the input data
    #is mirrored over the right boundary to minimize edge effects in distribution
    #that do not fall to zero towards the right edge
    bkg_kde = ROOT.RooKeysPdf("bkg_kde", "bkg_kde", m4l, bkg, ROOT.RooKeysPdf.MirrorRight)

    #Parameters and model for the fit of the simulated signal samples
    meanHiggs_sig = ROOT.RooRealVar("meanHiggs_sig", "The mean of the Higgs CB for the signal", 125, 115, 135, "GeV")
    sigmaHiggs = ROOT.RooRealVar("sigmaHiggs_sig", "The width of Higgs CB for the signal", 5, 0., 20, "GeV")
    alphaHiggs = ROOT.RooRealVar("alphaHiggs_sig", "The tail of Higgs CB for the signal", 1.5, -5, 5)
    nHiggs = ROOT.RooRealVar("nHiggs_sig", "The normalization of Higgs CB for the signal", 1.5, 0, 10)
    CBHiggs_sig = ROOT.RooCBShape("CBHiggs_sig","The Higgs Crystall Ball for the signal",m4l,meanHiggs_sig,sigmaHiggs,alphaHiggs,nHiggs)
    #Unbinned ML fit to signal
    fitHiggs = CBHiggs_sig.fitTo(sig, ROOT.RooFit.Save(True), ROOT.RooFit.AsymptoticError(True))
    
    fitHiggs.Print("v")
    #Parameters and model for data fit
    meanHiggs_data = ROOT.RooRealVar("m_{H}", "The mean of the Higgs CB for the data", 125, 115, 135, "GeV")

    CBHiggs_data = ROOT.RooCBShape("CBHiggs_data","The Higgs Crystall Ball for the data",m4l,meanHiggs_data,sigmaHiggs,alphaHiggs,nHiggs)
    #sigfrac= ROOT.RooRealVar("sigfrac", "fraction signal fraction", 0.8, 0., 1.)
    sig_frac= ROOT.RooRealVar("sigfrac", "fraction signal fraction", sig_frac_count)
    sig_coeff= ROOT.RooRealVar("sig_coeff", "fraction signal fraction", 1)
    bkg_frac= ROOT.RooRealVar("bkg_coeff", "fraction bkg fraction", bkg_frac_count)

    totPDF = ROOT.RooAddPdf("totPDF", "Higgs_data+bkg", ROOT.RooArgList(CBHiggs_data, bkg_kde), ROOT.RooArgList(sig_frac,bkg_frac))
    #Unbinned ML fit to data
    fitdata = totPDF.fitTo(data, ROOT.RooFit.Save(True))
    fitdata.Print("v")
    print("Fraction sig/bkg is:")
    print( sig_frac_count)
    print("Fraction bkg/sig is:")
    print( bkg_frac_count)


    meanHiggs_sig.Print()
    meanHiggs_data.Print()
    sigmaHiggs.Print()
    alphaHiggs.Print()
    nHiggs.Print()

    
    m4l.setBins(10)
    xframe = m4l.frame()
    data.plotOn(xframe)
    totPDF.plotOn(xframe, ROOT.RooFit.Components("bkg_kde"), ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kRed))
    totPDF.plotOn(xframe, ROOT.RooFit.Components("CBHiggs_data"), ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kBlue))
    totPDF.plotOn(xframe, ROOT.RooFit.LineColor(ROOT.kGreen))

    CBHiggs_data.plotOn(xframe)

    c1 = ROOT.TCanvas()
    xframe.Draw()
    #input()
    c1.SaveAs("exercise_0.png")

    #Now save the data and the PDF into a Workspace, for later use for statistical analysis
    fOutput = ROOT.TFile("Workspace_mumufit.root","RECREATE")
    ws = ROOT.RooWorkspace("ws") 
    getattr(ws,'import')(totPDF)
    getattr(ws,'import')(data)
    ws.writeToFile("Workspace_mumufit.root")
    del ws

    #ws.Write()
    fOutput.Write()
    fOutput.Close()

if __name__ == "__main__":
    main()