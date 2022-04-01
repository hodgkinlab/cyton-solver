"""
This script contains model setting variables as well as the program status variables.
"""

# Cyton 1 PDF settings
CYTON1_CONFIG = {
	'first_div': 'Lognormal',
	'first_die': 'Lognormal',
	'subsq_div': 'Lognormal',
	'subsq_die': 'Lognormal'
}

# Cyton 1.5 PDF default settings - Lognormal
CYTON15_CONFIG = {
	'unstim_die': 'Lognormal',
	'stim_div': 'Lognormal',
	'stim_die': 'Lognormal',
	'stim_dd': 'Lognormal'
}
# Cyton 1.5 PDF default settings - Gaussian
# CYTON15_CONFIG = {
# 	'unstim_die': 'Gaussian',
# 	'stim_div': 'Gaussian',
# 	'stim_die': 'Gaussian',
# 	'stim_dd': 'Gaussian'
# }

# program specific settings
CONSOLE = None
TOGGLE_CONSOLE = False  # console state check

# imported file related variables
FILE_LOADED = False
FILE_NAME = ''
FILE_PATH = ''
FULL_FILE_PATH = ''

DATA_FREE = True  # revert back to data free mode
