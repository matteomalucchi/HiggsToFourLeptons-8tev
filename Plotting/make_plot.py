"""Implementation of the plotting step of the analysis

The plotting combines the histograms to plots which allow to study the
inital dataset based on observables motivated through physics.
"""
import os
import sys
import argparse
import logging

import ROOT

sys.path.append('../')

from Definitions.variables_def import VARIABLES_DICT
from Definitions.selections_def import  SELECTIONS
from Plotting import plotting_functions

ROOT.gROOT.SetBatch(True)


def make_plot (args, logger, path=""):
    """Main function of the plotting step. The plotting takes for
    each variable the histograms for each final state and sample.
    Then, the histograms are plotted with just the background,
    just the signal, just the data and finally, by combining all
    signal and background processes, in a stacked manner overlain by the data points.
    This procedure is repeated with all final states combined.

    :param args: Global configuration of the analysis.
    :type args: argparse.Namespace
    :param logger: Configurated logger for printing messages.
    :type logger: logging.RootLogger
    :param path: Optional base path where the directories
        ``histograms/`` and ``plot/`` can be found.
    :type path: str
    """

    logger.info(">>> Executing %s \n", os.path.basename(__file__))

    if args.logLevel >= 20:
        ROOT.gErrorIgnoreLevel = ROOT.kWarning

    infile_path = os.path.join(path, args.output, "Histograms", "Histograms.root")
    # Check if file exists or not 
    try:
        if not os.path.exists(infile_path):
            raise FileNotFoundError
        infile = ROOT.TFile(infile_path, "READ")
    except FileNotFoundError as not_fund_err:
        logger.exception("File %s can't be found %s",
                        infile_path, not_fund_err,  stack_info=True)
        return
        
    plotting_functions.set_style()

    if args.ml :
        var_dict = VARIABLES_DICT["tot"]
    else :
        var_dict = VARIABLES_DICT["part"]

    variables = var_dict.keys()

    for selection in SELECTIONS.keys():
        logger.info(">>> Processing %s\n", selection)

        for variable in variables:
            if variable != "Weight":

                # Get histograms for the signal
                signals = {}
                for final_state in ["FourMuons", "FourElectrons", "TwoMuonsTwoElectrons"]:
                    histo_name = f"SMHiggsToZZTo4L_{final_state}_{variable}_{selection}"
                    try:
                        signals[final_state] = plotting_functions.get_histogram(infile, histo_name)
                    except RuntimeError as run_time_err:
                        logger.debug("ERROR:  %s ", run_time_err,  stack_info=True)
                
                try:
                    plotting_functions.combine_final_states(signals)
                except KeyError:
                    logger.debug("ERROR: Failed to create the signal histogram of the combined final states", 
                                    stack_info=True)
                    
                # Get the normalized histograms for the signal
                signals_norm = {}
                for final_state, signal_histo in signals.items():
                    histo = signal_histo.Clone()
                    histo.Scale(1/histo.Integral())
                    signals_norm[final_state] = histo

                # Get histograms for the background
                backgrounds = {}
                try:
                    backgrounds["FourMuons"] = plotting_functions.get_histogram(infile,
                                    f"ZZTo4mu_FourMuons_{variable}_{selection}")
                except RuntimeError as run_time_err:
                        logger.debug("ERROR:  %s ", run_time_err,  stack_info=True)
                        
                try:
                    backgrounds["FourElectrons"] = plotting_functions.get_histogram(infile,
                                    f"ZZTo4e_FourElectrons_{variable}_{selection}")
                except RuntimeError as run_time_err:
                        logger.debug("ERROR:  %s ", run_time_err,  stack_info=True)
                        
                try:
                    backgrounds["TwoMuonsTwoElectrons"] = plotting_functions.get_histogram(infile,
                                    f"ZZTo2e2mu_TwoMuonsTwoElectrons_{variable}_{selection}")
                except RuntimeError as run_time_err:
                        logger.debug("ERROR:  %s ", run_time_err,  stack_info=True)
                
                try:
                    plotting_functions.combine_final_states(backgrounds)
                except KeyError:
                    logger.debug("ERROR: Failed to create the background histogram of the combined final states", 
                                    stack_info=True)
                    
                # Get the normalized histograms for the background
                backgrounds_norm = {}
                for final_state, background_histo in backgrounds.items():
                    histo = background_histo.Clone()
                    histo.Scale(1/histo.Integral())
                    backgrounds_norm[final_state] = histo

                # Get histograms for the data
                data = {}
                for final_state, samples in [
                            ["FourMuons", ["Run2012B_DoubleMuParked",
                                           "Run2012C_DoubleMuParked"]],
                            ["FourElectrons", ["Run2012B_DoubleElectron",
                                               "Run2012C_DoubleElectron"]],
                            ["TwoMuonsTwoElectrons", ["Run2012B_DoubleMuParked",
                                                      "Run2012C_DoubleMuParked",
                                                      "Run2012B_DoubleElectron",
                                                      "Run2012C_DoubleElectron"]]
                        ]:
                    for sample in samples:
                        try: 
                            histo = plotting_functions.get_histogram(infile,
                                        f"{sample}_{final_state}_{variable}_{selection}")
                            if not final_state in data:
                                data[final_state] = histo
                            else:
                                data[final_state].Add(histo)
                        except RuntimeError as run_time_err:
                            logger.debug("ERROR:  %s ", run_time_err,  stack_info=True)

                try:
                    plotting_functions.combine_final_states(data)
                except KeyError:
                    logger.debug("ERROR: Failed to create the data histogram of the combined final states", 
                                    stack_info=True)
                    
                # Dictionary for the different types of datasets
                inputs_dict = {
                    "data" : data,
                    "background" : backgrounds,
                    "signal" : signals,
                    "sig_bkg_normalized" : [backgrounds_norm, signals_norm],
                    "total" : ["data", "background", "signal"]
                }

                # Loop over the types of datasets and the final states
                for input_type, inputs in inputs_dict.items():
                    
                    # Check if the input_type to plot is one of those requested by the user
                    if input_type not in args.typeDistribution and args.typeDistribution != "all":
                        continue

                    # Create the directory to save the plots if doesn't already exist
                    dir_name = os.path.join(path, args.output, "Plots", selection, input_type)
                    try:
                        os.makedirs(dir_name)
                        logger.debug("Directory %s/ Created", dir_name)
                    except FileExistsError:
                        logger.debug("The directory %s/ already exists", dir_name)

                    for final_state in ["FourMuons", "FourElectrons",
                                        "TwoMuonsTwoElectrons", "Combined"]:
                        canvas = ROOT.TCanvas("", "", 600, 600)
                        legend = ROOT.TLegend(0.5, 0.7, 0.8, 0.9)
                        legend.SetBorderSize(0)
                        
                        try:
                            if input_type in ["data", "background", "signal"]:
                                input_histo = inputs[final_state]
                                plotting_functions.input_style(input_type, input_histo)
                                plotting_functions.add_title(input_histo, var_dict[variable])
                                input_histo.SetMaximum(input_histo.GetMaximum() * 1.4)
                                if input_type == "data":
                                    input_histo.Draw("E1P")
                                elif input_type in ("background", "signal"):
                                    input_histo.Draw("HIST")
                                legend=plotting_functions.add_legend(legend, input_type, input_histo)
                                legend.Draw()

                            elif input_type == "sig_bkg_normalized":
                                bkg_norm = inputs[0][final_state]
                                sig_norm = inputs[1][final_state]
                                plotting_functions.input_style("background", bkg_norm)
                                plotting_functions.input_style("signal", sig_norm)
                                plotting_functions.add_title(bkg_norm, var_dict[variable])
                                bkg_norm.SetMaximum(max(bkg_norm.GetMaximum(),
                                                        sig_norm.GetMaximum()) * 1.5)
                                bkg_norm.Draw("HIST")
                                sig_norm.Draw("HIST SAME")
                                legend=plotting_functions.add_legend(legend, "background", bkg_norm)
                                legend=plotting_functions.add_legend(legend, "signal", sig_norm)
                                legend.Draw()

                            elif input_type == "total":

                                # Add the background to the signal
                                # in order to compare it with the data.
                                signals[final_state].Add(backgrounds[final_state])
                                for input_key in inputs:
                                    input_histo=inputs_dict[input_key][final_state]
                                    plotting_functions.input_style(input_key, input_histo)
                                    legend=plotting_functions.add_legend(legend, input_key, input_histo)

                                plotting_functions.add_title(signals[final_state], var_dict[variable])
                                signals[final_state].SetMaximum(
                                                    max(backgrounds[final_state].GetMaximum(),
                                                    data[final_state].GetMaximum()) * 1.4)
                                signals[final_state].Draw("HIST")
                                backgrounds[final_state].Draw("HIST SAME")
                                data[final_state].Draw("E1P SAME")
                                legend.Draw()

                            plotting_functions.add_latex()

                            # Save the plots
                            file_name = f"{input_type}_{final_state}_{variable}_{selection}.pdf"
                            complete_name = os.path.join(dir_name, file_name)
                            canvas.SaveAs(complete_name)
                            
                        except KeyError:
                            logger.debug("ERROR: Failed to create the plot for %s_%s_%s_%s", 
                                   input_type, final_state, variable, selection, stack_info=True)


if __name__ == "__main__":

    # General configuration
    parser = argparse.ArgumentParser( description = 'Analysis Tool' )
    parser.add_argument('-o', '--output',     default="Output", type=str,
                        help='name of the output directory')
    parser.add_argument('-m', '--ml', default=True,   action='store_const', const=False,
                        help='disables machine learning algorithm')
    parser.add_argument('-l', '--logLevel',   default=20, type=int,   
                            help='integer representing the level of the logger:\
                             DEBUG=10, INFO = 20, WARNING = 30, ERROR = 40' )
    parser.add_argument('-t', '--typeDistribution',   default="all", type=str,   
                        help='comma separated list of the type of distributions to plot: \
                        data, background, signal, sig_bkg_normalized, total' )
    parser.add_argument('-f', '--finalState',   default="all", type=str,   
                            help='comma separated list of the final states to analyse: \
                            FourMuons,FourElectrons,TwoMuonsTwoElectrons' )
    args_main = parser.parse_args()

    # Create and configure logger
    logging.basicConfig( format='\n%(asctime)s %(message)s')
    # Create an object
    logger_main=logging.getLogger()
    
    # Check if logLevel valid       
    try:
        if args_main.logLevel not in [10, 20, 30, 40]:
            raise argparse.ArgumentTypeError(f"the value for logLevel {args_main.logLevel} is invalid: it must be either 10, 20, 30 or 40")
    except argparse.ArgumentTypeError as arg_err:
        args_main.logLevel = 20
        logger_main.exception("%s \nlogLevel is set to 20 \n", arg_err, stack_info=True)
        
    # Set the threshold of logger
    logger_main.setLevel(args_main.logLevel)

    # Check if finalState is valid
    try:
        if not any(final_state in args_main.finalState for final_state 
               in ["all", "FourMuons", "FourElectrons", "TwoMuonsTwoElectrons"]):
            raise argparse.ArgumentTypeError(f"the final state {args_main.finalState} is invalid: \
                it must be either all,FourMuons,FourElectrons,TwoMuonsTwoElectrons")
    except argparse.ArgumentTypeError as arg_err:
        logger_main.exception("%s \n finalState is set to all \n", arg_err, stack_info=True)
        args_main.finalState = "all"  
    
    # Check if typeDistribution is valid
    try:
        if not any(type_distribution in args_main.typeDistribution for type_distribution 
               in ["all", "data", "background", "signal", "sig_bkg_normalized", "total"]):
            raise argparse.ArgumentTypeError(f"the type of distribution {args_main.typeDistribution} is invalid: \
                it must be either all,data,background,signal,sig_bkg_normalized,total")
    except argparse.ArgumentTypeError as arg_err:
        logger_main.exception("%s \n typeDistribution is set to all \n", arg_err, stack_info=True)
        args_main.typeDistribution = "all"  
        

    make_plot(args_main, logger_main, "..")
