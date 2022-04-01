import numpy as np
from scipy.stats import norm, lognorm, expon

import src.common.settings as config
import src.common.global_vars as gvars
from src.workbench.cyton1.c1_model import Cyton1Model
from src.workbench.cyton15.c15_model import Cyton15Model


class UpdatePDF:
	def __init__(self):
		self.t = np.arange(0.1, max(gvars.HT), 0.01)

		# cyton 1
		self.undividedDiv = []
		self.undividedDeath = []
		self.dividedDiv = []
		self.dividedDeath = []

		# cyton 1.5
		self.unstimDeath = []
		self.stimDiv = []
		self.stimDeath = []
		self.stimDD = []

	@staticmethod
	def compute_pdf(times, mu, sig, lamb=1, pdf_type='Lognormal'):
		if pdf_type == 'Lognormal':
			log_mu = np.log(mu)
			return lognorm.pdf(times, sig, scale=np.exp(log_mu))
		elif pdf_type == 'Gaussian':
			return norm.pdf(times, loc=mu, scale=sig)
		elif pdf_type == 'Exponential':
			return expon.pdf(times, scale=1.0 / mu)

	def update_cyton1_pdf(self):
		# if config.FILE_LOADED and not config.DATA_FREE:
		# 	self.t = np.arange(0.1, max(gvars.EXP_HT[gvars.C1_ICND]), 0.01)
		# else:
		self.t = np.arange(0.1, max(gvars.HT), 0.01)

		self.undividedDiv = self.compute_pdf(
			self.t,
			gvars.C1_PARAMS['mu0div'], gvars.C1_PARAMS['sig0div'],
			pdf_type=config.CYTON1_CONFIG['first_div']
		)
		self.undividedDeath = -self.compute_pdf(
			self.t,
			gvars.C1_PARAMS['mu0death'], gvars.C1_PARAMS['sig0death'],
			pdf_type=config.CYTON1_CONFIG['first_die']
		)
		self.dividedDiv = self.compute_pdf(
			self.t,
			gvars.C1_PARAMS['muSubdiv'], gvars.C1_PARAMS['sigSubdiv'],
			pdf_type=config.CYTON1_CONFIG['subsq_div']
		)
		self.dividedDeath = -self.compute_pdf(
			self.t,
			gvars.C1_PARAMS['muSubdeath'], gvars.C1_PARAMS['sigSubdeath'],
			pdf_type=config.CYTON1_CONFIG['subsq_die']
		)

	def update_cyton15_pdf(self):
		# if config.FILE_LOADED and not config.DATA_FREE:
		# 	self.t = np.arange(0.1, max(gvars.EXP_HT[gvars.C15_ICND]), 0.01)
		# else:
		self.t = np.arange(0.1, max(gvars.HT), 0.01)

		self.unstimDeath = -self.compute_pdf(
			self.t,
			gvars.C15_PARAMS['unstimMuDeath'], gvars.C15_PARAMS['unstimSigDeath'],
			pdf_type=config.CYTON15_CONFIG['unstim_die']
		)
		self.stimDiv = self.compute_pdf(
			self.t,
			gvars.C15_PARAMS['stimMuDiv'], gvars.C15_PARAMS['stimSigDiv'],
			pdf_type=config.CYTON15_CONFIG['stim_div']
		)
		self.stimDeath = -self.compute_pdf(
			self.t,
			gvars.C15_PARAMS['stimMuDeath'], gvars.C15_PARAMS['stimSigDeath'],
			pdf_type=config.CYTON15_CONFIG['stim_die']
		)
		self.stimDD = self.compute_pdf(
			self.t,
			gvars.C15_PARAMS['stimMuDD'], gvars.C15_PARAMS['stimSigDD'],
			pdf_type=config.CYTON15_CONFIG['stim_dd']
		)


class UpdateModelCurve:
	def __init__(self):
		# n = int(max(gvars.HT)/gvars.TIME_INC) + 1
		# self.model_time = np.linspace(0.0, max(gvars.HT), n)
		self.model_time = np.arange(0.0, max(gvars.HT)+gvars.TIME_INC, gvars.TIME_INC)

		self.c1_total_cells = []
		self.c15_total_cells = []

	def update_cyton1_model(self):
		if config.FILE_LOADED and not config.DATA_FREE:
			# n = int(max(gvars.EXP_HT[gvars.C1_ICND]) / gvars.TIME_INC) + 1
			# self.model_time = np.linspace(0.0, max(gvars.EXP_HT[gvars.C1_ICND]), n)
			self.model_time = np.arange(0.0, max(gvars.HT)+gvars.TIME_INC, gvars.TIME_INC)

			self.c1_total_cells = Cyton1Model(
				gvars.EXP_HT[gvars.C1_ICND],
				gvars.INIT_CELL,
				gvars.MAX_DIV,
				gvars.TIME_INC, [], []
			).compute_model_results(self.model_time, gvars.C1_PARAMS)
		else:
			# n = int(max(gvars.HT) / gvars.TIME_INC) + 1
			# self.model_time = np.linspace(0.0, max(gvars.HT), n)
			self.model_time = np.arange(0.0, max(gvars.HT)+gvars.TIME_INC, gvars.TIME_INC)

			self.c1_total_cells = Cyton1Model(
				gvars.HT,
				gvars.INIT_CELL,
				gvars.MAX_DIV,
				gvars.TIME_INC, [], []
			).compute_model_results(self.model_time, gvars.C1_PARAMS)

	def update_cyton15_model(self):
		if config.FILE_LOADED and not config.DATA_FREE:
			# n = int(max(gvars.EXP_HT[gvars.C15_ICND]) / gvars.TIME_INC) + 1
			# self.model_time = np.linspace(0.0, max(gvars.EXP_HT[gvars.C15_ICND]), n)
			self.model_time = np.arange(0.0, max(gvars.HT)+gvars.TIME_INC, gvars.TIME_INC)

			self.c15_total_cells = Cyton15Model(
				gvars.EXP_HT[gvars.C15_ICND],
				gvars.INIT_CELL,
				gvars.MAX_DIV,
				gvars.TIME_INC, [], [], False
			).compute_model_results(self.model_time, gvars.C15_PARAMS)
		else:
			# n = int(max(gvars.HT) / gvars.TIME_INC) + 1
			# self.model_time = np.linspace(0.0, max(gvars.HT), n)
			self.model_time = np.arange(0.0, max(gvars.HT)+gvars.TIME_INC, gvars.TIME_INC)

			self.c15_total_cells = Cyton15Model(
				gvars.HT,
				gvars.INIT_CELL,
				gvars.MAX_DIV,
				gvars.TIME_INC, [], [], False
			).compute_model_results(self.model_time, gvars.C15_PARAMS)


class UpdateCompare:
	def __init__(self):
		pass
