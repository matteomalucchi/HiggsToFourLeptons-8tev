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
ROOT.gErrorIgnoreLevel = ROOT.kWarning


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


    infile_path = os.path.join(path, args.output, "histograms", "histograms.root")
    infile = ROOT.TFile(infile_path, "READ")

    plotting_functions.set_style()

    if args.ml :
        var_dict = VARIABLES_DICT["tot"]
    else :
        var_dict = VARIABLES_DICT["part"]

    variables = var_dict.keys()

    for selection in SELECTIONS.keys():
        logger.info(">>> Processing {selection}\n")

        for variable in variables:
            if variable != "Weight":

                # Get histograms for the signal
                signals = {}
                for final_state in ["FourMuons", "FourElectrons", "TwoMuonsTwoElectrons"]:
                    signals[final_state] = plotting_functions.get_histogram(infile,
                                            f"SMHiggsToZZTo4L_{final_state}_{variable}_{selection}")
                plotting_functions.combine_final_states(signals)

                # Get the normalized histograms for the signal
                signals_norm = {}
                for final_state, signal_histo in signals.items():
                    histo = signal_histo.Clone()
                    histo.Scale(1/histo.Integral())
                    signals_norm[final_state] = histo

                # Get histograms for the background
                backgrounds = {}
                backgrounds["FourMuons"] = plotting_functions.get_histogram(infile,
                                f"ZZTo4mu_FourMuons_{variable}_{selection}")
                backgrounds["FourElectrons"] = plotting_functions.get_histogram(infile,
                                f"ZZTo4e_FourElectrons_{variable}_{selection}")
                backgrounds["TwoMuonsTwoElectrons"] = plotting_functions.get_histogram(infile,
                                f"ZZTo2e2mu_TwoMuonsTwoElectrons_{variable}_{selection}")
                plotting_functions.combine_final_states(backgrounds)

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
                        histo = plotting_functions.get_histogram(infile,
                                        f"{sample}_{final_state}_{variable}_{selection}")
                        if not final_state in data:
                            data[final_state] = histo
                        else:
                            data[final_state].Add(histo)

                plotting_functions.combine_final_states(data)

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

                    # Create the directory to save the plots if doesn't already exist
                    dir_name = os.path.join(path, args.output, "plots", selection, input_type)
                    if not os.path.exists(dir_name):
                        os.makedirs(dir_name)
                        logger.debug("Directory %s Created", dir_name)

                    for final_state in ["FourMuons", "FourElectrons",
                                        "TwoMuonsTwoElectrons", "combined"]:
                        canvas = ROOT.TCanvas("", "", 600, 600)
                        legend = ROOT.TLegend(0.5, 0.7, 0.8, 0.9)
                        legend.SetBorderSize(0)

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
                        file_name = f"{input_type}_{final_state}_{variable}.pdf"
                        complete_name = os.path.join(dir_name, file_name)
                        canvas.SaveAs(complete_name)


if __name__ == "__main__":

    # Create and configure logger
    logging.basicConfig( format='\n%(asctime)s %(message)s')
    # Create an object
    logger_main=logging.getLogger()
    # Set the threshold of logger
    logger_main.setLevel(logging.INFO)

    # global configuration
    parser = argparse.ArgumentParser( description = 'Analysis Tool' )
    parser.add_argument('-p', '--parallel',   default=False,   action='store_const',
                        const=True, help='enables running in parallel')
    parser.add_argument('-n', '--nWorkers',   default=0,
                        type=int,   help='number of workers' )
    parser.add_argument('-m', '--ml', default=False,   action='store_const', const=True,
                        help='enables machine learning algorithm')
    parser.add_argument('-o', '--output',     default="Output", type=str,
                        help='name of the output directory')
    args_main = parser.parse_args()

    make_plot(args_main, logger_main, "..")
