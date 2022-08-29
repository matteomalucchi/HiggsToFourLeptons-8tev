Usage
=====

.. _installation:

Installation
------------

To use HiggsToFourLeptons-8tev, first clone the
`repository from GitHub <https://github.com/matteomalucchi/HiggsToFourLeptons-8tev>`_:

.. code-block:: console

   $ git clone https://github.com/matteomalucchi/HiggsToFourLeptons-8tev.git



Run the whole analysis
======================

run_analysis
------------
.. autofunction:: run_analysis.run_analysis


Set up the analysis
===================

set_up
------
.. autofunction:: set_up.set_up


Skimming
========

skim
----
.. autofunction:: Skimming.skim.skim

skim_tools
----------
.. autofunction:: Skimming.skim_tools.event_selection
.. autofunction:: Skimming.skim_tools.four_vec
.. autofunction:: Skimming.skim_tools.order_four_vec
.. autofunction:: Skimming.skim_tools.def_mass_pt_eta_phi
.. autofunction:: Skimming.skim_tools.four_vec_boost
.. autofunction:: Skimming.skim_tools.def_angles
.. autofunction:: Skimming.skim_tools.add_event_weight


Machine learning 
================

ml_training
-----------
.. autofunction:: Machine_Learning.ml_training.ml_training

ml_application
--------------
.. autofunction:: Machine_Learning.ml_application.ml_application

ml_selection
------------
.. autofunction:: Machine_Learning.ml_selection.ml_selection


Histogramming
=============

make_histo
----------
.. autofunction:: Histogramming.make_histo.make_histo

ml_histo
--------
.. autofunction:: Histogramming.ml_histo.ml_histo

histogramming_functions
-----------------------
.. autofunction:: Histogramming.histogramming_functions.book_histogram_1d
.. autofunction:: Histogramming.histogramming_functions.book_histogram_2d
.. autofunction:: Histogramming.histogramming_functions.write_histogram


Plotting
========

make_plot
---------
.. autofunction:: Plotting.make_plot.make_plot

ml_plot
-------
.. autofunction:: Plotting.ml_plot.ml_plot

plotting_functions
------------------


.. autofunction:: Plotting.plotting_functions.get_histogram
.. autofunction:: Plotting.plotting_functions.combine_final_states
.. autofunction:: Plotting.plotting_functions.set_style
.. autofunction:: Plotting.plotting_functions.input_style
.. autofunction:: Plotting.plotting_functions.add_title
.. autofunction:: Plotting.plotting_functions.add_legend
.. autofunction:: Plotting.plotting_functions.add_latex


Higgs mass fit
==============

fit_mass
--------
.. autofunction:: fit_mass.fit_mass


Test Skim
=========

test_skim
---------

.. autoclass:: Test.test_skim.TestSkim
   :members:

