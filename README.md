<a href='https://higgstofourleptons-8tev.readthedocs.io/en/latest/contents.html'>
    <img src='https://readthedocs.org/projects/higgstofourleptons-8tev/badge/?version=latest' alt='Documentation Status' />
</a>

# Analysis of Higgs boson decays to four leptons

This repository contains an analysis of the decay of a Higgs boson into two Z bosons which in turn decay in four leptons using reduced NanoAOD files created from CMS Open Data. The analysis follows loosely 
\href{https://www.sciencedirect.com/science/article/pii/S0370269312008581}{the official CMS analysis published in 2012} and
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
\href{https://journals.aps.org/prd/abstract/10.1103/PhysRevD.86.095031}{[Phys.Rev.D86:095031,2012]}. 
Then, the algorithm is applied to the whole dataset in order to obtain a graph in which the 
distribution of the kinematic discriminant $K_D$ versus the invariant mass of the four leptons is plotted.
This shows a clear separation between signal and background, hence a further cut on the data can be 
applied in order to obtain a "cleaner" sample. Finally, the invariant mass of the four leptons 
is fitted in order to obtain an estimate of the Higgs mass.

# How to run this

The complete analysis can be performed by simply running `python run_analysis.py`. The single steps can be executed separately as explained in more detail below.


