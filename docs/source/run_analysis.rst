Run the whole analysis
======================

run_analysis.py
---------------
.. autofunction:: run_analysis.run_analysis

The options for running the analysis include:

.. code-block:: console

    -h, --help            show this help message and exit
    -l LOGLEVEL, --logLevel LOGLEVEL
                            integer representing the level of the logger: DEBUG=10, INFO = 20, WARNING = 30, ERROR = 40
    -d [DOWNLOAD], --download [DOWNLOAD]
                            enables the download of input data. If not specified otherwise the files are saved in the 'Input/' directory
    -b [BASEPATH], --basePath [BASEPATH]
                            base path where to find the input data. If enabled it automatically gets the input data from EOS unless a local directory is specified
    -o OUTPUT, --output OUTPUT
                            name of the output directory
    -c [CLEAROUTPUT], --clearOutput [CLEAROUTPUT]
                            name of output folder to be deleted. If not specified otherwise the 'Output/' directory is deleted
    -q, --skim            disables the skimming step
    -m, --ml              disables machine learning algorithm
    -g, --graphPlots      disables the graphing of the distribution plots
    -i, --invariantMassFit
                            disables fit of the Higgs mass
    -s SAMPLE, --sample SAMPLE
                            string with comma separated list of samples to analyse: Run2012B_DoubleElectron, Run2012B_DoubleMuParked, Run2012C_DoubleElectron, Run2012C_DoubleMuParked, SMHiggsToZZTo4L,
                            ZZTo2e2mu, ZZTo4e, ZZTo4mu
    -f FINALSTATE, --finalState FINALSTATE
                            comma separated list of the final states to analyse: FourMuons,FourElectrons,TwoMuonsTwoElectrons
    -e, --typeOfParallel  parallel type for the downloads: default is multi-thread, if activated is multi-process
    -p, --parallel        disables running in parallel
    -n NWORKERS, --nWorkers NWORKERS
                            number of workers for multi-threading
    -r [RANGE], --range [RANGE]
                            number of events on which the analysis is ran over (does not work in parallel)
    -a MLVARIABLES, --MLVariables MLVARIABLES
                            name of the set of variables to be used in the ML algorithm defined 'Analysis/Definitions/variables_ml_def.py': tot, angles, higgs
    -v VARIABLEDISTRIBUTION, --variableDistribution VARIABLEDISTRIBUTION
                            string with comma separated list of the variables to plot. The complete list is defined in 'Analysis/Definitions/variables_def.py'
    -t TYPEDISTRIBUTION, --typeDistribution TYPEDISTRIBUTION
                            comma separated list of the type of distributions to plot: data, background, signal, sig_bkg_normalized, total
