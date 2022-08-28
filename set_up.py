import argparse
import os
import shutil
import logging

def set_up (args):      
    
    # Create and configure logger
    logging.basicConfig( format='\n%(asctime)s - %(filename)s - %(message)s')
    # Create an object
    logger=logging.getLogger() 
       
    # Check if logLevel valid
    try:
        if args.logLevel not in [10, 20, 30, 40]:
            raise argparse.ArgumentTypeError(f"the value for logLevel {args.logLevel} is invalid: it must be either 10, 20, 30 or 40")
    except argparse.ArgumentTypeError as arg_err:
        logger.exception("%s \n logLevel is set to 20 \n", arg_err, stack_info=True)
        args.logLevel = 20
    except AttributeError:
        pass
        
    # Set the threshold of logger
    logger.setLevel(args.logLevel)   
    
    
    # Check if typeDistribution is valid
    try:
        if not any(type_distribution in args.typeDistribution.split(",") for type_distribution 
               in ["all", "data", "background", "signal", "sig_bkg_normalized", "total"]):
            raise argparse.ArgumentTypeError(f"the type of distribution {args.typeDistribution} is invalid: \
                it must be either all,data,background,signal,sig_bkg_normalized,total")
    except argparse.ArgumentTypeError as arg_err:
        logger.exception("%s \n typeDistribution is set to all \n", arg_err, stack_info=True)
        args.typeDistribution = "all"       
    except AttributeError:
        pass    
    
    # Check if finalState is valid
    try:
        if not any(final_state in args.finalState.split(",") for final_state 
               in ["all", "FourMuons", "FourElectrons", "TwoMuonsTwoElectrons"]):
            raise argparse.ArgumentTypeError(f"the final state {args.finalState} is invalid: \
                it must be either all,FourMuons,FourElectrons,TwoMuonsTwoElectrons")
    except argparse.ArgumentTypeError as arg_err:
        logger.exception("%s \n finalState is set to all \n", arg_err, stack_info=True)
        args.finalState = "all"  
    except AttributeError:
        pass        
    
    # Check if variablesML is valid
    try:
        if not any(var_ml in args.variablesML for var_ml 
               in ["tot", "part", "higgs"]):
            raise argparse.ArgumentTypeError(f"the set of ML variables {args.variablesML} is invalid: \
                it must be either tot, part, higgs")
    except argparse.ArgumentTypeError as arg_err:
        logger.exception("%s \n variablesML is set to tot \n", arg_err, stack_info=True)
        args.variablesML = "tot"    
    except AttributeError:
        pass
    
    # Check if sample is valid
    try:
        if not any(sample in args.sample.split(",") for sample 
               in ["all", "Run2012B_DoubleElectron", "Run2012B_DoubleMuParked", "Run2012C_DoubleElectron", 
                   "Run2012C_DoubleMuParked", "SMHiggsToZZTo4L", "ZZTo2e2mu", "ZZTo4e", "ZZTo4mu"]):
            raise argparse.ArgumentTypeError(f"the sample {args.sample} is invalid: \
                it must be either all, Run2012B_DoubleElectron, Run2012B_DoubleMuParked, Run2012C_DoubleElectron, \
                Run2012C_DoubleMuParked, SMHiggsToZZTo4L, ZZTo2e2mu, ZZTo4e, ZZTo4mu")
    except argparse.ArgumentTypeError as arg_err:
        logger.exception("%s \n sample is set to all \n", arg_err, stack_info=True)
        args.sample = "all"    
    except AttributeError:
        pass        
        
    # Clear the output folder
    if args.clearOutput != "":
        try:
            shutil.rmtree(args.clearOutput)
        except OSError as os_err:
            logger.debug("ERROR directory %s/ could not be deleted: \n %s", args.clearOutput, os_err)
        else:
            logger.debug("Directory %s/ has been succesfully deleted", args.clearOutput)


    # Create the directory to save the outputs if doesn't already exist
    try:
        os.makedirs(args.output)
        logger.debug("Directory %s/ Created", args.output)
    except FileExistsError:
        logger.debug("The directory %s/ already exists", args.output)
        
    return logger
    