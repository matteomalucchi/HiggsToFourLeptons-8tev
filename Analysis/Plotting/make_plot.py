""" The plotting combines the histograms to plots which allow to study the
inital dataset based on observables motivated through physics.
"""
import argparse
import os
import sys
import time

import ROOT

sys.path.append(os.path.join("..","..", ""))

from Analysis import set_up
from Analysis.Definitions.selections_def import SELECTIONS
from Analysis.Definitions.variables_def import VARIABLES_DICT
from Analysis.Plotting import plotting_functions

ROOT.gROOT.SetBatch(True)


def make_plot (args, logger):
    """ Main function of the plotting step. The plotting takes for
    each variable the histograms for each final state and sample.
    Later, plots of these variables are produced for various sample
    combinations: only the signal, only the background, only the data,
    the combination of all the above (with signal and background stacked
    on top of each other) and also the combination of normalized signal and background.

    :param args: Global configuration of the analysis.
    :type args: argparse.Namespace
    :param logger: Configured logger for printing messages.
    :type logger: logging.RootLogger
    :param path: Optional base path where the directories
        ``Histograms/`` and ``Plots/`` can be found.
    :type path: str
    """

    logger.info(">>> Executing %s \n", os.path.basename(__file__))

    start_time = time.time()

    if args.logLevel >= 20:
        ROOT.gErrorIgnoreLevel = ROOT.kWarning

    infile_path = os.path.join(args.output, "Histograms", "Histograms.root")
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
            # Check if the variable to plot is one of those requested by the user
            if (variable not in args.variableDistribution
                and args.variableDistribution != "all") or variable == "Weight":
                continue

            # Get histograms for the signal
            signals = {}

            # Check if the sample to plot is one of those requested by the user
            if "SMHiggsToZZTo4L" in args.sample or args.sample == "all":
                for final_state in ["FourMuons", "FourElectrons", "TwoMuonsTwoElectrons"]:
                    histo_name = f"SMHiggsToZZTo4L_{final_state}_{variable}_{selection}"
                    try:
                        signals[final_state] = plotting_functions.get_histogram(infile, histo_name)
                    except RuntimeError as run_time_err:
                        logger.debug("ERROR:  %s ", run_time_err,  stack_info=True)

                try:
                    plotting_functions.combine_final_states(signals)
                except KeyError:
                    logger.debug(
                       "ERROR: Failed to create the signal histogram of the combined final states",
                        stack_info=True)

            # Get the normalized histograms for the signal
            signals_norm = {}
            for final_state, signal_histo in signals.items():
                histo = signal_histo.Clone()
                histo.Scale(1/histo.Integral()*100)
                signals_norm[final_state] = histo

            # Get histograms for the background
            backgrounds = {}
            for sample, final_state in {"ZZTo4mu":"FourMuons",
                                        "ZZTo4e":"FourElectrons",
                                        "ZZTo2e2mu":"TwoMuonsTwoElectrons"
                    }.items():
                # Check if the sample to plot is one of those requested by the user
                if sample not in args.sample and args.sample != "all":
                    continue
                try:
                    backgrounds[final_state] = plotting_functions.get_histogram(infile,
                                f"{sample}_{final_state}_{variable}_{selection}")
                except RuntimeError as run_time_err:
                    logger.debug("ERROR:  %s ", run_time_err,  stack_info=True)

            try:
                plotting_functions.combine_final_states(backgrounds)
            except KeyError:
                logger.debug(
                   "ERROR: Failed to create the background histogram of the combined final states",
                    stack_info=True)

            # Get the normalized histograms for the background
            backgrounds_norm = {}
            for final_state, background_histo in backgrounds.items():
                histo = background_histo.Clone()
                histo.Scale(1/histo.Integral()*100)
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
                    # Check if the sample to plot is one of those requested by the user
                    if sample not in args.sample and args.sample != "all":
                        continue
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
                logger.debug(
                   "ERROR: Failed to create the data histogram of the combined final states",
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
                dir_name = os.path.join(args.output, "Plots", selection, input_type)
                try:
                    os.makedirs(dir_name)
                    logger.debug("Directory %s/ Created", dir_name)
                except FileExistsError:
                    logger.debug("The directory %s/ already exists", dir_name)

                for final_state in ["FourMuons", "FourElectrons",
                                    "TwoMuonsTwoElectrons", "Combined"]:

                    if final_state not in args.finalState and args.finalState != "all":
                        continue

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

    logger.info(">>> Execution time: %s s \n",(time.time() - start_time))

if __name__ == "__main__":

    # General configuration
    parser = argparse.ArgumentParser( description = "Analysis Tool" )
    parser.add_argument("-o", "--output",     default=os.path.join("..", "..", "Output"), type=str,
                        help="name of the output directory")
    parser.add_argument("-m", "--ml", default=True,   action="store_const", const=False,
                        help="disables machine learning algorithm")
    parser.add_argument("-l", "--logLevel",   default=20, type=int,
                            help="integer representing the level of the logger:\
                             DEBUG=10, INFO = 20, WARNING = 30, ERROR = 40" )
    parser.add_argument("-t", "--typeDistribution",   default="all", type=str,
                        help="comma separated list of the type of distributions to plot: \
                        data, background, signal, sig_bkg_normalized, total" )
    parser.add_argument("-f", "--finalState",   default="all", type=str,
                            help="comma separated list of the final states to analyse: \
                            FourMuons,FourElectrons,TwoMuonsTwoElectrons" )
    parser.add_argument("-s", "--sample",    default="all", type=str,
                        help="string with comma separated list of samples to analyse: \
                        Run2012B_DoubleElectron, Run2012B_DoubleMuParked, Run2012C_DoubleElectron, \
                        Run2012C_DoubleMuParked, SMHiggsToZZTo4L, ZZTo2e2mu, ZZTo4e, ZZTo4mu")
    parser.add_argument("-v", "--variableDistribution",    default="all", type=str,
                        help="string with comma separated list of the variables to plot. \
                            The complete list is defined in 'variables_def.py'")
    args_main = parser.parse_args()

    logger_main=set_up.set_up(args_main)


    make_plot(args_main, logger_main)
