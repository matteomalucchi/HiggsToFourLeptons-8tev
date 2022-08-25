"""In this step two 2D scatter plots of Higgs_mass vs Discriminant 
are created, one for the simulated background and one for the 
simulated signal. Each plot contains both the combination 
of all background/signal datasets and the real data 
separated in the three possible final states.
"""

import os
import argparse
import logging
import sys

import ROOT

sys.path.append('../')
from Plotting import plotting_functions

#ROOT.gROOT.SetBatch(True)

def ml_plot (args, logger, path=""):
    """ Main function of the plotting step. The plotting takes 
    for each variable the histograms for each final state and sample.
    Then, the histograms are plotted with just the background, just the signal, just the data
    and finally, by combining all signal and background processes, in a stacked manner overlain
    by the data points. This procedure is repeated with all final states combined. 
    
    :param args: Global configuration of the analysis.
    :type args: argparse.Namespace
    :param logger: Configurated logger for printing messages.
    :type logger: logging.RootLogger
    :param path: Optional base path where the directories ``histograms/`` and ``discriminant_plots/`` can be found.
    :type path: str
    """   

    logger.info(f">>> Executing {os.path.basename(__file__)}\n")

    infile_path = os.path.join(path, args.output, "histograms", "histograms_discriminant.root")
    infile = ROOT.TFile(infile_path, "READ")

    datasets = ["signal", "background", "data_el", "data_mu", "data_elmu"]
        
    plotting_functions.SetStyle()
    histos = {}

    for dataset in datasets:
        # Get histograms for the signal
        
        histos[dataset] = plotting_functions.GetHistogram(infile, dataset)
        plotting_functions.InputStyle(dataset, histos[dataset])

    # Create the directory to save the plots if doesn't already exist
    dir_name = os.path.join(path, args.output, "discriminant_plots")
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        logger.debug("Directory " , dir_name ,  " Created ")
        
    for type in ["signal", "background"]:

        c = ROOT.TCanvas("", "", 600, 600)
        legend = ROOT.TLegend(0.75, 0.8, 0.85, 0.9)

        plotting_functions.AddTitle(histos[type])
        histos[type].Scale(1/histos[type].GetMaximum())
        histos[type].Draw("COLZ")
        histos["data_el"].Draw("SAME P") 
        histos["data_mu"].Draw("SAME P") 
        histos["data_elmu"].Draw("SAME P") 

        legend=plotting_functions.AddLegend(legend, "discriminant", histos)
        legend.Draw()

        plotting_functions.AddLatex()

        # Save the plots
        file_name = f"discriminant_{type}.pdf"
        complete_name = os.path.join(dir_name, file_name)
        #input()
        c.SaveAs(complete_name)

if __name__ == "__main__":
    
    # Create and configure logger 
    logging.basicConfig( format='\n%(asctime)s %(message)s') 
    # Create an object 
    logger=logging.getLogger() 
    # Set the threshold of logger
    logger.setLevel(logging.INFO)     
    # General configuration
    
    parser = argparse.ArgumentParser( description = 'Analysis Tool' )
    parser.add_argument('-p', '--parallel',   default=False,   action='store_const',     const=True, help='enables running in parallel')
    parser.add_argument('-n', '--nWorkers',   default=0,                                 type=int,   help='number of workers' )  
    parser.add_argument('-o', '--output',     default="Output", type=str,   help='name of the output directory')
    args = parser.parse_args()
    
    ml_plot(args, logger, "..")

                    
                

                    










