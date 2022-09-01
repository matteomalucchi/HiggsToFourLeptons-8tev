Welcome to HiggsToFourLeptons-8tev's documentation!
===================================================


**HiggsToFourLeptons-8tev** is a project that makes use of the Python language 
and is interfaced with ROOT, and provides analysis tools for the Higgs decay in
two Z bosons which subsequently decay in four leptons. The datasets used are
reduced NanoAOD files created from `CMS Open Data <http://opendata.cern.ch/record/12360>`_.
The analysis follows loosely 
`the official CMS analysis published in 2012 <https://www.sciencedirect.com/science/article/pii/S0370269312008581>`_
and consists in two main parts: the reconstruction of the Higgs boson mass and 
the development of a machine learning algorithm which allows for a better 
discrimination between signal and background. The first is obtained by "skimming" 
the dataset, i.e. by removing all events which are not of interest for the reconstruction
of Higgs bosons, and by computing the various observables necessary for the analysis.
The remaining variables are finally plotted distinguishing the data from the simulated 
signal and background. The second part consists in training a machine learning algorithm
using as input the simulated signal and background Monte Carlo samples and as discriminant
variables the invariant masses of the two reconstructed Z bosons and the five angles 
formed by the leptons in the final state as described in detail in the article 
`[Phys.Rev.D86:095031,2012] <https://journals.aps.org/prd/abstract/10.1103/PhysRevD.86.095031>`_. 
Then, the algorithm is applied to the whole dataset in order to obtain a graph in which the 
distribution of the kinematic discriminant $K_D$ versus the invariant mass of the four leptons is plotted.
This shows a clear separation between signal and background, hence a further cut on the data can be 
applied in order to obtain a "cleaner" sample. Finally, the invariant mass of the four leptons 
is fitted in order to obtain an estimate of the Higgs mass.

Check out the :doc:`usage` section for further information, including how to
:ref:`install <installation>` the project.



.. note::

   This project is under active development.

.. toctree::
   usage
   run_analysis
   set_up
   download
   skimming
   machine_learning
   histogramming
   plotting
   fit_mass
   test_skim
   api
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
