# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'mivot-validator'
author = 'Laurent MICHEL'
release = '0.0.1'

import sys, os
sys.path.insert(0, os.path.abspath('../..'))
sys.path.insert(0, os.path.abspath('../'))


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_click.ext",
    "sphinx_rtd_theme",
    "sphinx.ext.autodoc",  # allows to generate .rst files from docstring
    "sphinx.ext.napoleon", # allows sphinx to parse numpy and Google style docstrings
    "sphinx.ext.viewcode", # add possibility to view source code
    "sphinx.ext.intersphinx", # can generate automatic links to the documentation of objects in other projects.
    "sphinx.ext.extlinks", # Markup to shorten external links
    "sphinx.ext.doctest", # Test snippets in the documentation
    "sphinx.ext.autosummary", # Generate autodoc summaries
 ]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
