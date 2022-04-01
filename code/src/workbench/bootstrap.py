import time
from datetime import datetime
import psutil
import random
import multiprocessing as mp
from contextlib import redirect_stdout
from lmfit import Model

import src.common.global_vars as gvars
from src.workbench.cyton1 import Cyton1Model
from src.workbench.cyton15 import Cyton15Model


# redirect 'print' messages to text file & automatically releases stdout to default
def redirect_msg(text, path):
	with open(path, 'a+') as out:
		with redirect_stdout(out):
			print(text)


def print_elapsed_time(start, end):
	hours, rem = divmod(end - start, 3600)
	minutes, seconds = divmod(rem, 60)

	msg = "Total elapsed time - {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)
	print(" > > " + msg)

	return msg


def resampling(data, num_reps):
	"""
	This function resameples input data with replacement
	input data format (3D list) : Ignoring icnd index because we can directly access current index from global vars
		[ <- itpt
			[ <- irep
				[] <- igen
			]
		]
	:param1 data: (list of lists) multidimensional data
	:param2 num_reps: (list) contains an information about number of replicates per time point
	:returns: (tuple) 1D arrays of resampled data & generation number
	"""
	x, res = [], []
	for itpt in range(len(data)):
		for irep in range(num_reps[itpt]):
			for igen in range(gvars.MAX_DIV+1):
				x.append(igen)
				ridx = random.randint(0, num_reps[itpt]-1)
				res.append(data[itpt][ridx][igen])
	return x, res


def _boots(procnum, sobj, icnd, iters, gmodel, pars, num_reps):
	# temporary local variable storage per parameters
	presults = [
		[], [], [], [], [], [], [], [], [], []
	]
	for i in range(int(iters)):
		print(" > > [proc:{0}] Bootstrap ITER {1}".format(procnum, i+1))

		x, res = resampling(gvars.CELL_GENS_REPS[icnd], num_reps)

		result = gmodel.fit(
			res,
			params=pars,
			flatten_generation_list=x,
			# method='differential_evolution',
			method='leastsq',
			# iter_cb=callback_print_function,
			# fit_kws={
			# 	'max_nfev': 99999,
			# 	'popsize': 30,
			# 	'disp': True
			# }
		)

		# append result to local list per iteration
		j = 0
		for key, val in result.params.valuesdict().items():
			presults[j].append(val)
			j += 1

	sobj[procnum] = presults


# TODO: Extend this method for Cyton 1
def bootstrap(icnd, original, boot_iter, rgs):
	"""
	main bootstrap function - call this function to initiate bootstrap sequence
	this function does not return anything, instead automatically export results

	:param icnd : (int) index of condition in a dataset
	:param original : (list) list of fitted parameters from original dataset
	:param boot_iter : (int) multiples of number of system cores (incl. hyper threads)
	:param alpha : (float) confidence range (e.g. 95% CI => 0.05)
	:return: (tuple) low & high values of the confidence interval
	"""
	num_reps = [len(l) for l in gvars.CELL_GENS_REPS[icnd]]
	alpha = (1 - rgs)/100

	model = Cyton15Model(
		gvars.EXP_HT[icnd], gvars.INIT_CELL, gvars.MAX_DIV, gvars.TIME_INC, num_reps, gvars.C15_CHECK[icnd], False
	)

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
		name='Cyton 1.5 Model (Bootstrap)'
	)

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

	print("\n[{0}] Initiate bootstrapping...".format(datetime.now().replace(microsecond=0)))
	start = time.time()

	# create Manager object for retreiving data from individual core via shared object
	manager = mp.Manager()
	sobj = manager.dict()
	procs = []  # store Process objects to synchronise the results
	nc = int(psutil.cpu_count(logical=False))
	for c in range(nc):
		proc = mp.Process(
			target=_boots,
			args=(c, sobj, icnd, boot_iter/nc, gmodel, pars, num_reps)
		)
		# proc.daemon = True
		procs.append(proc)
	# pool = mp.Pool(processes=nc)
	# iters = []
	# for i in range(nc):
	# 	iters.append(boot_iter/nc)
	# results = [pool.apply_async(_boots, args=(x, sobj, icnd, iters[x], gmodel, pars, num_reps)) for x in range(nc)]
	print(procs)
	# start all Processes
	for p in procs:
		p.start()
	#
	# # wait for all cores to finish the work
	# for p in procs:
	# 	p.join()
	#
	# print(sobj)
	# concatenate results from all cores
	# new = []
	# a, b, c, d, e, f, g, h, i, j = [], [], [], [], [], [], [], [], [], []
	# for core in range(nc):
	# 	a += sobj.values()[core][0]
	# 	b += sobj.values()[core][1]
	# 	c += sobj.values()[core][2]
	# 	d += sobj.values()[core][3]
	# 	e += sobj.values()[core][4]
	# 	f += sobj.values()[core][5]
	# 	g += sobj.values()[core][6]
	# 	h += sobj.values()[core][7]
	# 	i += sobj.values()[core][8]
	# 	j += sobj.values()[core][9]
	#
	# new.append(a)
	# new.append(b)
	# new.append(c)
	# new.append(d)
	# new.append(e)
	# new.append(f)
	# new.append(g)
	# new.append(h)
	# new.append(i)
	# new.append(j)
	#
	# end = time.time()
	# elps = print_elapsed_time(start, end)
	#
	# # print(new)
	# print(elps)
	#
	# low, high = 0, 0
	# return low, high