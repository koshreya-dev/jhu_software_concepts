import os
import sys
sys.path.insert(0, os.path.abspath('../../src'))

autodoc_mock_imports = ["bs4", "psycopg_pool", "psycopg", "flask"]

project = 'GradCafe Data Analysis'
author = 'Shreya Kodati'
release = '1.0'

# Extensions
extensions = [
    'sphinx.ext.autodoc',      # Automatically document your modules
    'sphinx.ext.napoleon',     # For Google/NumPy style docstrings
    'sphinx.ext.viewcode',     # Add links to source code
]

templates_path = ['_templates']
exclude_patterns = []

# HTML options
html_theme = 'alabaster'  # Can use 'sphinx_rtd_theme' if installed
html_static_path = ['_static']
