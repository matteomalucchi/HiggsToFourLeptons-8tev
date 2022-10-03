""" Download the various sample from the `CMS open-data portal
<http://opendata.cern.ch/record/12360>`_.
"""

import argparse
import multiprocessing as mp
import os
import sys
import threading as thr
import urllib.error
import urllib.request
from functools import wraps
from time import perf_counter

import progressbar

sys.path.append(os.path.join("..", ""))

from Analysis import set_up
from Analysis.Definitions.samples_download_def import SAMPLES_DOWNLOAD


class MyProgressBar():
    """ Class that defines a progress bar for the download.
    """

    def __init__(self):
        """ Create the attribute for the progress bar.
        """

        self.prog_bar = None

    def __call__(self, block_num, block_size, total_size):
        """ Update the progress bar for each downloaded block.

        :param block_num: Number of the downloaded block
        :type block_num: int
        :param block_size: Size in bites of the downloaded block
        :type block_size: int
        :param block_num: Total size in bites of the file
        :type block_num: int
        """

        if not self.prog_bar:
            self.prog_bar=progressbar.ProgressBar(maxval=total_size)
            self.prog_bar.start()

        downloaded = block_num * block_size
        if downloaded < total_size:
            self.prog_bar.update(downloaded)
        else:
            self.prog_bar.finish()


def count_func(func):
    """ Function that counts the number of times the input function is called recursively.

    :param func: Function to be wrapped
    :type func: function
    """

    @wraps(func)
    def counted(*args):
        counted.call_count += 1
        return func(*args)
    counted.call_count = 1
    return counted


def get_file_parallel(log, num, sample, file):
    """Function that downloads the various samples in parallel from the CMS open-data portal.

    :param log: Configured logger for printing messages.
    :type log: logging.RootLogger
    :param num: Number present in the url
    :type num: int
    :param sample: Name of the sample to download.
    :type sample: str
    :param file: Name of the file to be saved.
    :type file: str
    """

    count = 1
    while count <= 6:
        try:
            urllib.request.urlretrieve(
                f"http://opendata.cern.ch/record/{num}/files/{sample}.root", file)
        except urllib.error.HTTPError as http_err:
            log.exception("File %s.root can't be found %s",
                            sample, http_err, stack_info=True)
            return
        except urllib.error.ContentTooShortError:
            log.error(
                "Network conditions is not good. Reloading for %d time file %s.root",
                count, sample)
            count += 1
        else:
            return

    log.exception("ERROR: Download of %s.root has failed due to bad network conditions!\n", sample)


@count_func
def get_file(log, num, sample, file):
    """Function that downloads the various samples not in parallel from the CMS open-data portal.

    This function, unlike parallel one, shows a progress bar (using a specific class created for
    this very purpose) and uses a decorator in order to count the number of times that
    is called recursively.
    The reason why this needlessly complicated function was defined
    is that it makes use of some tools that, in the rest of the project, weren't employed.


    :param log: Configured logger for printing messages.
    :type log: logging.RootLogger
    :param num: Number present in the url
    :type num: int
    :param sample: Name of the sample to download.
    :type sample: str
    :param file: Name of the file to be saved.
    :type file: str
    """

    try:
        urllib.request.urlretrieve(
            f"http://opendata.cern.ch/record/{num}/files/{sample}.root", file, MyProgressBar())
    except urllib.error.HTTPError as http_err:
        log.exception("File %s.root can't be found %s",
                        sample, http_err, stack_info=True)
    except urllib.error.ContentTooShortError:
        log.error("Network conditions is not good. Reloading for %d time file %s.root",
                        get_file.call_count, sample)
        if get_file.call_count == 7:
            log.exception(
                "ERROR: Download of %s.root has failed due to bad network conditions!\n", sample)
            get_file.call_count=0
            return
        get_file(log, num, sample, file)
    else:
        get_file.call_count=0


def download(args, logger):
    """ Main function that creates the threads/processes and
    sets up the multithread/multiprocess operations.

    :param args: Global configuration of the analysis.
    :type args: argparse.Namespace
    :param logger: Configured logger for printing messages.
    :type logger: logging.RootLogger
    """

    logger.info(">>> Executing %s \n", os.path.basename(__file__))
    time= perf_counter()

    if args.parallel:
        logger.info(">>> Executing in parallel \n")
        parallel_list = []
        #Loop over the various samples
        for sample_name, number in SAMPLES_DOWNLOAD.items():

            # Check if the sample is one of those requested by the user
            if sample_name not in args.sample and args.sample != "all":
                continue

            logger.info(">>> Process sample: %s \n", sample_name)
            file_name=os.path.join(args.download, f"{sample_name}.root")

            if args.typeOfParallel == "thread":
                logger.info(">>> Executing multi-threading \n")
                parallel_list.append(thr.Thread(target=get_file_parallel,
                                    args=(logger, number, sample_name, file_name)))
            elif args.typeOfParallel == "process":
                logger.info(">>> Executing multi-processing \n")
                parallel_list.append(mp.Process(target=get_file_parallel,
                                    args=(logger, number, sample_name, file_name)))

        # Start parallel
        for parallel_elem in parallel_list:
            parallel_elem.start()

        # Join parallel
        for parallel_elem in parallel_list:
            parallel_elem.join()

    else:
        logger.info(">>> Executing not in parallel \n")
        # Loop over the various samples
        for sample_name, number in SAMPLES_DOWNLOAD.items():

            # Check if the sample is one of those requested by the user
            if sample_name not in args.sample and args.sample != "all":
                continue

            logger.info(">>> Process sample: %s \n", sample_name)
            file_name=os.path.join(args.download, f"{sample_name}.root")
            get_file(logger, number, sample_name, file_name)

    print("Time: "+str(perf_counter()-time))



if __name__ == "__main__":

    # General configuration
    parser = argparse.ArgumentParser( description = "Analysis Tool" )
    parser.add_argument("-p", "--parallel",   default=True,   action="store_const",
                            const=False, help="disables running in parallel")
    parser.add_argument("-e", "--typeOfParallel", default="thread",   action="store_const",
                         const="process",  help="parallel type for the downloads: \
                         default is multi-thread, if activated is multi-process" )
    parser.add_argument("-l", "--logLevel",   default=20, type=int,
                            help="integer representing the level of the logger:\
                             DEBUG=10, INFO = 20, WARNING = 30, ERROR = 40" )
    parser.add_argument("-s", "--sample",    default="all", type=str,
                            help="string with comma separated list of samples to analyse: \
                            Run2012B_DoubleElectron, Run2012B_DoubleMuParked, \
                            Run2012C_DoubleElectron,  Run2012C_DoubleMuParked, \
                            SMHiggsToZZTo4L, ZZTo2e2mu, ZZTo4e, ZZTo4mu")
    parser.add_argument("-d", "--download", default="../Input",
                            type=str, help="directory where to download the input data")
    args_main = parser.parse_args()

    logger_main=set_up.set_up(args_main)

    download(args_main, logger_main)
