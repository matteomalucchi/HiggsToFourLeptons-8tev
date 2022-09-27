Welcome to HiggsToFourLeptons-8tev's documentation!
===================================================


**HiggsToFourLeptons-8tev** is a project that makes use of the Python language
and is interfaced with ROOT, and provides analysis tools for the Higgs decay in
two Z bosons which subsequently decay in four leptons. The datasets used are
reduced NanoAOD files created from `CMS Open Data <http://opendata.cern.ch/record/12360>`_
using data from Run 1 at 8 TeV for a total of 11.6 fb :math:`^{-1}`.
The analysis follows loosely
`the official CMS analysis published in 2012 <https://www.sciencedirect.com/science/article/pii/S0370269312008581>`_.
First, the dataset is "skimmed", i.e. all events which are not of interest for the reconstruction
of Higgs bosons are removed, and the various observables necessary for the analysis are computed.
The remaining variables are then plotted and the invariant mass of the four leptons
is fitted in order to measure the Higgs mass.
Subsequently, a Deep Neural Network is trained
using as input the simulated signal and background Monte Carlo samples and as discriminant
variables the invariant masses of the two reconstructed Z bosons and the five angles
formed by the leptons in the final state as described in detail in the article
`[Phys.Rev.D86:095031,2012] <https://journals.aps.org/prd/abstract/10.1103/PhysRevD.86.095031>`_.
Then, the DNN is evaluated on the whole dataset in order to obtain a graph in which the
distribution of the DNN Discriminant versus the invariant mass of the four leptons is plotted.
This shows a clear separation between signal and background, hence a further cut on the data based on this discriminant can be
applied in order to obtain a "cleaner" sample and better discriminate the signal from the background.

Check out the :doc:`usage` section for further information, including how to
:ref:`install <installation>` the project and how to :ref:`run the whole analysis <run_analysis>`.

The full list of modules can be found :ref:`here <modules>`.

.. toctree::
   usage
   Modules
   run_analysis
   set_up
   download_dataset
   skimming
   machine_learning
   histogramming
   plotting
   fit_mass
   test_skim
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
