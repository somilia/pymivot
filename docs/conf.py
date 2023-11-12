import sys, os

sys.path.insert(0, os.path.abspath('../mivot_validator'))
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

extensions = [
    'sphinx.ext.autodoc'
    ]
