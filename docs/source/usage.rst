Usage
=====

.. _installation:

Installation
------------

To use HiggsToFourLeptons-8tev, first clone the
`repository from GitHub <https://github.com/matteomalucchi/HiggsToFourLeptons-8tev>`_:

.. code-block:: console

   $ git clone https://github.com/matteomalucchi/HiggsToFourLeptons-8tev.git


.. _skimming:

Skimming
========

skim
----
.. autofunction:: skimming.skim.skim

skim_tools
----------
.. autofunction:: skimming.skim_tools.EventSelection
.. autofunction:: skimming.skim_tools.FourVec
.. autofunction:: skimming.skim_tools.OrderFourVec
.. autofunction:: skimming.skim_tools.DefMassPtEtaPhi
.. autofunction:: skimming.skim_tools.FourvecBoost
.. autofunction:: skimming.skim_tools.DefAngles
.. autofunction:: skimming.skim_tools.AddEventWeight


Machine learning 
================

ml_training
-----------
.. autofunction:: machine_learning.ml_training.ml_training

ml_application
--------------
.. autofunction:: machine_learning.ml_application.ml_application

ml_selection
------------
.. autofunction:: machine_learning.ml_selection.ml_selection


Histogramming
=============

make_histo
----------
.. autofunction:: histogramming.make_histo.make_histo

ml_histo
--------
.. autofunction:: histogramming.ml_histo.ml_histo

histogramming_functions
-----------------------
.. autofunction:: histogramming.histogramming_functions.BookHistogram1D
.. autofunction:: histogramming.histogramming_functions.BookHistogram2D
.. autofunction:: histogramming.histogramming_functions.WriteHistogram


Plotting
========

make_plot
---------
.. autofunction:: plotting.make_plot.make_plot

ml_plot
-------
.. autofunction:: plotting.ml_plot.ml_plot

plotting_functions
------------------
.. autofunction:: plotting.plotting_functions.GetHistogram
.. autofunction:: plotting.plotting_functions.CombineFinalStates
.. autofunction:: plotting.plotting_functions.SetStyle
.. autofunction:: plotting.plotting_functions.InputStyle
.. autofunction:: plotting.plotting_functions.AddTitle
.. autofunction:: plotting.plotting_functions.AddLegend
.. autofunction:: plotting.plotting_functions.AddLatex


Higgs mass fit
==============

fit_mass
--------
.. autofunction:: fit_mass.fit_mass
