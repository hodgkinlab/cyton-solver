import numpy as np
cimport numpy as np
np.get_include()
from scipy.stats import lognorm, norm, expon
import src.common.settings as config

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

cimport cython
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
class Cyton15Model:
	def __init__(self, ht, n0, max_div, dt, num_reps, check, fit_to_total_cells, thread=None):
		self.t0 = <DTYPE_t>0.0
		self.tf = <DTYPE_t>(max(ht) + dt)
		self.dt = <DTYPE_t>dt  # time increment : discretisation factor of time

		# declare theoretical time array
		# cdef np.ndarray[DTYPE_t, ndim=1] times = np.zeros(shape=(int(self.tf/self.dt)+1), dtype=DTYPE)
		# cdef np.ndarray[DTYPE_t, ndim=1] semi_inf_time = np.zeros(shape=(int(self.tf/self.dt)+1), dtype=DTYPE)
		self.times = np.arange(self.t0, self.tf, dt, dtype=DTYPE)
		self.semi_inf_time = np.arange(self.t0, 5000, dt, dtype=DTYPE)

		self.n0 = n0  # experiment initial cell number
		self.ht = ht  # experiment harvested times
		self.num_reps = num_reps
		self.check = check  # check matrix for data inclusion/exclusion

		self.exp_max_div = max_div  # experimentally determined maximum division number
		self.max_div = 25  # theoretical maximum division number

		self.iter = 0
		self.thread = thread  # required to abort fit
		self.last_param = []  # an empty list to save parameters at every iteration

		self.fit_to_total_cells = fit_to_total_cells

		self.unstim_death_pdf = config.CYTON15_CONFIG['unstim_die']
		self.stim_div_pdf = config.CYTON15_CONFIG['stim_div']
		self.stim_die_pdf = config.CYTON15_CONFIG['stim_die']
		self.stim_dd_pdf = config.CYTON15_CONFIG['stim_dd']

	# this function only takes care of live cell computation for fittings
	def cyton15(self, flatten_generation_list,
				DTYPE_t unstimMu, DTYPE_t unstimSig,
				DTYPE_t stimMuDiv, DTYPE_t stimSigDiv,
				DTYPE_t stimMuDeath, DTYPE_t stimSigDeath,
				DTYPE_t stimMuDD, DTYPE_t stimSigDD,
				DTYPE_t b, DTYPE_t pF):
		# check for abort signal
		if not self.thread.is_running:
			print(' >>> Abort fitting!')
			raise Exception  # raising any exception to stop
		self.iter += 1

		cdef list params = [
			unstimMu, unstimSig,
			stimMuDiv, stimSigDiv,
			stimMuDeath, stimSigDeath,
			stimMuDD, stimSigDD,
			b, pF
		]
		self.save_last_param(params)

		cdef unsigned int n = self.times.size

		# pre-compute probability distributions
		cdef np.ndarray[DTYPE_t, ndim=1] pdfDiv = np.zeros(shape=n, dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=1] pdfDD = np.zeros(shape=n, dtype=DTYPE)
		pdfDiv = self.compute_pdf(self.times, stimMuDiv, stimSigDiv, pdf_type=self.stim_div_pdf)
		pdfDD = self.compute_pdf(self.times, stimMuDD, stimSigDD, pdf_type=self.stim_dd_pdf)

		# pre-compute cumulative distributions
		cdef np.ndarray[DTYPE_t, ndim=1] cdfUnstim = np.zeros(shape=n, dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=1] cdfDiv = np.zeros(shape=n, dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=1] cdfDie = np.zeros(shape=n, dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=1] cdfDD = np.zeros(shape=n, dtype=DTYPE)
		cdfUnstim = self.compute_cdf(self.times, unstimMu, unstimSig, pdf_type=self.unstim_death_pdf)
		cdfDiv = self.compute_cdf(self.times, stimMuDiv, stimSigDiv, pdf_type=self.stim_div_pdf)
		cdfDie = self.compute_cdf(self.times, stimMuDeath, stimSigDeath, pdf_type=self.stim_die_pdf)
		cdfDD = self.compute_cdf(self.times, stimMuDD, stimSigDD, pdf_type=self.stim_dd_pdf)

		# declare 3 arrays for unstimulated cells, divided cells & destiny cells
		cdef np.ndarray[DTYPE_t, ndim=1] nUnstim = np.zeros(shape=n, dtype=DTYPE)
		nUnstim = self.n0 * (1. - pF) * (1. - cdfUnstim)
		cdef np.ndarray[DTYPE_t, ndim=2] nDIV = np.zeros(shape=(self.max_div+1, n), dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=2] nDD = np.zeros(shape=(self.max_div+1, n), dtype=DTYPE)

		# declare array to store proportion of destiny cells
		cdef np.ndarray[DTYPE_t, ndim=2] DDprop = np.zeros(shape=(self.max_div+1, n), dtype=DTYPE)

		# store number of live cells at all time per generations
		cdef np.ndarray[DTYPE_t, ndim=2] cells_gen = np.zeros(shape=(self.exp_max_div+1, n), dtype=DTYPE)

		# store total live cells
		cdef np.ndarray[DTYPE_t, ndim=1] total_live_cells = np.zeros(shape=n, dtype=DTYPE)

		cdef DTYPE_t t, core
		cdef DTYPE_t top = 0.
		cdef DTYPE_t bottom = 0.
		cdef unsigned int igen, j, l
		for igen in range(self.max_div+1):
			for j, t in enumerate(self.times):
				# nUnstim[j] = self.n0 * (1. - pF) * (1. - cdfUnstim[j])
				core = <DTYPE_t>(2.**igen * self.n0 * pF * (1. - cdfDie[j]))
				if igen == 0:
					# nDIV[igen, j] = core * (1. - cdfDD[j]) * np.sum(pdfDiv[j:]) * self.dt
					nDIV[igen, j] = core * (1. - cdfDD[j]) * (1. - cdfDiv[j])

					if j == 0:
						# DDprop[igen, j] = pdfDD[j] * np.sum(pdfDiv) * self.dt
						DDprop[igen, j] = pdfDD[j] * cdfDiv[n-1]
						nDD[igen, j] = core * DDprop[igen, j] * self.dt
					else:
						# DDprop[igen, j] = pdfDD[j] * np.sum(pdfDiv[j:]) * self.dt + DDprop[igen, j-1]
						DDprop[igen, j] = pdfDD[j] * (1. - cdfDiv[j]) + DDprop[igen, j-1]
						nDD[igen, j] = core * DDprop[igen, j] * self.dt

					cells_gen[igen, j] = nUnstim[j] + nDIV[igen, j] + nDD[igen, j]
					total_live_cells[j] += cells_gen[igen, j]
				else:
					# bottom = <DTYPE_t>(t + b * (igen - 1))
					# top = <DTYPE_t>(t + b * igen)
					# where = np.where((bottom < self.times) & (self.times <= top))
					# l = where[0].size
					# k = (igen - 1) * l
					if j == 0:
						bottom = <DTYPE_t>(t + b * (igen - 1))
						top = <DTYPE_t>(t + b * igen)
						where = np.where((bottom < self.semi_inf_time) & (self.semi_inf_time <= top))
						l = where[0].size
						k = (igen - 1) * l
					else:
						if k < j <= (k+l):
							# nDIV[igen, j] = core * (1. - cdfDD[j]) * np.sum(pdfDiv[:j-k]) * self.dt
							nDIV[igen, j] = core * (1. - cdfDD[j]) * cdfDiv[j-k]

							# DDprop[igen, j] = pdfDD[j] * np.sum(pdfDiv[:j-k]) * self.dt + DDprop[igen, j-1]
							DDprop[igen, j] = pdfDD[j] * cdfDiv[j-k] + DDprop[igen, j-1]
							nDD[igen, j] = core * DDprop[igen, j] * self.dt
						elif j > (k+l):
							# nDIV[igen, j] = core * (1. - cdfDD[j]) * np.sum(pdfDiv[j-k-l:j-k]) * self.dt
							nDIV[igen, j] = core * (1. - cdfDD[j]) * (cdfDiv[j-k] - cdfDiv[j-k-l])

							# DDprop[igen, j] = pdfDD[j] * np.sum(pdfDiv[j-k-l:j-k]) * self.dt + DDprop[igen, j-1]
							DDprop[igen, j] = pdfDD[j] * (cdfDiv[j-k] - cdfDiv[j-k-l]) + DDprop[igen, j-1]
							nDD[igen, j] = core * DDprop[igen, j] * self.dt

						if igen < self.exp_max_div:
							cells_gen[igen, j] = nDIV[igen, j] + nDD[igen, j]
						else:
							cells_gen[self.exp_max_div, j] += nDIV[igen, j] + nDD[igen, j]
					total_live_cells[j] += nDIV[igen, j] + nDD[igen, j]

		# extract number of live cells at harvested time points from 'cells_gen' array
		cdef list model = []
		if not self.fit_to_total_cells:
			for itpt, ht in enumerate(self.ht):
				t_idx = np.where(self.times == ht)
				for irep in range(self.num_reps[itpt]):
					for igen in range(self.exp_max_div+1):
						# check for excluded data
						if self.check[itpt][irep][igen]:
							model.append(cells_gen[igen, t_idx[0][0]])
		else:
			for itpt, ht in enumerate(self.ht):
				t_idx = np.where(self.times == ht)
				for irep in range(self.num_reps[itpt]):
					model.append(total_live_cells[t_idx[0][0]])

		return np.asfarray(model)

	def save_last_param(self, params):
		if self.iter % 50 == 0:
			self.last_param = []
		self.last_param.append(params)
		return self.last_param

	def compute_pdf(self, times, mu, sig, lamb=1, str pdf_type='Lognormal'):
		if pdf_type == 'Lognormal':
			log_mu = np.log(mu)
			return lognorm.pdf(times, sig, scale=np.exp(log_mu))
		elif pdf_type == 'Gaussian':
			return norm.pdf(times, loc=mu, scale=sig)
		elif pdf_type == 'Exponential':
			return expon.pdf(times, scale=1.0/mu)

	def compute_cdf(self, times, mu, sig, lamb=1, str pdf_type='Lognormal'):
		if pdf_type == 'Lognormal':
			log_mu = np.log(mu)
			return lognorm.cdf(times, sig, scale=np.exp(log_mu))
		elif pdf_type == 'Gaussian':
			return norm.cdf(times, loc=mu, scale=sig)
		elif pdf_type == 'Exponential':
			return expon.cdf(times, scale=1.0/mu)

	# following function is a copy of 'cyton15' but with extra dead cell computation
	def compute_model_results(self, model_times, params):
		# unstimulated death parameters
		cdef DTYPE_t muUnstim = params['unstimMuDeath']
		cdef DTYPE_t sigUnstim = params['unstimSigDeath']

		# stimulated cells parameters
		cdef DTYPE_t muDiv = params['stimMuDiv']
		cdef DTYPE_t sigDiv = params['stimSigDiv']
		cdef DTYPE_t muDie = params['stimMuDeath']
		cdef DTYPE_t sigDie = params['stimSigDeath']
		cdef DTYPE_t muDD = params['stimMuDD']
		cdef DTYPE_t sigDD = params['stimSigDD']

		# Subsequent division time & cell fraction parameters
		cdef DTYPE_t b = params['SubDivTime']
		cdef DTYPE_t pF = params['pfrac']

		cdef unsigned int n = model_times.size

		# pre-compute probablity distributions
		cdef np.ndarray[DTYPE_t, ndim=1] pdfDiv = np.zeros(shape=n, dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=1] pdfDie = np.zeros(shape=n, dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=1] pdfDD = np.zeros(shape=n, dtype=DTYPE)
		pdfDiv = self.compute_pdf(model_times, muDiv, sigDiv, pdf_type=self.stim_div_pdf)
		pdfDie = self.compute_pdf(model_times, muDie, sigDie, pdf_type=self.stim_die_pdf)
		pdfDD = self.compute_pdf(model_times, muDD, sigDD, pdf_type=self.stim_dd_pdf)

		# pre-compute cumulative distributions
		cdef np.ndarray[DTYPE_t, ndim=1] cdfUnstim = np.zeros(shape=n, dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=1] cdfDiv = np.zeros(shape=n, dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=1] cdfDie = np.zeros(shape=n, dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=1] cdfDD = np.zeros(shape=n, dtype=DTYPE)
		cdfUnstim = self.compute_cdf(model_times, muUnstim, sigUnstim, pdf_type=self.unstim_death_pdf)
		cdfDiv = self.compute_cdf(model_times, muDiv, sigDiv, pdf_type=self.stim_div_pdf)
		cdfDie = self.compute_cdf(model_times, muDie, sigDie, pdf_type=self.stim_die_pdf)
		cdfDD = self.compute_cdf(model_times, muDD, sigDD, pdf_type=self.stim_dd_pdf)

		"""LIVE CELLS"""
		# declare 3 arrays for unstimulated cells, divided cells & destiny cells
		cdef np.ndarray[DTYPE_t, ndim=1] nUnstim = np.zeros(shape=n, dtype=DTYPE)
		nUnstim = self.n0 * (1. - pF) * (1. - cdfUnstim)
		cdef np.ndarray[DTYPE_t, ndim=2] nDIV = np.zeros(shape=(self.max_div+1, n), dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=2] nDD = np.zeros(shape=(self.max_div+1, n), dtype=DTYPE)

		# declare array to store proportion of destiny cells
		cdef np.ndarray[DTYPE_t, ndim=2] DDprop = np.zeros(shape=(self.max_div+1, n), dtype=DTYPE)

		# store number of cells at all time per generation
		cdef np.ndarray[DTYPE_t, ndim=2] cells_gen = np.zeros(shape=(self.exp_max_div+1, n), dtype=DTYPE)

		# store total live cells
		cdef np.ndarray[DTYPE_t, ndim=1] total_live_cells = np.zeros(shape=n, dtype=DTYPE)

		"""DEAD CELLS"""
		# store unstimulated dead cells
		cdef np.ndarray[DTYPE_t, ndim=1] nDeadUnstim = np.zeros(shape=n, dtype=DTYPE)
		nDeadUnstim = self.n0 * (1. - pF) * cdfUnstim

		# store dead cells from dividing cells
		cdef np.ndarray[DTYPE_t, ndim=2] nDeadDIV = np.zeros(shape=(self.max_div+1, n), dtype=DTYPE)

		# store dead cells from destiny cells
		cdef np.ndarray[DTYPE_t, ndim=2] nDeadDD = np.zeros(shape=(self.max_div+1, n), dtype=DTYPE)

		# store dead cells at all time per generation
		cdef np.ndarray[DTYPE_t, ndim=2] dead_cells_gen = np.zeros(shape=(self.exp_max_div+1, n), dtype=DTYPE)

		# store total dead cells
		cdef np.ndarray[DTYPE_t, ndim=1] total_dead_cells = np.zeros(shape=n, dtype=DTYPE)

		cdef DTYPE_t t, core, core_dead
		cdef DTYPE_t top = 0.
		cdef DTYPE_t bottom = 0.
		cdef unsigned int igen, j, l
		for igen in range(self.max_div+1):
			for j, t in enumerate(model_times):
				core = <DTYPE_t>(2.**igen * self.n0 * pF * (1. - cdfDie[j]))
				core_dead = <DTYPE_t>(2.**igen * self.n0 * pF * cdfDie[j])
				if igen == 0:
					# compute live & dead dividing cells
					# nDIV[igen, j] = core * (1. - cdfDD[j]) * np.sum(pdfDiv[j:]) * self.dt
					nDIV[igen, j] = core * (1. - cdfDD[j]) * (1. - cdfDiv[j])
					# nDeadDIV[igen, j] = core_dead * (1. - cdfDD[j]) * (1. - cdfDiv[j])  # this method doesn't know if there's any live cells left to die. so perhaps wrong method.

					# compute proportion of destiny cells
					if j == 0:
						nDeadDIV[igen, j] = 2. * nDIV[igen, j] * pdfDie[j] * self.dt

						# DDprop[igen, j] = pdfDD[j] * np.sum(pdfDiv) * self.dt
						DDprop[igen, j] = pdfDD[j] * cdfDiv[n-1]
						nDD[igen, j] = core * DDprop[igen, j] * self.dt
						nDeadDD[igen, j] = 2. * nDD[igen, j] * pdfDie[j] * self.dt
					else:
						nDeadDIV[igen, j] = 2. * nDIV[igen, j] * pdfDie[j] * self.dt + nDeadDIV[igen, j-1]

						# DDprop[igen, j] = pdfDD[j] * np.sum(pdfDiv[j:]) * self.dt + DDprop[igen, j-1]
						DDprop[igen, j] = pdfDD[j] * (1. - cdfDiv[j]) + DDprop[igen, j-1]
						nDD[igen, j] = core * DDprop[igen, j] * self.dt
						nDeadDD[igen, j] = 2. * nDD[igen, j] * pdfDie[j] * self.dt + nDeadDD[igen, j-1]

					# compute live & dead destiny cells - this method doesn't know if there's any live cells left to die. so perhaps wrong method.
					# nDD[igen, j] = core * DDprop[igen, j] * self.dt
					# nDeadDD[igen, j] = core_dead * DDprop[igen, j] * self.dt
					# nDeadDD[igen, j] = 2. * nDD[igen, j] * pdfDie[j] * self.dt + nDeadDD[igen, j-1]

					# compute total live cells
					cells_gen[igen, j] = nUnstim[j] + nDIV[igen, j] + nDD[igen, j]
					total_live_cells[j] += cells_gen[igen, j]

					# compute total dead cells
					dead_cells_gen[igen, j] = nDeadUnstim[j] + nDeadDIV[igen, j] + nDeadDD[igen, j]
					total_dead_cells[j] += dead_cells_gen[igen, j]
				else:
					# bottom = <DTYPE_t>(t + b * (igen - 1))
					# top = <DTYPE_t>(t + b * igen)
					# where = np.where((bottom < times) & (times <= top))
					# l = where[0].size
					# k = (igen - 1) * l
					if j == 0:
						bottom = <DTYPE_t>(t + b * (igen - 1))
						top = <DTYPE_t>(t + b * igen)
						where = np.where((bottom < self.semi_inf_time) & (self.semi_inf_time <= top))
						l = where[0].size
						k = (igen - 1) * l
					else:
						if k < j <= (k+l):
							# nDIV[igen, j] = core * (1. - cdfDD[j]) * np.sum(pdfDiv[:j-k]) * self.dt
							nDIV[igen, j] = core * (1. - cdfDD[j]) * cdfDiv[j-k]
							# nDeadDIV[igen, j] = core_dead * (1. - cdfDD[j]) * cdfDiv[j-k]  # this method doesn't know if there's any live cells left to die. so perhaps wrong method.

							# DDprop[igen, j] = pdfDD[j] * np.sum(pdfDiv[:j-k]) * self.dt + DDprop[igen, j-1]
							DDprop[igen, j] = pdfDD[j] * cdfDiv[j-k] + DDprop[igen, j-1]
							nDD[igen, j] = core * DDprop[igen, j] * self.dt
							# nDeadDD[igen, j] = core_dead * DDprop[igen, j] * self.dt
						elif j > (k+l):
							# nDIV[igen, j] = core * (1. - cdfDD[j]) * np.sum(pdfDiv[j-k-l:j-k]) * self.dt
							nDIV[igen, j] = core * (1. - cdfDD[j]) * (cdfDiv[j-k] - cdfDiv[j-k-l])
							# nDeadDIV[igen, j] = core_dead * (1. - cdfDD[j]) * (cdfDiv[j-k] - cdfDiv[j-k-l])  # this method doesn't know if there's any live cells left to die. so perhaps wrong method.

							# DDprop[igen, j] = pdfDD[j] * np.sum(pdfDiv[j-k-l:j-k]) * self.dt + DDprop[igen, j-1]
							DDprop[igen, j] = pdfDD[j] * (cdfDiv[j-k] - cdfDiv[j-k-l]) + DDprop[igen, j-1]
							nDD[igen, j] = core * DDprop[igen, j] * self.dt
							# nDeadDD[igen, j] = core_dead * DDprop[igen, j] * self.dt

						nDeadDIV[igen, j] = 2. * nDIV[igen, j] * pdfDie[j] * self.dt + nDeadDIV[igen, j-1]
						nDeadDD[igen, j] = 2. * nDD[igen, j] * pdfDie[j] * self.dt + nDeadDD[igen, j-1]

					if igen < self.exp_max_div:
						cells_gen[igen, j] = nDIV[igen, j] + nDD[igen, j]
						dead_cells_gen[igen, j] = nDeadDIV[igen, j] + nDeadDD[igen, j]
					else:
						cells_gen[self.exp_max_div, j] += nDIV[igen, j] + nDD[igen, j]
						dead_cells_gen[self.exp_max_div, j] += nDeadDIV[igen, j] + nDeadDD[igen, j]
					total_live_cells[j] += nDIV[igen, j] + nDD[igen, j]
					total_dead_cells[j] += nDeadDIV[igen, j] + nDeadDD[igen, j]

		cdef unsigned int itpt
		cdef list cells_gen_at_ht = [[] for _ in range(len(self.ht))]
		cdef list dead_cells_gen_at_ht = [[] for _ in range(len(self.ht))]
		cdef np.ndarray[DTYPE_t, ndim=1] total_live_cells_at_ht = np.zeros(shape=(len(self.ht)), dtype=DTYPE)
		for itpt, ht in enumerate(self.ht):
			t_idx = np.where(model_times == ht)
			for igen in range(self.exp_max_div+1):
				cells_gen_at_ht[itpt].append(cells_gen[igen, t_idx[0][0]])
				dead_cells_gen_at_ht[itpt].append(dead_cells_gen[igen, t_idx[0][0]])
			total_live_cells_at_ht[itpt] = total_live_cells[t_idx[0][0]]

		# collect theoretical components
		live_stuffs = [total_live_cells, cells_gen, nDIV, nDD, nUnstim]
		dead_stuffs = [total_dead_cells, dead_cells_gen, nDeadDIV, nDeadDD, nDeadUnstim]

		# collect experimentally relevant components
		exp_rel = [total_live_cells_at_ht, cells_gen_at_ht, dead_cells_gen_at_ht]

		return exp_rel, live_stuffs, dead_stuffs





