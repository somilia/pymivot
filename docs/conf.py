import sys, os

sys.path.insert(0, os.path.abspath('../..'))
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary'
    ]
autosummary_generate = True

autodoc_mock_imports = ["astropy", "lxml", "xmltodict", "numpy", "xmlschema"]
