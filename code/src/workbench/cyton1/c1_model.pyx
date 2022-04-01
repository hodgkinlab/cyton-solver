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
class Cyton1Model:
	def __init__(self, ht, n0, max_div, dt, num_reps, check, thread=None):
		self.t0 = 0.0
		self.tf = max(ht)
		self.dt = dt
		self.initCellNo = n0
		self.harvestTimes = ht
		self.maxDivisions = max_div
		self.num_replicates = num_reps
		self.check = check

		# Default mechanical death parameter values
		self.mechanicalDeathProportion = <DTYPE_t>0.0
		self.mechanicalDeathConstant = <DTYPE_t>0.5

		self.thread = thread

		self.iter = 0
		self.last_param = []

		self.first_div_pdf = config.CYTON1_CONFIG['first_div']
		self.first_die_pdf = config.CYTON1_CONFIG['first_die']
		self.subsq_div_pdf = config.CYTON1_CONFIG['subsq_div']
		self.subsq_die_pdf = config.CYTON1_CONFIG['subsq_die']

	# TODO: OVERALL BAD PROGRAMMING! FIX IT (if you care)!
	def cyton1_model(self, flatten_generation_list,
					 DTYPE_t mu0Div, DTYPE_t sig0Div,
					 DTYPE_t mu0Death, DTYPE_t sig0Death,
					 DTYPE_t muSubDiv, DTYPE_t sigSubDiv,
					 DTYPE_t muSubDeath, DTYPE_t sigSubDeath,
					 DTYPE_t pF0, DTYPE_t pFMu, DTYPE_t pFSig,
					 DTYPE_t MDProp, DTYPE_t MDDecay):
		# check if user clicked 'Abort Fit' button
		if not self.thread.is_running:
			print(' >>> Abort fitting!')
			raise Exception
		self.iter += 1

		cdef list params = [
			mu0Div, sig0Div,
			mu0Death, sig0Death,
			muSubDiv, sigSubDiv,
			muSubDeath, sigSubDeath,
			pF0, pFMu, pFSig,
			MDProp, MDDecay
		]
		self.save_last_param(params)

		# create times array
		cdef unsigned int l = 0
		cdef DTYPE_t t1
		cdef np.ndarray[DTYPE_t, ndim=1] times = np.zeros(int(self.tf/self.dt), dtype=DTYPE)
		t1 = self.t0 + self.dt
		while t1 <= self.tf:
			times[l] = t1
			t1 += self.dt
			l += 1

		cdef unsigned int n = times.size

		# create times array with 0
		cdef DTYPE_t t2
		cdef np.ndarray[DTYPE_t, ndim=1] timesWith0 = np.zeros(n+1, dtype=DTYPE)
		t2 = self.t0
		l = 0
		while t2 <= self.tf:
			timesWith0[l] = t2
			t2 += self.dt
			l += 1

		# first division : PDF parameters
		cdef DTYPE_t mu0div, sig0div
		cdef DTYPE_t mudie, sig0die
		mu0div, sig0div = mu0Div, sig0Div
		mu0die, sig0die = mu0Death, sig0Death

		# subsequent division : PDF parameters
		cdef DTYPE_t muSdiv, sigSdiv
		cdef DTYPE_t muSdie, sigSdie
		muSdiv, sigSdiv = muSubDiv, sigSubDiv
		muSdie, sigSdie = muSubDeath, sigSubDeath

		# progress fraction calculation as a parameter
		cdef DTYPE_t pf0, pfMu, pfSig
		pf0 = pF0
		pfMu = pFMu
		pfSig = pFSig
		cdef np.ndarray[DTYPE_t, ndim=1] pF = np.zeros(self.maxDivisions+1, dtype=DTYPE)
		pF[0] = pf0

		cdef unsigned int i, j, k
		cdef DTYPE_t numer
		cdef DTYPE_t denom
		for i in range(1, self.maxDivisions+1):
			numer = <DTYPE_t>1.0 - norm.cdf(i, loc=pfMu, scale=pfSig)
			denom = <DTYPE_t>1.0 - norm.cdf(<unsigned int>(i-1), loc=pfMu, scale=pfSig)
			if denom > <DTYPE_t>0.0:
				pF[i] = numer/denom
			else:
				pF[i] = 0.0

		# compute PDFs
		cdef np.ndarray[DTYPE_t, ndim=1] pdfDiv0 = np.zeros(n, dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=1] pdfDeath0 = np.zeros(n, dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=1] pdfDivSubseq = np.zeros(n, dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=1] pdfDeathSubseq = np.zeros(n, dtype=DTYPE)
		pdfDiv0 = self.compute_pdf(times, mu0div, sig0div, pdfType=self.first_div_pdf)
		pdfDeath0 = self.compute_pdf(times, mu0die, sig0die, pdfType=self.first_die_pdf)
		pdfDivSubseq = self.compute_pdf(times, muSdiv, sigSdiv, pdfType=self.subsq_div_pdf)
		pdfDeathSubseq = self.compute_pdf(times, muSdie, sigSdie, pdfType=self.subsq_die_pdf)

		cdef np.ndarray[DTYPE_t, ndim=1] cumPdfDiv0 = np.zeros(n, dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=1] cumPdfDeath0 = np.zeros(n, dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=1] cumPdfDivSubseq = np.zeros(n, dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=1] cumPdfDeathSubseq = np.zeros(n, dtype=DTYPE)
		cumPdfDiv0 = self.compute_cdf(times, mu0div, sig0div, pdfType=self.first_div_pdf)
		cumPdfDeath0 = self.compute_cdf(times, mu0die, sig0die, pdfType=self.first_die_pdf)
		cumPdfDivSubseq = self.compute_cdf(times, muSdiv, sigSdiv, pdfType=self.subsq_div_pdf)
		cumPdfDeathSubseq = self.compute_cdf(times, muSdie, sigSdie, pdfType=self.subsq_die_pdf)

		self.mechanicalDeathProportion = MDProp
		self.mechanicalDeathConstant = MDDecay
		cdef np.ndarray[DTYPE_t, ndim=1] pdfMechDeath = np.zeros(n, dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=1] cumPdfMechDeath = np.zeros(n, dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=1] mechDeathDecay = np.zeros(n, dtype=DTYPE)
		pdfMechDeath = self.compute_pdf(times, 0, 0, pdfType='Exponential')
		cumPdfMechDeath = self.compute_cdf(times, 0, 0, pdfType='Exponential')
		mechDeathDecay = self.calcMechanicalDeathDecay(timesWith0)

		# compute generation-0 live & dead cells
		cdef np.ndarray[DTYPE_t, ndim=2] divMatrix = np.zeros(shape=(self.maxDivisions+1, n), dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=2] deathMatrix = np.zeros(shape=(self.maxDivisions+1, n), dtype=DTYPE)
		cdef DTYPE_t checkSmall = <DTYPE_t>0.0
		cdef DTYPE_t checkSmall2 = <DTYPE_t>0.0
		for i in range(n):
			checkSmall = <DTYPE_t>self.initCellNo * pF[0] * pdfDiv0[i] * (<DTYPE_t>1.0 - <DTYPE_t>self.mechanicalDeathProportion * cumPdfMechDeath[<unsigned int>(i+1)] - (<DTYPE_t>1.0 - <DTYPE_t>self.mechanicalDeathProportion) * cumPdfDeath0[<unsigned int>(i+1)])
			if checkSmall < 1E-15:
				checkSmall = <DTYPE_t>0.0
			divMatrix[0, i] = checkSmall

			checkSmall2 = self.initCellNo * ( (<DTYPE_t>1.0 - <DTYPE_t>self.mechanicalDeathProportion) * pdfDeath0[i] + <DTYPE_t>self.mechanicalDeathProportion * pdfMechDeath[i] ) * (<DTYPE_t>1.0 - pF[0] * cumPdfDiv0[i])
			if checkSmall2 < 1E-15:
				checkSmall2 = <DTYPE_t>0.0
			deathMatrix[0, i] = checkSmall2

		# compute subsequent generation live & dead cells
		cdef np.ndarray[DTYPE_t, ndim=2] wosmatrixDiv = np.zeros(shape=(n, n), dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=2] wosmatrixDeath = np.zeros(shape=(n, n), dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=2] displacedMatrixDiv = np.zeros(shape=(n, n*2), dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=2] displacedMatrixDeath = np.zeros(shape=(n, n*2), dtype=DTYPE)
		cdef DTYPE_t sumLIVE
		cdef DTYPE_t sumDEAD
		cdef np.ndarray[DTYPE_t, ndim=1] sumArryLIVE = np.zeros(shape=(n), dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=1] sumArryDEAD = np.zeros(shape=(n), dtype=DTYPE)
		for i in range(1, len(divMatrix)):

			# calculate 'wosmatrix'
			for j in range(len(wosmatrixDiv)):
				for k in range(len(wosmatrixDiv[0])):
					checkSmall = <DTYPE_t>2.0 * divMatrix[<unsigned int>(i-1), j] * pF[i] * pdfDivSubseq[k] * (<DTYPE_t>1.0 - cumPdfDeathSubseq[<unsigned int>(k+1)])
					if checkSmall < 1E-15:
						checkSmall = <DTYPE_t>0.0
					wosmatrixDiv[j, k] = checkSmall

					checkSmall2 = <DTYPE_t>2.0 * divMatrix[<unsigned int>(i-1), j] * (<DTYPE_t>1.0 - pF[i]) * pdfDeathSubseq[k] + <DTYPE_t>2.0 * divMatrix[<unsigned int>(i-1), j] * pF[i] * pdfDeathSubseq[k] * (<DTYPE_t>1.0 - cumPdfDivSubseq[k])
					if checkSmall2 < 1E-15:
						checkSmall2 = <DTYPE_t>0.0
					wosmatrixDeath[j, k] = checkSmall2

			# displace 'wosmatrix'
			for j in range(len(wosmatrixDiv)):
				for k in range(len(wosmatrixDiv[0])):
					displacedMatrixDiv[j, <unsigned int>(k+j)] = wosmatrixDiv[j, k]
					displacedMatrixDeath[j, <unsigned int>(k+j)] = wosmatrixDeath[j, k]

			# sum vertically
			for j in range(len(wosmatrixDiv[0])):
				sumLIVE = <DTYPE_t>0.0
				sumDEAD = <DTYPE_t>0.0
				for k in range(len(wosmatrixDiv)):
					sumLIVE += displacedMatrixDiv[k, j]
					sumDEAD += displacedMatrixDeath[k, j]
				sumArryLIVE[j] = sumLIVE
				sumArryDEAD[j] = sumDEAD

			divMatrix[i] = sumArryLIVE
			deathMatrix[i] = sumArryDEAD

		cdef np.ndarray[DTYPE_t, ndim=2] LiveMatrix = np.zeros(shape=(self.maxDivisions+1, n+1), dtype=DTYPE)
		LiveMatrix[0, 0] = <DTYPE_t>self.initCellNo
		for i in range(self.maxDivisions+1):
			for j in range(1, len(LiveMatrix[0])):
				if i == 0:
					LiveMatrix[0, j] = LiveMatrix[0, <unsigned int>(j-1)] - divMatrix[0, <unsigned int>(j-1)] - deathMatrix[0, <unsigned int>(j-1)]
				else:
					LiveMatrix[i, j] = LiveMatrix[i, <unsigned int>(j-1)] + <DTYPE_t>2.0*divMatrix[<unsigned int>(i-1), <unsigned int>(j-1)] - deathMatrix[i, <unsigned int>(j-1)] - divMatrix[i, <unsigned int>(j-1)]

		cdef list model = []
		cdef unsigned int tIDX
		cdef int igen
		cdef DTYPE_t real_time
		cdef DTYPE_t theoretical_time
		for tIDX, theoretical_time in enumerate(timesWith0):
			for itpt, real_time in enumerate(self.harvestTimes):
				if real_time == theoretical_time:
					for irep in range(self.num_replicates[itpt]):
						for igen in range(0, self.maxDivisions+1):
							# check for excluded data
							if self.check[itpt][irep][igen]:
								model.append(LiveMatrix[igen, tIDX])

		return np.asfarray(model)

	def save_last_param(self, params):
		if self.iter % 50 == 0:
			self.last_param = []
		self.last_param.append(params)
		return self.last_param

	def compute_pdf(self, times, DTYPE_t mu, DTYPE_t sig, str pdfType='Lognormal'):
		cdef unsigned int i
		cdef DTYPE_t time
		cdef DTYPE_t val
		cdef np.ndarray[DTYPE_t, ndim=1] cdf = np.zeros(len(times)+1, dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=1] pdf = np.zeros(len(times)+1, dtype=DTYPE)
		if pdfType == 'Lognormal':
			log_mu = np.log(mu)
			for i, time in enumerate(times):
				val = lognorm.cdf(time, sig, scale=np.exp(log_mu))
				if val < 1E-15:
					val = <DTYPE_t>0.0
				cdf[i+1] = val
				pdf[i] = cdf[i+1] - cdf[i]
		elif pdfType == 'Gaussian':
			for i, time in enumerate(times):
				val = norm.cdf(time, loc=mu, scale=sig)
				if val < 1E-15:
					val = <DTYPE_t>0.0
				cdf[i+1] = val
				pdf[i] = cdf[i+1] - cdf[i]
		elif pdfType == 'Exponential':
			cdf[0] = expon.cdf(0.0, scale=1.0/self.mechanicalDeathConstant)
			for i, time in enumerate(times):
				val = expon.cdf(time, scale=1.0/self.mechanicalDeathConstant)
				if val < 1E-15:
					val = <DTYPE_t>0.0
				cdf[i+1] = val
				pdf[i] = cdf[i+1] - cdf[i]
		return pdf

	def compute_cdf(self, times, DTYPE_t mu, DTYPE_t sig, str pdfType='Lognormal'):
		cdef unsigned int i
		cdef DTYPE_t t
		cdef DTYPE_t val
		cdef list timesBiggerBy1 = []
		t = self.t0 + self.dt
		while t <= self.tf + self.dt:
			timesBiggerBy1.append(t)
			t += self.dt

		cdef np.ndarray[DTYPE_t, ndim=1] cdf = np.zeros(len(times)+1, dtype=DTYPE)
		if pdfType == 'Lognormal':
			log_mu = np.log(mu)
			for i in range(len(timesBiggerBy1)-1):
				val = lognorm.cdf(timesBiggerBy1[i], sig, scale=np.exp(log_mu))
				if val < 1E-15:
					val = <DTYPE_t>0.0
				cdf[i+1] = val
		elif pdfType == 'Gaussian':
			for i in range(len(timesBiggerBy1)-1):
				val = norm.cdf(timesBiggerBy1[i], loc=mu, scale=sig)
				if val < 1E-15:
					val = <DTYPE_t>0.0
				cdf[i+1] = val
		elif pdfType == 'Exponential':
			for i in range(len(timesBiggerBy1)-1):
				val = expon.cdf(timesBiggerBy1[i], scale=1.0/self.mechanicalDeathConstant)
				if val < 1E-15:
					val = <DTYPE_t>0.0
				cdf[i+1] = val
		return cdf

	def calcMechanicalDeathDecay(self, times):
		cdef unsigned int i
		cdef DTYPE_t time
		cdef DTYPE_t mdk
		cdef DTYPE_t val
		cdef np.ndarray[DTYPE_t, ndim=1] mechDeathDecay = np.zeros(len(times), dtype=DTYPE)

		mdk = self.mechanicalDeathConstant
		for i, time in enumerate(times):
			val = <DTYPE_t>np.exp(- mdk * time)
			if val < 1E-15:
				val = <DTYPE_t>0.0
			mechDeathDecay[i] = val
		return mechDeathDecay

	# this is just a duplicate from above but to return different values for plotting
	def compute_model_results(self, TIMES, PARAMS):
		self.tf = max(TIMES)

		# create times array
		cdef unsigned int l = 0
		cdef DTYPE_t t1
		cdef np.ndarray[DTYPE_t, ndim=1] times = np.zeros(int(self.tf/self.dt), dtype=DTYPE)
		t1 = self.t0 + self.dt
		while t1 <= self.tf:
			times[l] = t1
			t1 += self.dt
			l += 1

		cdef unsigned int n = times.size

		# create times array with 0
		cdef DTYPE_t t2
		cdef np.ndarray[DTYPE_t, ndim=1] timesWith0 = np.zeros(n+1, dtype=DTYPE)
		t2 = self.t0
		l = 0
		while t2 <= self.tf:
			timesWith0[l] = t2
			t2 += self.dt
			l += 1

		# first division : PDF parameters
		cdef DTYPE_t mu0div, sig0div
		cdef DTYPE_t mudie, sig0die
		mu0div, sig0div = PARAMS['mu0div'], PARAMS['sig0div']
		mu0die, sig0die = PARAMS['mu0death'], PARAMS['sig0death']

		# subsequent division : PDF parameters
		cdef DTYPE_t muSdiv, sigSdiv
		cdef DTYPE_t muSdie, sigSdie
		muSdiv, sigSdiv = PARAMS['muSubdiv'], PARAMS['sigSubdiv']
		muSdie, sigSdie = PARAMS['muSubdeath'], PARAMS['sigSubdeath']

		# progress fraction calculation as a parameter
		cdef DTYPE_t pf0, pfMu, pfSig
		pf0 = PARAMS['pf0']
		pfMu = PARAMS['pfmu']
		pfSig = PARAMS['pfsig']
		cdef np.ndarray[DTYPE_t, ndim=1] pF = np.zeros(self.maxDivisions+1, dtype=DTYPE)
		pF[0] = pf0

		cdef unsigned int i, j, k
		cdef DTYPE_t numer
		cdef DTYPE_t denom
		for i in range(1, self.maxDivisions+1):
			numer = <DTYPE_t>1.0 - norm.cdf(i, loc=pfMu, scale=pfSig)
			denom = <DTYPE_t>1.0 - norm.cdf(<unsigned int>(i-1), loc=pfMu, scale=pfSig)
			if denom > <DTYPE_t>0.0:
				pF[i] = numer/denom
			else:
				pF[i] = 0.0

		# compute PDFs
		cdef np.ndarray[DTYPE_t, ndim=1] pdfDiv0 = np.zeros(n, dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=1] pdfDeath0 = np.zeros(n, dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=1] pdfDivSubseq = np.zeros(n, dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=1] pdfDeathSubseq = np.zeros(n, dtype=DTYPE)
		pdfDiv0 = self.compute_pdf(times, mu0div, sig0div, pdfType=self.first_div_pdf)
		pdfDeath0 = self.compute_pdf(times, mu0die, sig0die, pdfType=self.first_die_pdf)
		pdfDivSubseq = self.compute_pdf(times, muSdiv, sigSdiv, pdfType=self.subsq_div_pdf)
		pdfDeathSubseq = self.compute_pdf(times, muSdie, sigSdie, pdfType=self.subsq_die_pdf)

		cdef np.ndarray[DTYPE_t, ndim=1] cumPdfDiv0 = np.zeros(n, dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=1] cumPdfDeath0 = np.zeros(n, dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=1] cumPdfDivSubseq = np.zeros(n, dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=1] cumPdfDeathSubseq = np.zeros(n, dtype=DTYPE)
		cumPdfDiv0 = self.compute_cdf(times, mu0div, sig0div, pdfType=self.first_div_pdf)
		cumPdfDeath0 = self.compute_cdf(times, mu0die, sig0die, pdfType=self.first_die_pdf)
		cumPdfDivSubseq = self.compute_cdf(times, muSdiv, sigSdiv, pdfType=self.subsq_div_pdf)
		cumPdfDeathSubseq = self.compute_cdf(times, muSdie, sigSdie, pdfType=self.subsq_die_pdf)

		self.mechanicalDeathProportion = PARAMS['MechProp']
		self.mechanicalDeathConstant = PARAMS['MechDecayConst']
		cdef np.ndarray[DTYPE_t, ndim=1] pdfMechDeath = np.zeros(n, dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=1] cumPdfMechDeath = np.zeros(n, dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=1] mechDeathDecay = np.zeros(n, dtype=DTYPE)
		pdfMechDeath = self.compute_pdf(times, 0, 0, pdfType='Exponential')
		cumPdfMechDeath = self.compute_cdf(times, 0, 0, pdfType='Exponential')
		mechDeathDecay = self.calcMechanicalDeathDecay(timesWith0)

		# compute generation-0 live & dead cells
		cdef np.ndarray[DTYPE_t, ndim=2] divMatrix = np.zeros(shape=(self.maxDivisions+1, n), dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=2] deathMatrix = np.zeros(shape=(self.maxDivisions+1, n), dtype=DTYPE)
		cdef DTYPE_t checkSmall = <DTYPE_t>0.0
		cdef DTYPE_t checkSmall2 = <DTYPE_t>0.0
		for i in range(n):
			checkSmall = <DTYPE_t>self.initCellNo * pF[0] * pdfDiv0[i] * (<DTYPE_t>1.0 - <DTYPE_t>self.mechanicalDeathProportion * cumPdfMechDeath[<unsigned int>(i+1)] - (<DTYPE_t>1.0 - <DTYPE_t>self.mechanicalDeathProportion) * cumPdfDeath0[<unsigned int>(i+1)])
			if checkSmall < 1E-15:
				checkSmall = <DTYPE_t>0.0
			divMatrix[0, i] = checkSmall

			checkSmall2 = <DTYPE_t>self.initCellNo * ( (<DTYPE_t>1.0 - <DTYPE_t>self.mechanicalDeathProportion) * pdfDeath0[i] + <DTYPE_t>self.mechanicalDeathProportion * pdfMechDeath[i] ) * (<DTYPE_t>1.0 - pF[0] * cumPdfDiv0[i])
			if checkSmall2 < 1E-15:
				checkSmall2 = <DTYPE_t>0.0
			deathMatrix[0, i] = checkSmall2

		# compute subsequent generation live & dead cells
		cdef np.ndarray[DTYPE_t, ndim=2] wosmatrixDiv = np.zeros(shape=(n, n), dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=2] wosmatrixDeath = np.zeros(shape=(n, n), dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=2] displacedMatrixDiv = np.zeros(shape=(n, n*2), dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=2] displacedMatrixDeath = np.zeros(shape=(n, n*2), dtype=DTYPE)
		cdef DTYPE_t sumLIVE
		cdef DTYPE_t sumDEAD
		cdef np.ndarray[DTYPE_t, ndim=1] sumArryLIVE = np.zeros(shape=n, dtype=DTYPE)
		cdef np.ndarray[DTYPE_t, ndim=1] sumArryDEAD = np.zeros(shape=n, dtype=DTYPE)
		for i in range(1, len(divMatrix)):

			# calculate 'wosmatrix'
			for j in range(len(wosmatrixDiv)):
				for k in range(len(wosmatrixDiv[0])):
					checkSmall = <DTYPE_t>2.0 * divMatrix[<unsigned int>(i-1), j] * pF[i] * pdfDivSubseq[k] * (<DTYPE_t>1.0 - cumPdfDeathSubseq[<unsigned int>(k+1)])
					# if checkSmall < 1E-15:
					#     checkSmall = <DTYPE_t>0.0
					wosmatrixDiv[j, k] = checkSmall

					checkSmall2 = <DTYPE_t>2.0 * divMatrix[<unsigned int>(i-1), j] * (<DTYPE_t>1.0 - pF[i]) * pdfDeathSubseq[k] + <DTYPE_t>2.0 * divMatrix[<unsigned int>(i-1), j] * pF[i] * pdfDeathSubseq[k] * (<DTYPE_t>1.0 - cumPdfDivSubseq[k])
					# if checkSmall2 < 1E-15:
					#     checkSmall2 = <DTYPE_t>0.0
					wosmatrixDeath[j, k] = checkSmall2

			# displace 'wosmatrix'
			for j in range(len(wosmatrixDiv)):
				for k in range(len(wosmatrixDiv[0])):
					displacedMatrixDiv[j, <unsigned int>(k+j)] = wosmatrixDiv[j, k]
					displacedMatrixDeath[j, <unsigned int>(k+j)] = wosmatrixDeath[j, k]

			# sum vertically
			for j in range(len(wosmatrixDiv[0])):
				sumLIVE = <DTYPE_t>0.0
				sumDEAD = <DTYPE_t>0.0
				for k in range(len(wosmatrixDiv)):
					sumLIVE += displacedMatrixDiv[k, j]
					sumDEAD += displacedMatrixDeath[k, j]
				sumArryLIVE[j] = sumLIVE
				sumArryDEAD[j] = sumDEAD

			divMatrix[i] = sumArryLIVE
			deathMatrix[i] = sumArryDEAD

		cdef np.ndarray[DTYPE_t, ndim=2] LiveMatrix = np.zeros(shape=(self.maxDivisions+1, n+1), dtype=DTYPE)
		LiveMatrix[0, 0] = <DTYPE_t>self.initCellNo
		for i in range(0, len(LiveMatrix)):
			for j in range(1, len(LiveMatrix[0])):
				if i == 0:
					LiveMatrix[i, j] = LiveMatrix[i, <unsigned int>(j-1)] - divMatrix[i, <unsigned int>(j-1)] - deathMatrix[i, <unsigned int>(j-1)]
				else:
					LiveMatrix[i, j] = LiveMatrix[i, <unsigned int>(j-1)] + <DTYPE_t>2.0*divMatrix[<unsigned int>(i-1), <unsigned int>(j-1)] - deathMatrix[i, <unsigned int>(j-1)] - divMatrix[i, <unsigned int>(j-1)]
		# for j in range(1, len(LiveMatrix[0])):
		# 	LiveMatrix[0, j] = LiveMatrix[0, <unsigned int>(j-1)] - divMatrix[0, <unsigned int>(j-1)] - deathMatrix[0, <unsigned int>(j-1)]
		# for i in range(1, len(LiveMatrix)):
		# 	for j in range(1, len(LiveMatrix[0])):
		# 		LiveMatrix[i, j] = LiveMatrix[i, <unsigned int>(j-1)] + <DTYPE_t>2.0*divMatrix[<unsigned int>(i-1), <unsigned int>(j-1)] - deathMatrix[i, <unsigned int>(j-1)] - divMatrix[i, <unsigned int>(j-1)]

		# compute total cells at every time points (sum over divisions)
		cdef np.ndarray[DTYPE_t, ndim=1] TotalLiveCell = np.zeros(shape=(len(LiveMatrix[0])), dtype=DTYPE)
		# cdef np.ndarray[DTYPE_t, ndim=1] TotalDeadCell = np.zeros(shape=(len(cumDeadCell[0])), dtype=DTYPE)
		for i in range(len(LiveMatrix[0])):
			for j in range(len(LiveMatrix)):
				TotalLiveCell[i] += LiveMatrix[j, i]
				# TotalDeadCell[i] += cumDeadCell[j, i]

		cdef unsigned int tIDX
		cdef unsigned int itpt = 0
		cdef int igen
		cdef DTYPE_t real_time
		cdef DTYPE_t theoretical_time
		cdef list CompareWithData = []
		cdef list CellsAtAllGens = [[] for _ in range(len(self.harvestTimes))]
		for itpt, ht in enumerate(self.harvestTimes):
			t_idx = np.where(TIMES == ht)
			for igen in range(self.maxDivisions+1):
				CellsAtAllGens[itpt].append(LiveMatrix[igen, t_idx[0][0]])
			CompareWithData.append(TotalLiveCell[t_idx[0][0]])
		# 1-Oct-2018 : wrong method to summarise live cells
		# for tIDX, theoretical_time in enumerate(timesWith0):
		# 	for real_time in self.harvestTimes:
		# 		if real_time == theoretical_time:
		# 			for igen in range(0, self.maxDivisions+1):
		# 				CellsAtAllGens[itpt].append(LiveMatrix[igen, tIDX])
		# 			CompareWithData.append(TotalLiveCell[tIDX])
		# 			itpt += 1

		# compute cumulative dead cells at each generations
		# cdef DTYPE_t sum
		# cdef np.ndarray[DTYPE_t, ndim=2] cumDeadCell = np.zeros(shape=(self.maxDivisions+1, n+1), dtype=DTYPE)
		# for i in range(len(deathMatrix)):
		#     sum = <DTYPE_t>0.0
		#     for j in range(len(deathMatrix[0])):
		#         sum += deathMatrix[i, j]
		#         cumDeadCell[i, j] = sum
		return TotalLiveCell, CompareWithData, CellsAtAllGens, LiveMatrix