# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here.

import sys
import os

sys.path.insert(0, os.path.abspath("../.."))
sys.setrecursionlimit(1500)

project = "HiggsToFourLeptons-8tev"
copyright = "2022, matteomalucchi"
author = "matteomalucchi"
release = "0.1"

master_doc = 'index'


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'readthedocs_ext.readthedocs',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
]

"""    "sphinx.ext.duration",
    "sphinx.ext.mathjax",
    "sphinx.ext.imgmath", 
    "sphinx.ext.todo",
    "breathe",
    "sphinxarg.ext"""

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

"""
import subprocess
subprocess.call("make clean", shell=True)
subprocess.call("cd ../../doxygen ; doxygen Doxygen", shell=True)

breathe_projects = { "HiggsToFourLeptons_8tev": "../../doxygen/build/xml/" }
breathe_default_project = "HiggsToFourLeptons_8tev"
"""