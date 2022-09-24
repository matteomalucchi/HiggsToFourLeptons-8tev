""" Download the various sample from the CMS open-data portal.
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

SAMPLES_DOWNLOAD={
    "SMHiggsToZZTo4L" : 12361,
    "ZZTo4mu" : 12362,
    "ZZTo4e" : 12363,
    "ZZTo2e2mu" : 12364,
    "Run2012B_DoubleMuParked" : 12365,
    "Run2012C_DoubleMuParked" : 12366,
    "Run2012B_DoubleElectron" : 12367,
    "Run2012C_DoubleElectron" : 12368
}


class MyProgressBar():
    """ Class that defines a progress bar for the download.
    """

    def __init__(self):
        """ Create the attribute pbar
        """

        self.pbar = None

    def __call__(self, block_num, block_size, total_size):
        """ Update the progress bar for each downloaded block.

        :param block_num: Number of the downloaded block
        :type block_num: int
        :param block_size: Size in bites of the downloaded block
        :type block_size: int
        :param block_num: Total size in bites of the file
        :type block_num: int
        """

        if not self.pbar:
            self.pbar=progressbar.ProgressBar(maxval=total_size)
            self.pbar.start()

        downloaded = block_num * block_size
        if downloaded < total_size:
            self.pbar.update(downloaded)
        else:
            self.pbar.finish()


def count(func):
    """ Function that counts the number of times get_file is called recursevely.

    :param func: Function to be wrapped
    :type func: function
    """

    @wraps(func)
    def counted(*args):
        counted.call_count += 1
        return func(*args)
    counted.call_count = 0
    return counted


def get_file_parallel(log, num, sample, file):
    """Function that downloads the various samples in parallel from the CMS open-data portal.

    :param log: Configurated logger for printing messages.
    :type log: logging.RootLogger
    :param num: Number present in the url
    :type num: int
    :param sample: Name of the sample to download.
    :type sample: str
    :param file: Name of the file to be saved.
    :type file: str
    """

    count = 1
    while count <= 4:
        try:
            urllib.request.urlretrieve(f"http://opendata.cern.ch/record/{num}/files/{sample}.root", file)
        except urllib.error.HTTPError as http_err:
            log.exception("File %s.root can't be found %s",
                            sample, http_err, stack_info=True)
            return
        except urllib.error.ContentTooShortError:
            log.exception("Network conditions is not good. Reloading for %d time file %s.root", count, sample)
            count += 1
        else:
            return

    log.exception("Download of %s.root has failed due to bad network conditions!", sample)


@count
def get_file(log, num, sample, file):
    """Function that downloads the various samples not in parallel from the CMS open-data portal.
    This function, unlike parallel one, shows a progress bar (using a specific class created for
    this very purpose) and uses a decorator in order to count the number of times that
    is called recursively.

    The reason why this needlessly complicated function was defined
    is that it makes use of some tools that, in the rest of the project, weren't employed.


    :param log: Configurated logger for printing messages.
    :type log: logging.RootLogger
    :param num: Number present in the url
    :type num: int
    :param sample: Name of the sample to download.
    :type sample: str
    :param file: Name of the file to be saved.
    :type file: str
    """

    try:
        urllib.request.urlretrieve(f"http://opendata.cern.ch/record/{num}/files/{sample}.root", file, MyProgressBar())
    except urllib.error.HTTPError as http_err:
        log.exception("File %s.root can't be found %s",
                        sample, http_err, stack_info=True)
    except urllib.error.ContentTooShortError:
        log.exception("Network conditions is not good. Reloading for %d time file %s.root",
                        get_file.call_count, sample)
        if get_file.call_count == 4 :
            log.exception("Download of %s.root has failed due to bad network conditions! \n", sample)
            get_file.call_count=0
            return
        get_file(log, num, sample, file)
    else:
        get_file.call_count=0


def download(args, logger):
    """ Main function that creates the threads and sets up the multithread process.

    :param args: Global configuration of the analysis.
    :type args: argparse.Namespace
    :param logger: Configurated logger for printing messages.
    :type logger: logging.RootLogger
    """

    logger.info(">>> Executing %s \n", os.path.basename(__file__))
    t= perf_counter()

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
                parallel_list.append(thr.Thread(target=get_file_parallel, args=(logger, number, sample_name, file_name)))
            elif args.typeOfParallel == "process":
                logger.info(">>> Executing multi-processing \n")
                parallel_list.append(mp.Process(target=get_file_parallel, args=(logger, number, sample_name, file_name)))

        #start parallel
        for parallel_elem in parallel_list:
            parallel_elem.start()
        #join parallel
        for parallel_elem in parallel_list:
            parallel_elem.join()

    else:
        logger.info(">>> Executing not in parallel \n")
        #Loop over the various samples
        for sample_name, number in SAMPLES_DOWNLOAD.items():

            # Check if the sample is one of those requested by the user
            if sample_name not in args.sample and args.sample != "all":
                continue

            logger.info(">>> Process sample: %s \n", sample_name)
            file_name=os.path.join(args.download, f"{sample_name}.root")
            get_file(logger, number, sample_name, file_name)

    print("Time: "+str(perf_counter()-t))



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
