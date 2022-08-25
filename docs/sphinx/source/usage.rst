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
.. autofunction:: Machine_learning.ml_training.ml_training

ml_application
--------------
.. autofunction:: Machine_learning.ml_application.ml_application

ml_selection
------------
.. autofunction:: Machine_learning.ml_selection.ml_selection


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

..
   .. autofunction:: Test.test_skim.TestSkim.test_sip
   .. autofunction:: Test.test_skim.TestSkim.test_pt_cuts
   .. autofunction:: Test.test_skim.TestSkim.test_lep_fourvec
   .. autofunction:: Test.test_skim.TestSkim.test_z_idx_samekind
   .. autofunction:: Test.test_skim.TestSkim.test_z_fourvec_samekind
   .. autofunction:: Test.test_skim.TestSkim.test_z_fourvec_2mu2el
   .. autofunction:: Test.test_skim.TestSkim.test_deltar
   .. autofunction:: Test.test_skim.TestSkim.test_order_idx_z
   .. autofunction:: Test.test_skim.TestSkim.test_split_lep_samekind
   .. autofunction:: Test.test_skim.TestSkim.test_lep1
   .. autofunction:: Test.test_skim.TestSkim.test_lep2
   .. autofunction:: Test.test_skim.TestSkim.test_z_heavy
   .. autofunction:: Test.test_skim.TestSkim.test_z_light
   .. autofunction:: Test.test_skim.TestSkim.test_boost
   .. autofunction:: Test.test_skim.TestSkim.test_cross
   .. autofunction:: Test.test_skim.TestSkim.test_phi
   .. autofunction:: Test.test_skim.TestSkim.test_theta
   .. autofunction:: Test.test_skim.TestSkim.test_cos_theta

.. autoclass:: Test.test_skim.TestSkim
   :members:


..
   .. doxygenfunction:: sipDef

   .. doxygenfunction:: HiggsToFourLeptons-8tev::ptCuts
