""" Download the various sample from the CMS open-data portal.
"""

import urllib.error
import urllib.request
import argparse
import os 
import threading as thr
from time import perf_counter
from functools import wraps

import set_up


            
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
'''
def get_file(log, num, sample, file):
    """Function that downloads the various sample from the CMS open-data portal.

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
    while count <= 2:
        try:    
            urllib.request.urlretrieve(f"http://opendata.cern.ch/record/{num}/files/{sample}.root", file)
            break
        except urllib.error.HTTPError as http_err:
            log.exception("File %s.root can't be found %s", 
                            sample, http_err, stack_info=True)   
            break     
        except urllib.error.ContentTooShortError:
            log.exception("Network conditions is not good. Reloading for %d time file %s.root", count, sample)
            count += 1
    
    if count > 2:
        log.exception("Download of %s.root has failed due to bad network conditions!", sample)
'''

"""def count(func):
    @wraps(func)
    def counted(*args):
        counted.call_count += 1
        return func(*args)
    counted.call_count = 0
    return counted

@count
def get_file(log, num, sample, file):

    try:    
        urllib.request.urlretrieve(f"http://opendata.cern.ch/record/{num}/files/{sample}.root", file)
    except urllib.error.HTTPError as http_err:
        log.exception("File %s.root can't be found %s", 
                        sample, http_err, stack_info=True)   
    except urllib.error.ContentTooShortError:
        log.exception("Network conditions is not good. Reloading for %d time file %s.root", get_file.call_count, sample)
        if get_file.call_count == 10 : return
        get_file(log, num, sample, file)
    """

def download(args, logger):
    """ Main function that creates the threads and sets up the multithread process.

    :param args: Global configuration of the analysis.
    :type args: argparse.Namespace
    :param logger: Configurated logger for printing messages.
    :type logger: logging.RootLogger
    """

    logger.info(">>> Executing %s \n", os.path.basename(__file__))
   
    threads = []

    #Loop over the various samples
    for sample_name, number in SAMPLES_DOWNLOAD.items():
        
        # Check if the sample is one of those requested by the user
        if sample_name not in args.sample and args.sample != "all":
            continue
        
        logger.info(">>> Process sample: %s \n", sample_name)
        file_name=os.path.join(args.download, f"{sample_name}.root")
        
        threads.append(thr.Thread(target=get_file, args=(logger, number, sample_name, file_name)))

    t= perf_counter()
    
    #start threads
    for thread in threads:
        thread.start()
    #join threads
    for thread in threads:
        thread.join()
        
    print("Time: "+str(perf_counter()-t))
        

    
if __name__ == "__main__": 
    
    # General configuration
    parser = argparse.ArgumentParser( description = "Analysis Tool" )
    parser.add_argument("-p", "--parallel",   default=True,   action="store_const",
                            const=False, help="disables running in parallel")
    parser.add_argument("-n", "--nWorkers",   default=0,
                            type=int,   help="number of workers" )
    parser.add_argument("-l", "--logLevel",   default=20, type=int,   
                            help="integer representing the level of the logger:\
                             DEBUG=10, INFO = 20, WARNING = 30, ERROR = 40" ) 
    parser.add_argument("-s", "--sample",    default="all", type=str,
                            help="string with comma separated list of samples to analyse: \
                            Run2012B_DoubleElectron, Run2012B_DoubleMuParked, \
                            Run2012C_DoubleElectron,  Run2012C_DoubleMuParked, \
                            SMHiggsToZZTo4L, ZZTo2e2mu, ZZTo4e, ZZTo4mu")
    parser.add_argument("-d", "--download", default="Input", 
                            type=str, help="directory where to download the input data")
    args_main = parser.parse_args()

    logger_main=set_up.set_up(args_main)
    
    download(args_main, logger_main)
    