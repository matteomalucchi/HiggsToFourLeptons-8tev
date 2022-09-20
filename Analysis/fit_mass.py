""" The mass of the Higgs candidate is fitted with a Crystal Ball. 
A fit on the simulated samples and a fit on the data 
(estimating the background from the MC) are performed.
"""

import time
import os
import argparse


import ROOT

from Analysis.Definitions.samples_def import SAMPLES
from Analysis.Definitions.selections_def import  SELECTIONS
from Analysis.Plotting import plotting_functions

import Analysis.set_up as set_up

def fit_mass (args, logger):
    """ Main function for the mass fit of the Higgs candidate
    using a Crystal Ball.
    
    :param args: Global configuration of the analysis.
    :type args: argparse.Namespace
    :param logger: Configurated logger for printing messages.
    :type logger: logging.RootLogger

    """
    ROOT.gErrorIgnoreLevel = ROOT.kError

    logger.info(">>> Executing %s \n", os.path.basename(__file__))
    
    #plotting_functions.set_style()

    start_time = time.time()

    # Create the directory to save the outputs of the fit if doesn't already exist
    dir_name = os.path.join(args.output, "Fit_results1")
    try:
        os.makedirs(dir_name)
        logger.debug("Directory %s/ Created", dir_name)
    except FileExistsError:
        logger.debug("The directory %s/ already exists", dir_name)
        
    # Loop over the possible selections
    for selection, tree_name in SELECTIONS.items():
        try:
            logger.info(">>> Process %s\n", selection)
            
            sig_chain= ROOT.TChain(tree_name)
            bkg_chain= ROOT.TChain(tree_name)
            data_chain= ROOT.TChain(tree_name)

            for sample_name, final_states in SAMPLES.items():
                # Check if the sample to plot is one of those requested by the user
                if sample_name not in args.sample and args.sample != "all":
                    continue
                for final_state in final_states:
                    # Check if the final state is one of those requested by the user
                    if final_state not in args.finalState and args.finalState != "all":
                        continue
                    logger.info(">>> Process sample %s and final state %s", 
                                sample_name, final_state)

                    # Check if input file exists or not
                    try: 
                        infile_path = os.path.join(args.output, "Skim_data", 
                                            f"{sample_name}{final_state}Skim.root")
                        if not os.path.exists(infile_path):
                            raise FileNotFoundError
                    except FileNotFoundError as not_found_err:
                        logger.debug("Sample %s final state %s: File %s can't be found %s",
                                        sample_name, final_state, infile_path, not_found_err,  stack_info=True)
                        continue

                    file = ROOT.TFile(infile_path,"READ")
                    tree= file.Get(tree_name)
                    if not tree:
                        raise RuntimeError

                    if sample_name.startswith("SM"):
                        sig_chain.Add(infile_path)

                    elif sample_name.startswith("ZZ"):
                        bkg_chain.Add(infile_path)

                    elif sample_name.startswith("Run"):
                        data_chain.Add(infile_path)

            m4l = ROOT.RooRealVar("Higgs_mass",f"4 leptons invariant mass with {selection}", 110, 140,"GeV")
            weight = ROOT.RooRealVar("Weight","Weight", 0, 1,"GeV")

            sig = ROOT.RooDataSet("signal", "", sig_chain, ROOT.RooArgSet(m4l, weight) )
            bkg = ROOT.RooDataSet("background", "", bkg_chain, ROOT.RooArgSet(m4l, weight) )
            data = ROOT.RooDataSet("data", "", data_chain, ROOT.RooArgSet(m4l, weight) )

            # Calculate signal fraction
            sig_frac_count = sig.sumEntries()/(sig.sumEntries()+bkg.sumEntries())
            bkg_frac_count = bkg.sumEntries()/(sig.sumEntries()+bkg.sumEntries())
            
            # KDE for background. In this configuration the input data
            # is mirrored over the right boundary to minimize edge effects in distribution
            # that do not fall to zero towards the right edge
            bkg_kde = ROOT.RooKeysPdf("bkg_kde", "bkg_kde", m4l, bkg, ROOT.RooKeysPdf.MirrorRight)

            # Parameters and model for the fit of the simulated signal samples
            meanHiggs_sig = ROOT.RooRealVar("meanHiggs_sig", "The mean of the Higgs CB for the signal", 125, 115, 135, "GeV")
            sigmaHiggs = ROOT.RooRealVar("sigmaHiggs_sig", "The width of Higgs CB for the signal", 5, 0., 20, "GeV")
            alphaHiggs = ROOT.RooRealVar("alphaHiggs_sig", "The tail of Higgs CB for the signal", 1.5, -5, 5)
            nHiggs = ROOT.RooRealVar("nHiggs_sig", "The normalization of Higgs CB for the signal", 1.5, 0, 10)
            CBHiggs_sig = ROOT.RooCBShape("CBHiggs_sig","The Higgs Crystall Ball for the signal",
                                            m4l, meanHiggs_sig, sigmaHiggs, alphaHiggs, nHiggs)
            
            # Unbinned ML fit to signal
            fitHiggs = CBHiggs_sig.fitTo(sig, ROOT.RooFit.Save(True), ROOT.RooFit.AsymptoticError(True))
            fitHiggs.Print("v")

            # Parameters and model for data fit
            meanHiggs_data = ROOT.RooRealVar("m_{H}", "The mean of the Higgs CB for the data", 125, 115, 135, "GeV")
            CBHiggs_data = ROOT.RooCBShape("CBHiggs_data","The Higgs Crystall Ball for the data",
                                            m4l, meanHiggs_data, sigmaHiggs, alphaHiggs, nHiggs)
            
            # Signal and background fractions
            sig_frac= ROOT.RooRealVar("sigfrac", "signal fraction", sig_frac_count)
            bkg_frac= ROOT.RooRealVar("bkg_coeff", "bkg fraction", bkg_frac_count)

            # Total PDF of data and background
            totPDF = ROOT.RooAddPdf("totPDF", "Higgs_data+bkg", ROOT.RooArgList(CBHiggs_data, bkg_kde), ROOT.RooArgList(sig_frac,bkg_frac))
            
            # Unbinned ML fit to data
            fitdata = totPDF.fitTo(data, ROOT.RooFit.Save(True))
            fitdata.Print("v")
            logger.info("Fraction sig/bkg is: %s\n",sig_frac_count)
            logger.info("Fraction bkg/sig is: %s\n",bkg_frac_count)

            # Print fit results
            meanHiggs_sig.Print()
            meanHiggs_data.Print()
            sigmaHiggs.Print()
            alphaHiggs.Print()
            nHiggs.Print()

            # Plot mass fit
            m4l.setBins(10)
            xframe = m4l.frame()
            xframe.SetTitle("")
            data.plotOn(xframe, ROOT.RooFit.Name("data"))
            totPDF.plotOn(xframe, ROOT.RooFit.Name("bkg_kde"), ROOT.RooFit.Components("bkg_kde"), ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kRed))
            totPDF.plotOn(xframe, ROOT.RooFit.Name("CBHiggs_data"), ROOT.RooFit.Components("CBHiggs_data"), ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kBlue))
            totPDF.plotOn(xframe, ROOT.RooFit.Name("totPDF"), ROOT.RooFit.LineColor(ROOT.kGreen))

            canvas = ROOT.TCanvas()
            xframe.Draw()
            plotting_functions.add_latex()

            legend = ROOT.TLegend(0.6, 0.7, 0.9, 0.9)
            plotting_functions.add_legend(legend, "fit")
            legend.Draw()
            
            #input()
            output_name = os.path.join(dir_name, f"fit_mass_{selection}.pdf")
            canvas.SaveAs(output_name)

            #Now save the data and the PDF into a Workspace
            out_file_name= os.path.join(dir_name, f"Workspace_mass_fit_{selection}.root")
            fOutput = ROOT.TFile(out_file_name,"RECREATE")
            ws = ROOT.RooWorkspace("ws") 
            getattr(ws,"import")(totPDF)
            getattr(ws,"import")(data)
            ws.writeToFile(out_file_name)
            del ws
            fOutput.Write()
            fOutput.Close()

        except RuntimeError:
            logger.debug("Can't find the TTree %s", tree_name, stack_info=True)

    logger.info(">>> Execution time: %s s \n", (time.time() - start_time))        

if __name__ == "__main__":
    
    # General configuration
    parser = argparse.ArgumentParser( description = "Analysis Tool" )
    parser.add_argument("-o", "--output",     default="Output", type=str,  
                        help="name of the output directory")
    parser.add_argument("-l", "--logLevel",   default=20, type=int,   
                            help="integer representing the level of the logger:\
                             DEBUG=10, INFO = 20, WARNING = 30, ERROR = 40" )
    parser.add_argument("-f", "--finalState",   default="all", type=str,   
                            help="comma separated list of the final states to analyse: \
                            FourMuons,FourElectrons,TwoMuonsTwoElectrons" )
    parser.add_argument("-s", "--sample",    default="all", type=str,
                        help="string with comma separated list of samples to analyse: \
                        Run2012B_DoubleElectron, Run2012B_DoubleMuParked, Run2012C_DoubleElectron, \
                        Run2012C_DoubleMuParked, SMHiggsToZZTo4L, ZZTo2e2mu, ZZTo4e, ZZTo4mu")    
    args_main = parser.parse_args()
    
    logger_main=set_up.set_up(args_main)
    
    
    fit_mass(args_main, logger_main)