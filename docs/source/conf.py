# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
from pathlib import Path

sys.path.insert(0, str(Path('..', '../src/').resolve()))

project = 'p4lantir'
copyright = '2025, acmo0'
author = 'acmo0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
	'sphinx.ext.autodoc',
	'sphinx.ext.coverage',
	'sphinx_rtd_theme',
	'sphinx.ext.duration',
	'sphinx.ext.doctest',
	'sphinx.ext.autosummary',
	'sphinx.ext.intersphinx',
	'sphinx.ext.viewcode',
	'sphinx.ext.githubpages',
	'sphinx_copybutton',
	'sphinx_multiversion',
]

# smv_tag_whitelist = r'\d+\.\d+\.\d+.*$|latest'
# # Whitelist pattern for branches (set to '' to ignore all branches)
# smv_branch_whitelist = ''
# smv_released_pattern = r'v.*'
# smv_latest_version = 'v0.1'
# smv_remote_whitelist = None

templates_path = ['_templates']

exclude_patterns = []

language = 'en'



# Versioning setup
smv_tag_whitelist = r'^.*$'
smv_branch_whitelist = "dev-doc|main"
smv_outputdir_format = '{ref.name}'


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_logo = "../../imgs/logo.svg"
autodoc_member_order = "bysource"
autodoc_preserve_defaults = True

pygments_style = 'sas'
highlight_options = {
	"python": {"linenos": True}
}

html_static_path = ['_static']

html_theme_options = {
    'logo_only': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'flyout_display': 'hidden',
    'version_selector': True,
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

