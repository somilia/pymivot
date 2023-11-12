import sys, os

# path to source
this_path = os.path.dirname(os.path.abspath(__file__))
packagedir = os.path.join(this_path, '..','mivot_validator')

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}
