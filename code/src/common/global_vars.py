"""
This file contains global variables that constantly updating & called throughout the program.
Various action listeners are linked and as such user inputs values are handled and stored in here.

Perhaps this is not the best way to manage model related parameters but it is definitely easier way to construct
communication between different modules.
"""

# default Cyton model variables
TIME_INC = 1.
MAX_DIV = 10
INIT_CELL = 10000.
HT = [0., 16., 54., 80., 106., 120.]

# Cyton 1 defaults
C1_ICND = 0  # this index represents selected condition in imported data file for Cyton 1
C1_PARAMS = {
	'mu0div': 40.0, 'sig0div': 0.2,
	'mu0death': 60.0, 'sig0death': 0.2,
	'muSubdiv': 15.0, 'sigSubdiv': 0.5,
	'muSubdeath': 13.0, 'sigSubdeath': 0.4,
	'pf0': 1.0, 'pfmu': 10.0, 'pfsig': 2.0,
	'MechProp': 0.0, 'MechDecayConst': 0.5
}
C1_VARY_PARAMS = {
	'mu0divLock': True, 'sig0divLock': True,
	'mu0deathLock': True, 'sig0deathLock': True,
	'muSubdivLock': True, 'sigSubdivLock': True,
	'muSubdeathLock': True, 'sigSubdeathLock': True,
	'pf0Lock': True, 'pfmuLock': True, 'pfsigLock': True,
	'MechPropLock': True, 'MechDecayConstLock': True
}
C1_UPPER_BOUNDS = {
	'mu0divUpperBound': 100.0, 'sig0divUpperBound': 1.0,
	'mu0deathUpperBound': 100.0, 'sig0deathUpperBound': 1.0,
	'muSubdivUpperBound': 100.0, 'sigSubdivUpperBound': 1.0,
	'muSubdeathUpperBound': 100.0, 'sigSubdeathUpperBound': 1.0,
	'pf0UpperBound': 1.0, 'pfmuUpperBound': 50.0, 'pfsigUpperBound': 5.0,
	'MechPropUpperBound': 1.0, 'MechDecayConstUpperBound': 1.0
}

# Cyton 1.5 defaults - Lognormal
C15_ICND = 0  # this index represents selected condition in imported data file for Cyton 1.5
C15_PARAMS = {
	'unstimMuDeath': 15.0, 'unstimSigDeath': 0.5,
	'stimMuDiv': 25.0, 'stimSigDiv': 0.2,
	'stimMuDeath': 75.0, 'stimSigDeath': 0.2,
	'stimMuDD': 50.0, 'stimSigDD': 0.15,
	'SubDivTime': 10.0, 'pfrac': 0.7
}
C15_VARY_PARAMS = {
	'unstimMuDeathLock': True, 'unstimSigDeathLock': True,
	'stimMuDivLock': True, 'stimSigDivLock': True,
	'stimMuDeathLock': True, 'stimSigDeathLock': True,
	'stimMuDDLock': True, 'stimSigDDLock': True,
	'SubDivTimeLock': True, 'pfracLock': True
}
C15_UPPER_BOUNDS = {
	'unstimMuDeathUpperBound': 300.0, 'unstimSigDeathUpperBound': 1.0,
	'stimMuDivUpperBound': 200.0, 'stimSigDivUpperBound': 1.0,
	'stimMuDeathUpperBound': 300.0,  'stimSigDeathUpperBound': 1.0,
	'stimMuDDUpperBound': 300.0, 'stimSigDDUpperBound': 1.0,
	'SubDivTimeUpperBound': 50.0, 'pfracUpperBound': 1.0
}
# Cyton 1.5 defaults - Gaussian
# C15_PARAMS = {
# 	'unstimMuDeath': 15.0, 'unstimSigDeath': 10.,
# 	'stimMuDiv': 25.0, 'stimSigDiv': 10.,
# 	'stimMuDeath': 75.0, 'stimSigDeath': 15.,
# 	'stimMuDD': 50.0, 'stimSigDD': 12.,
# 	'SubDivTime': 10.0, 'pfrac': 0.7
# }
# C15_UPPER_BOUNDS = {
# 	'unstimMuDeathUpperBound': 300.0, 'unstimSigDeathUpperBound': 200.0,
# 	'stimMuDivUpperBound': 200.0, 'stimSigDivUpperBound': 200.0,
# 	'stimMuDeathUpperBound': 300.0,  'stimSigDeathUpperBound': 200.0,
# 	'stimMuDDUpperBound': 300.0, 'stimSigDDUpperBound': 200.0,
# 	'SubDivTimeUpperBound': 50.0, 'pfracUpperBound': 1.0
# }

# TODO: fill in Cyton 2 model later!

# Data management variables
TOTAL_CELLS, TOTAL_CELLS_REPS, TOTAL_CELLS_SEM = [], [], []
CELL_GENS, CELL_GENS_REPS, CELL_GENS_SEM = [], [], []
EXP_HT, EXP_HT_REPS, EXP_NUM_TP = [], [], []
CONDITIONS = []
MAX_DIV_PER_CONDITIONS = []

# Fit related variables
C1_PREV_SS, C1_SS = 0., 0.  # report sum of squares residue
C15_PREV_SS, C15_SS = 0., 0.
C1_CHECK, C15_CHECK = [], []  # check matrices for Cyton 1 & Cyton 1.5 for data inclusion/exclusion
