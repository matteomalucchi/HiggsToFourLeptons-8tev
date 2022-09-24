""" Set up the logger for the analysis, check if
the arguments passed are valid and manage the output directory.
"""

import argparse
import os
import shutil
import logging
import sys

sys.path.append(os.path.join("..", ""))

from Analysis.Definitions.variables_def import  VARIABLES_COMPLETE
from Analysis.Definitions.variables_ml_def import  VARIABLES_ML_DICT
from Analysis.Definitions.samples_def import  SAMPLES


def check_val(log, input, correct_list, name):
    """ Check if the inputs are valid and sets them to
    the default value otherwise.

    :param log: Configurated logger for printing messages.
    :type log: logging.RootLogger
    :param input: input string
    :type input: str
    :param correct_list: list of accepted values
    :type correct_list: list(str)
    :param name: name of the argparse argument
    :type name: str
    :return: Correct input string
    :rtype: str
    """

    try:
        if not any(correct_in in input.split(",") for correct_in in correct_list):
            list_str=', '.join(correct_list)
            raise argparse.ArgumentTypeError(f"{name} {input} is invalid: it must be either {list_str}")
    except argparse.ArgumentTypeError as arg_err:
        log.exception("%s \n>>>%s is set to %s \n", arg_err, name, correct_list[0], stack_info=True)
        return correct_list[0]
    else:
        return input



def create_dir(log, dir, ignore):
    """Create the directory if doesn't
    already exist and create .gitignore.

    :param log: Configurated logger for printing messages.
    :type log: logging.RootLogger
    :param dir: Directory to create.
    :type dir: str
    :param ignore: Boolean that specifies if .gitignore should be created or not.
    :type ignore: bool
    """

    try:
        os.makedirs(dir)
        log.debug("Directory %s/ Created", dir)
    except FileExistsError:
        log.debug("The directory %s/ already exists", dir)
    finally:
        if ignore == True:
            file_path=os.path.join(dir, ".gitignore")
            if os.path.exists(file_path):
                pass
            else:
                # create .gitignore
                with open(file_path, 'w') as fp:
                    fp.write("# Ignore everything in this directory \n*")
                    fp.write("\n# Except this file \n!.gitignore")



def set_up (args):
    """ Function that sets up the logger, manages the various arguments
    of argparse and handles the output and input directories.

    :param args: Global configuration of the analysis.
    :type args: argparse.Namespace
    :return: Configuarated logger
    :rtype: logger
    """

    # Create and configure logger
    logging.basicConfig( format="\n%(asctime)s - %(filename)s - %(message)s")
    # Create an object
    logger=logging.getLogger()

    # Check if logLevel valid
    try:
        if args.logLevel not in [10, 20, 30, 40]:
            raise argparse.ArgumentTypeError(
                f"the value for logLevel {args.logLevel} is invalid: it must be either 10, 20, 30 or 40")
    except argparse.ArgumentTypeError as arg_err:
        logger.exception("%s \n logLevel is set to 20 \n", arg_err, stack_info=True)
        args.logLevel = 20
    except AttributeError:
        pass

    # Set the threshold of logger
    logger.setLevel(args.logLevel)


    # Check if typeDistribution is valid
    try:
        args.typeDistribution = check_val(logger, args.typeDistribution,
            ["all", "data", "background", "signal", "sig_bkg_normalized", "total"], "typeDistribution")
    except AttributeError:
        pass

    # Check if finalState is valid
    try:
        args.finalState = check_val(logger, args.finalState,
            ["all"] + SAMPLES["SMHiggsToZZTo4L"], "finalState")
    except AttributeError:
        pass

    # Check if variablesML is valid
    try:
        args.MLVariables = check_val(logger, args.MLVariables,
            list(VARIABLES_ML_DICT.keys()), "MLVariables")
    except AttributeError:
        pass

    # Check if sample is valid
    try:
        args.sample = check_val(logger, args.sample,
            ["all"] + list(SAMPLES.keys()), "sample")
    except AttributeError:
        pass

    # Check if variable is valid
    try:
        args.variableDistribution = check_val(logger, args.variableDistribution,
            ["all"] + list(VARIABLES_COMPLETE.keys()), "variableDistribution")
    except AttributeError:
        pass

    # Create the directory to save the downloaded files if doesn't already exist and create .gitignore
    try:
        if args.download != "":
            create_dir(logger, args.download, True)
    except AttributeError:
        pass

    # Clear the output folder
    try:
        if args.clearOutput != "":
            shutil.rmtree(args.clearOutput)
            logger.debug("Directory %s/ has been succesfully deleted", args.clearOutput)
    except OSError as os_err:
        logger.debug("ERROR directory %s/ could not be deleted: \n %s", args.clearOutput, os_err)
    except AttributeError:
        pass

    # Create the directory to save the outputs if doesn't already existand create .gitignore
    try:
        create_dir(logger, args.output, False)
    except AttributeError:
        pass

    return logger
