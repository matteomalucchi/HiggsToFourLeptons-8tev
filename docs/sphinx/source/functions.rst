Run the whole analysis
======================

run_analysis.py
---------------
.. autofunction:: run_analysis.run_analysis
..
    .. argparse::
        :filename: ../../run_analysis.py
        :func: run_analysis
        :prog: fancytools


Set up the analysis
===================

set_up.py
---------
.. autofunction:: set_up.set_up
.. autofunction:: set_up.check_val
.. autofunction:: set_up.create_dir


Download the datasets
=====================

download.py
-----------
.. autofunction:: download.download
.. autofunction:: download.get_file


Skimming
========

Skimming/skim.py
----------------
.. autofunction:: Skimming.skim.skim

Skimming/skim_tools.py
----------------------
.. autofunction:: Skimming.skim_tools.event_selection
.. autofunction:: Skimming.skim_tools.four_vec
.. autofunction:: Skimming.skim_tools.order_four_vec
.. autofunction:: Skimming.skim_tools.def_mass_pt_eta_phi
.. autofunction:: Skimming.skim_tools.four_vec_boost
.. autofunction:: Skimming.skim_tools.def_angles
.. autofunction:: Skimming.skim_tools.add_event_weight


Machine learning 
================

MachineLearning/ml_training.py
------------------------------
.. autofunction:: Machine_Learning.ml_training.ml_training

MachineLearning/ml_application.py
---------------------------------
.. autofunction:: Machine_Learning.ml_application.ml_application

MachineLearning/ml_selection.py
-------------------------------
.. autofunction:: Machine_Learning.ml_selection.ml_selection


Histogramming
=============

Histogramming/make_histo.py
---------------------------
.. autofunction:: Histogramming.make_histo.make_histo

Histogramming/ml_histo.py
-------------------------
.. autofunction:: Histogramming.ml_histo.ml_histo

Histogramming/histogramming_functions.py
----------------------------------------
.. autofunction:: Histogramming.histogramming_functions.book_histogram_1d
.. autofunction:: Histogramming.histogramming_functions.book_histogram_2d
.. autofunction:: Histogramming.histogramming_functions.write_histogram


Plotting
========

Plotting/make_plot.py
---------------------
.. autofunction:: Plotting.make_plot.make_plot

Plotting/ml_plot.py
-------------------
.. autofunction:: Plotting.ml_plot.ml_plot

Plotting/plotting_functions.py
------------------------------
.. autofunction:: Plotting.plotting_functions.get_histogram
.. autofunction:: Plotting.plotting_functions.combine_final_states
.. autofunction:: Plotting.plotting_functions.set_style
.. autofunction:: Plotting.plotting_functions.input_style
.. autofunction:: Plotting.plotting_functions.add_title
.. autofunction:: Plotting.plotting_functions.add_legend
.. autofunction:: Plotting.plotting_functions.add_latex


Higgs mass fit
==============

fit_mass.py
-----------
.. autofunction:: fit_mass.fit_mass


Test Skim
=========

Test/test_skim.py
-----------------

.. autoclass:: Test.test_skim.TestSkim
   :members:
