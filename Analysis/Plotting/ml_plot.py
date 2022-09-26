"""In this step two 2D scatter plots of Higgs_mass vs Discriminant
are created, one for the simulated background and one for the
simulated signal. Each plot contains both the combination
of all background/signal datasets and the real data
separated in the three possible final states.
"""

import argparse
import os
import sys
import time

import ROOT

sys.path.append(os.path.join("..","..", ""))

from Analysis import set_up
from Analysis.Plotting import plotting_functions


def ml_plot (args, logger):
    """ Main function of the plotting step. The plotting takes
    for each variable the histograms for each final state and sample.
    Then, the histograms are plotted with just the background,
    just the signal, just the data and finally, by combining all
    signal and background processes, in a stacked manner overlain
    by the data points.
    This procedure is repeated with all final states combined.

    :param args: Global configuration of the analysis.
    :type args: argparse.Namespace
    :param logger: Configurated logger for printing messages.
    :type logger: logging.RootLogger
    """

    logger.info(">>> Executing %s \n", os.path.basename(__file__))

    start_time = time.time()

    infile_path = os.path.join(args.output, "Histograms",
                               "Histograms_discriminant.root")
    # Check if file exists or not
    try:
        if not os.path.exists(infile_path):
            raise FileNotFoundError
        infile = ROOT.TFile(infile_path, "READ")
    except FileNotFoundError as not_fund_err:
        logger.exception("File %s can't be found %s",
                        infile_path, not_fund_err,  stack_info=True)
        return

    datasets = ["signal", "background", "data_el", "data_mu", "data_elmu"]

    plotting_functions.set_style()

    histos = {}
    # Get histograms
    for dataset in datasets:
        try:
            histos[dataset] = plotting_functions.get_histogram(infile, dataset)
            plotting_functions.input_style(dataset, histos[dataset])
        except RuntimeError as run_time_err:
            logger.debug("ERROR:  %s ", run_time_err,  stack_info=True)

    # Create the directory to save the plots if doesn't already exist
    dir_name = os.path.join(args.output, "Discriminant_plots")
    try:
        os.makedirs(dir_name)
        logger.debug("Directory %s/ Created", dir_name)
    except FileExistsError:
        logger.debug("The directory %s/ already exists", dir_name)

    for type_dataset in ["signal", "background"]:

        canvas = ROOT.TCanvas("", "", 600, 600)
        legend = ROOT.TLegend(0.75, 0.8, 0.85, 0.9)
        try:
            plotting_functions.add_title(histos[type_dataset])
            histos[type_dataset].Scale(1/histos[type_dataset].GetMaximum())
            histos[type_dataset].Draw("COLZ")
        except KeyError:
            logger.debug("ERROR: Failed to create the %s histogram",
                                    type_dataset, stack_info=True)
            continue

        try:
            histos["data_el"].Draw("SAME P")
        except KeyError:
            logger.debug(
                "ERROR: Failed to create the data histogram of the FourElectrons final state in the %s TH2D",
                type_dataset, stack_info=True)

        try:
            histos["data_mu"].Draw("SAME P")
        except KeyError:
            logger.debug(
                "ERROR: Failed to create the data histogram of the FourMuons final state in the %s TH2D",
                type_dataset, stack_info=True)

        try:
            histos["data_elmu"].Draw("SAME P")
        except KeyError:
            logger.debug(
                "ERROR: Failed to create the data histogram of the TwoMuonsTwoElectrons final state in the %s TH2D",
                type_dataset, stack_info=True)

        legend=plotting_functions.add_legend(legend, "discriminant", histos)
        legend.Draw()

        plotting_functions.add_latex()

        # Save the plots
        file_name = f"discriminant_{type_dataset}.pdf"
        complete_name = os.path.join(dir_name, file_name)
        canvas.SaveAs(complete_name)

    logger.info(">>> Execution time: %s s \n", (time.time() - start_time))

if __name__ == "__main__":

    # General configuration
    parser = argparse.ArgumentParser( description = "Analysis Tool" )
    parser.add_argument("-o", "--output",     default=os.path.join("..", "..", "Output"), type=str,
                        help="name of the output directory")
    parser.add_argument("-l", "--logLevel",   default=20, type=int,
                            help="integer representing the level of the logger:\
                             DEBUG=10, INFO = 20, WARNING = 30, ERROR = 40" )
    args_main = parser.parse_args()

    logger_main=set_up.set_up(args_main)

    ml_plot(args_main, logger_main)
