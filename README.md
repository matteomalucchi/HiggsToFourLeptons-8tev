<a href='https://higgstofourleptons-8tev.readthedocs.io/en/latest/'>
    <img src='https://readthedocs.org/projects/higgstofourleptons-8tev/badge/?version=latest' alt='Documentation Status' />
</a>

# Analysis of Higgs boson decays to four leptons

## Introduction
This repository contains an analysis of the decay of a Higgs boson into two Z bosons which in turn decay in four leptons using reduced NanoAOD files created from CMS Open Data. The analysis follows loosely 
[the official CMS analysis published in 2012](https://www.sciencedirect.com/science/article/pii/S0370269312008581) and
consists in two main parts: the reconstruction of the Higgs boson mass and 
the development of a machine learning algorithm which allows for a better 
discrimination between signal and background. The first is obtained by "skimming" 
the dataset, i.e. by removing all events which are not of interest for the reconstruction
of Higgs bosons, and by computing the various observables necessary for the analysis.
The remaining variables are finally plotted distinguishing the data from the simulated 
signal and background. The second part consists in training a machine learning algorithm
using as input the simulated signal and background Monte Carlo samples and as discriminant
variables the invariant masses of the two reconstructed Z bosons and the five angles 
formed by the leptons in the final state as described in detail in the article 
[[Phys.Rev.D86:095031,2012]](https://journals.aps.org/prd/abstract/10.1103/PhysRevD.86.095031). 
Then, the algorithm is applied to the whole dataset in order to obtain a graph in which the 
distribution of the kinematic discriminant versus the invariant mass of the four leptons is plotted.
This shows a clear separation between signal and background, hence a further cut on the data can be 
applied in order to obtain a "cleaner" sample. Finally, the invariant mass of the four leptons 
is fitted in order to obtain an estimate of the Higgs mass.

## How to run this

### Run the analysis
The complete analysis can be performed the first time by simply running 

>       python run_analysis.py -d

which also downloads the locally the input datasets. The several options may be displayed by typing

>       python run_analysis.py --help

The options include:


>  -d [DOWNLOAD], --download [DOWNLOAD]     enables the download of input data
>  -c [CLEAROUTPUT], --clearOutput [CLEAROUTPUT]       name of output folder to be deleted
>  -r [RANGE], --range [RANGE]      number of events on which the analysis is ran over (does not work in parallel)
>  -p, --parallel        disables running in parallel
>  -n NWORKERS, --nWorkers NWORKERS        number of workers
>  -l LOGLEVEL, --logLevel LOGLEVEL        integer representing the level of the logger: DEBUG=10, INFO = 20, WARNING = 30, ERROR = 40
>  -f FINALSTATE, --finalState FINALSTATE     comma separated list of the final states to analyse: FourMuons,FourElectrons,TwoMuonsTwoElectrons
>  -m, --ml              disables machine learning algorithm
>  -a ALGORITHMMLVAR, --algorithmMLVar ALGORITHMMLVAR      name of the set of variables to be used in the ML algorithm defined 'variables_ml_def.py': tot, part, higgs
>  -i, --invariantMassFit       disables fit of the Higgs mass
>  -g, --graphPlots      disables the graphing of the distribution plots
>  -t TYPEDISTRIBUTION, --typeDistribution TYPEDISTRIBUTION        comma separated list of the type of distributions to plot: data, background, signal, sig_bkg_normalized, total
>  -s SAMPLE, --sample SAMPLE       string with comma separated list of samples to analyse: Run2012B_DoubleElectron, Run2012B_DoubleMuParked, Run2012C_DoubleElectron, Run2012C_DoubleMuParked, SMHiggsToZZTo4L, ZZTo2e2mu, ZZTo4e, ZZTo4mu
>  -v VARIABLEDISTRIBUTION, --variableDistribution VARIABLEDISTRIBUTION       string with comma separated list of the variables to plot. The complete list is defined in 'variables_def.py'
>  -b [BASEPATH], --basePath [BASEPATH]      base path where to find the input data. If enabled it automatically gets the input data from EOS
>  -o OUTPUT, --output OUTPUT     name of the output directory


### Skimming





