"""
This module is the final stage of the optimisation preparation. It sorts the data in appropriate format as well as
caries fit settings provided by the user.

A spawned thread will call one of these functions to initialise the fitting process using LMFIT package.
"""

import time
import numpy as np
from lmfit import Model

import src.common.global_vars as gvars
from src.workbench.cyton1 import Cyton1Model
from src.workbench.cyton15 import Cyton15Model


def print_elapsed_time(start, end):
	hours, rem = divmod(end - start, 3600)
	minutes, seconds = divmod(rem, 60)
	print(" > Total elapsed time - {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))


def callback_print_function(pars, iter, resid, *args, **kws):
	# resid : user-defined model - data (lmfit.Model object)
	total_residual = 0.
	for res in resid:
		total_residual += res**2

	if iter % 100 == 0:
		print(
			"ITER   " + str(iter) + "   ",
			['%3.6f' % p.value for p in pars.values()],
			"%.5e" % total_residual
		)


def fit_to_cyton1(thread, algo_settings):
	start = time.time()

	print(
		'{0:9s}   {1:13} {2:13} {3:13} {4:13} {5:13} {6:13} {7:13} {8:13} {9:13} {10:13} {11:13} {12:13} {13:13} {14:13}'.format(
			'ITER', 'mu0Div', ' sig0Div', ' mu0Death', ' sig0Death', ' muSubDiv', ' sigSubDiv', ' muSubDeath',
			' sigSubDeath', ' pF0', ' pfMu', ' pfSig', 'MDProp', 'MDDecay', 'RSS')
	)

	# selected condition for fitting
	icnd = gvars.C1_ICND

	# prepare (x, y) data
	num_reps = [len(l) for l in gvars.CELL_GENS_REPS[icnd]]
	flatten_gens, flatten_cells = [], []
	for itpt in range(len(gvars.EXP_HT[icnd])):
		for irep in range(num_reps[itpt]):
			for igen in range(gvars.MAX_DIV_PER_CONDITIONS[icnd]+1):
				if gvars.C1_CHECK[icnd][itpt][irep][igen]:
					flatten_gens.append(igen)
					flatten_cells.append(gvars.CELL_GENS_REPS[icnd][itpt][irep][igen])

	x = np.array(flatten_gens, dtype=float)
	y = np.array(flatten_cells, dtype=float)

	model = Cyton1Model(
		gvars.EXP_HT[icnd], gvars.INIT_CELL, gvars.MAX_DIV, gvars.TIME_INC, num_reps, gvars.C1_CHECK[icnd], thread
	)

	try:
		gmodel = Model(
			model.cyton1_model,
			independent_vars=['flatten_generation_list'],
			param_names=[
				'mu0Div', 'sig0Div',
				'mu0Death', 'sig0Death',
				'muSubDiv', 'sigSubDiv',
				'muSubDeath', 'sigSubDeath',
				'pF0', 'pFMu', 'pFSig',
				'MDProp', 'MDDecay'
			],
			name='Cyton 1 Model'
		)

		params = gvars.C1_PARAMS
		upper_bounds = gvars.C1_UPPER_BOUNDS
		vary = gvars.C1_VARY_PARAMS
		# 13 parameters to fit :
		#  - mu0Div, sig0Dive, mu0Death, sig0Death, muSubDiv, sigSubDiv, muSubDeath, sigSubDeath
		#  - pf0, pfMu, pfSig, Mechanical death proportion, Mechanical death decay
		gmodel.set_param_hint('mu0Div', value=params['mu0div'], min=0.001, max=upper_bounds['mu0divUpperBound'], vary=vary['mu0divLock'])
		gmodel.set_param_hint('sig0Div', value=params['sig0div'], min=0.001, max=upper_bounds['sig0divUpperBound'], vary=vary['sig0divLock'])
		gmodel.set_param_hint('mu0Death', value=params['mu0death'], min=0.001, max=upper_bounds['mu0deathUpperBound'], vary=vary['mu0deathLock'])
		gmodel.set_param_hint('sig0Death', value=params['sig0death'], min=0.001, max=upper_bounds['sig0deathUpperBound'], vary=vary['sig0deathLock'])
		gmodel.set_param_hint('muSubDiv', value=params['muSubdiv'], min=0.001, max=upper_bounds['muSubdivUpperBound'], vary=vary['muSubdivLock'])
		gmodel.set_param_hint('sigSubDiv', value=params['sigSubdiv'], min=0.001, max=upper_bounds['sigSubdivUpperBound'], vary=vary['sigSubdivLock'])
		gmodel.set_param_hint('muSubDeath', value=params['muSubdeath'], min=0.001, max=upper_bounds['muSubdeathUpperBound'], vary=vary['muSubdeathLock'])
		gmodel.set_param_hint('sigSubDeath', value=params['sigSubdeath'], min=0.001, max=upper_bounds['sigSubdeathUpperBound'], vary=vary['sigSubdeathLock'])

		gmodel.set_param_hint('pF0', value=params['pf0'], min=0.001, max=upper_bounds['pf0UpperBound'], vary=vary['pf0Lock'])
		gmodel.set_param_hint('pFMu', value=params['pfmu'], min=0.001, max=upper_bounds['pfmuUpperBound'], vary=vary['pfmuLock'])
		gmodel.set_param_hint('pFSig', value=params['pfsig'], min=0.001, max=upper_bounds['pfsigUpperBound'], vary=vary['pfsigLock'])

		gmodel.set_param_hint('MDProp', value=params['MechProp'], min=0.001, max=upper_bounds['MechPropUpperBound'], vary=vary['MechPropLock'])
		gmodel.set_param_hint('MDDecay', value=params['MechDecayConst'], min=0.001, max=upper_bounds['MechDecayConstUpperBound'], vary=vary['MechDecayConstLock'])

		pars = gmodel.make_params()

		algorithm = algo_settings[0]
		if algorithm == 'LM':
			# least_squares : the most stable algorithm, it also contains all the features I need
			#  -> Run trust region method for bounded parameters : somehow this one doesn't work for CI
			# result = gmodel.fit(xy, params=params, flatten_generation_list=x,
			#                     method='least_squares',
			#                     fit_kws={'max_nfev': algo_settings[1], 'verbose': 1})
			result = gmodel.fit(
				y,
				params=pars,
				flatten_generation_list=x,
				iter_cb=callback_print_function,
				method='least_squares',
				fit_kws={
					# 'maxfev': algo_settings[1],
					'max_nfev': algo_settings[1],
					'ftol': algo_settings[2],
					'xtol': algo_settings[3],
					'gtol': algo_settings[4],
					# 'jac': '3-point',  # more accurate numerical differentiation scheme
					# 'loss': 'soft_l1'
					# 'full_output': True
				}
			)
		elif algorithm == 'DE':
			result = gmodel.fit(
				y,
				params=pars,
				flatten_generation_list=x,
				iter_cb=callback_print_function,
				method='differential_evolution',
				fit_kws={
					'max_nfev': algo_settings[1],
					'popsize': algo_settings[2],
					'tol': algo_settings[3],
					'atol': algo_settings[4],
					'disp': False
				}
			)

		# leastsq : LM legacy wrapper
		# differential_evolution : division by 0 error. cool stochastic GLOBAL minimizer method
		# brute : raise malloc_error, not working at all
		# nelder :
		# lbfgsb : does not support bounds, odd result -> no std.err report
		# powell : *bounds working, no std.err report
		# cg : does not support bounds
		# newton : needs user-defined Jacobian
		# cobyla : does not support bounds, no std.err report
		# tnc :
		# trust-ncg :
		# dogleg : needs user-defined Jacobian
		# slsqp : needs user-defined Jacobian

		print(result.fit_report())

		gvars.C1_PREV_SS = gvars.C1_SS
		gvars.C1_SS = result.chisqr

		print(" > Cyton 1 Sum of squares:")
		print(" > > prev: {0:.5f}".format(gvars.C1_PREV_SS))
		print(" > > curr: {0:.5f}".format(gvars.C1_SS))

		# end timer
		end = time.time()
		# print elapsed time
		print_elapsed_time(start, end)

		fitted = []
		for key, value in result.best_values.items():
			fitted.append(value)

		print(' > Updating parameters & plots...')

		return fitted

	except Exception as ex:
		# template = "An exception of type {0} occurred. Arguments:\n{1!r}"
		# message = template.format(type(ex).__name__, ex.args)
		# print(message)
		print(' > Updating parameters & plots...')

		# this will return last iteration of failed fit parameters
		return model.last_param[-1]


def fit_to_cyton15(thread, algo_settings, fit_to_total_cells):
	start = time.time()

	print(
		'\n{0:9s}  {1:13} {2:13} {3:13} {4:13} {5:13} {6:13} {7:13} {8:13} {9:13} {10:13} {11:13} {12:13} {13:13} {14:13}'.format(
			'ITER', 'mu0Div', ' sig0Div', ' mu0Death', ' sig0Death', ' muSubDiv', ' sigSubDiv', ' muSubDeath',
			' sigSubDeath', ' pF0', ' pfMu', ' pfSig', 'MDProp', 'MDDecay', 'RSS'))

	# selected condition for fitting
	icnd = gvars.C15_ICND

	# prepare (x, y) data
	# x : generations, y : number of cells per generation per time point
	num_reps = [len(l) for l in gvars.CELL_GENS_REPS[icnd]]
	if not fit_to_total_cells:
		flatten_gens, flatten_cells = [], []
		for itpt in range(len(gvars.EXP_HT[icnd])):
			for irep in range(num_reps[itpt]):
				for igen in range(gvars.MAX_DIV_PER_CONDITIONS[icnd]+1):
					# check for any excluded data
					if gvars.C15_CHECK[icnd][itpt][irep][igen]:
						flatten_gens.append(igen)
						flatten_cells.append(gvars.CELL_GENS_REPS[icnd][itpt][irep][igen])

		# convert flatten_gens(x) & flatten_cells(y) to numpy array
		x = np.array(flatten_gens, dtype=float)
		y = np.array(flatten_cells, dtype=float)
	else:
		x = np.array(gvars.EXP_HT_REPS[icnd])
		y = np.array(gvars.TOTAL_CELLS_REPS[icnd])

	# create Cyton model object -> preparing condition specific variables for fittings
	model = Cyton15Model(
		gvars.EXP_HT[icnd], gvars.INIT_CELL, gvars.MAX_DIV, gvars.TIME_INC, num_reps, gvars.C15_CHECK[icnd], fit_to_total_cells, thread
	)

	# try/except blcok for catching any errors & abort fit
	try:
		# create LMFIT model object -> specify objective function & variables
		gmodel = Model(
			model.cyton15,
			independent_vars=['flatten_generation_list'],
			param_names=[
				'unstimMu', 'unstimSig',
				'stimMuDiv', 'stimSigDiv',
				'stimMuDeath', 'stimSigDeath',
				'stimMuDD', 'stimSigDD',
				'b', 'pF'
			],
			name='Cyton 1.5 Model'
		)

		# 10 parameters to fit :
		#  - unstimulated:
		#     - muDeath, sigDeath
		#  - stimulated:
		#     - muDiv, sigDiv, muDeath, sigDeath, muDD, sigDD
		#  - Misc:
		#     - SubDivTime(b), pFrac
		params = gvars.C15_PARAMS
		upper_bounds = gvars.C15_UPPER_BOUNDS
		vary = gvars.C15_VARY_PARAMS
		gmodel.set_param_hint('unstimMu', value=params['unstimMuDeath'], min=0.001, max=upper_bounds['unstimMuDeathUpperBound'], vary=vary['unstimMuDeathLock'])
		gmodel.set_param_hint('unstimSig', value=params['unstimSigDeath'], min=0.001, max=upper_bounds['unstimSigDeathUpperBound'], vary=vary['unstimSigDeathLock'])
		gmodel.set_param_hint('stimMuDiv', value=params['stimMuDiv'], min=0.001, max=upper_bounds['stimMuDivUpperBound'], vary=vary['stimMuDivLock'])
		gmodel.set_param_hint('stimSigDiv', value=params['stimSigDiv'], min=0.001, max=upper_bounds['stimSigDivUpperBound'], vary=vary['stimSigDivLock'])
		gmodel.set_param_hint('stimMuDeath', value=params['stimMuDeath'], min=0.001, max=upper_bounds['stimMuDeathUpperBound'], vary=vary['stimMuDeathLock'])
		gmodel.set_param_hint('stimSigDeath', value=params['stimSigDeath'], min=0.001, max=upper_bounds['stimSigDeathUpperBound'], vary=vary['stimSigDeathLock'])
		gmodel.set_param_hint('stimMuDD', value=params['stimMuDD'], min=0.001, max=upper_bounds['stimMuDDUpperBound'], vary=vary['stimMuDDLock'])
		gmodel.set_param_hint('stimSigDD', value=params['stimSigDD'], min=0.001, max=upper_bounds['stimSigDDUpperBound'], vary=vary['stimSigDDLock'])

		gmodel.set_param_hint('b', value=params['SubDivTime'], min=0.001, max=upper_bounds['SubDivTimeUpperBound'], vary=vary['SubDivTimeLock'])
		gmodel.set_param_hint('pF', value=params['pfrac'], min=0.0, max=upper_bounds['pfracUpperBound'], vary=vary['pfracLock'])

		# create LMFIT Parameters() object
		pars = gmodel.make_params()

		algorithm = algo_settings[0]
		if algorithm == 'LM':
			# least_squares : the most stable algorithm, it also contains all the features I need
			#  -> Run trust region method for bounded parameters : somehow this one doesn't work for CI

			# 'least_squares' supposedly more robust and properly handled with bounds.
			# Strangely, this method does not utilise full features offered by LMFIT (e.g. error estimates)
			# result = gmodel.fit(
			#   y,
			#   params=params,
			#   flatten_generation_list=x,
			#   method='least_squares',
			#   fit_kws={'max_nfev': algo_settings[1], 'verbose': 1, 'gtol' : algo_settings[4]}
			# )

			# Specifically mentioned that it uses Levenberg-Marquardt algorithm in LMFIT doc.
			# it's an old wrapper (for backward compatibility) for scipy LM algorithm 'leastsq'
			# This supposedly unable to handle bounds itself, but LMFIT upgrade it with their own method to deal with bounds
			result = gmodel.fit(
				y,
				params=pars,
				flatten_generation_list=x,
				iter_cb=callback_print_function,
				method='least_squares',
				fit_kws={
					# 'maxfev': algo_settings[1],
					'max_nfev': algo_settings[1],
					'ftol': algo_settings[2],
					'xtol': algo_settings[3],
					'gtol': algo_settings[4],
					'jac': '3-point',  # more accurate numerical differentiation scheme
					# 'loss': 'soft_l1'
					# 'full_output': True
				}
			)
		elif algorithm == 'DE':
			# More robust methods for exploration but it has high computational cost
			result = gmodel.fit(
				y,
				params=pars,
				flatten_generation_list=x,
				method='differential_evolution',
				iter_cb=callback_print_function,
				fit_kws={
					'max_nfev': algo_settings[1],
					'popsize': algo_settings[2],
					'tol': algo_settings[3],
					'atol': algo_settings[4],
					'seed': 57893928,
					'disp': False
				}
			)

		print(result.fit_report())

		gvars.C15_PREV_SS = gvars.C15_SS
		gvars.C15_SS = result.chisqr

		print(" > Cyton 1.5 Sum of squares:")
		print(" > > prev: {0:.5f}".format(gvars.C15_PREV_SS))
		print(" > > curr: {0:.5f}".format(gvars.C15_SS))

		# end timer
		end = time.time()
		print_elapsed_time(start, end)

		fitted = []
		for key, value in result.best_values.items():
			fitted.append(value)

		print(' > Updating parameters & plots...')
		return fitted

	except Exception as ex:
		# template = "An exception of type {0} occurred. Arguments:\n{1!r}"
		# message = template.format(type(ex).__name__, ex.args)
		# print(message)
		print(' > Updating parameters & plots...')

		# this will return last iteration of failed fit parameters
		return model.last_param[-1]

