"""
This module allows the optimisation process to run separately from the main program thread. Otherwise the program will
freeze until the job is done.
Basically, this module acts as a bridge to spawn a thread and tell it what to do.
"""

from datetime import datetime
from PyQt5.Qt import QThread, pyqtSignal

import src.common.global_vars as gvars
from src.IO.error_handler import CustomError
from src.workbench.fit import fit_to_cyton1, fit_to_cyton15


class BackThread(QThread):

	finished = pyqtSignal(str, list)

	def __init__(self, model_id, algo_settings, batch_settings, fit_to_total_cells, boot_settings):
		QThread.__init__(self)
		self.setTerminationEnabled(True)
		self.is_running = True

		self.model_to_fit = model_id
		self.algo_settings = algo_settings

		# special options
		self.batch_fit = batch_settings[0]
		self.conditions = batch_settings[1]
		self.sd = batch_settings[2]

		self.fit_to_total_cells = fit_to_total_cells

		if self.model_to_fit == 'cyton1':
			self.fitted_params = [
				gvars.C1_PARAMS['mu0div'], gvars.C1_PARAMS['sig0div'],
				gvars.C1_PARAMS['mu0death'], gvars.C1_PARAMS['sig0death'],
				gvars.C1_PARAMS['muSubdiv'], gvars.C1_PARAMS['sigSubdiv'],
				gvars.C1_PARAMS['muSubdeath'], gvars.C1_PARAMS['sigSubdeath'],
				gvars.C1_PARAMS['pf0'], gvars.C1_PARAMS['pfmu'], gvars.C1_PARAMS['pfsig'],
				gvars.C1_PARAMS['MechProp'], gvars.C1_PARAMS['MechDecayConst']
			]
		elif self.model_to_fit == 'cyton1.5':
			self.fitted_params = [
				gvars.C15_PARAMS['unstimMuDeath'], gvars.C15_PARAMS['unstimSigDeath'],
				gvars.C15_PARAMS['stimMuDiv'], gvars.C15_PARAMS['stimSigDiv'],
				gvars.C15_PARAMS['stimMuDeath'], gvars.C15_PARAMS['stimSigDeath'],
				gvars.C15_PARAMS['stimMuDD'], gvars.C15_PARAMS['stimSigDD'],
				gvars.C15_PARAMS['SubDivTime'], gvars.C15_PARAMS['pfrac']
			]
		else:
			self.fitted_params = []  # just in case

	def run(self):
		try:
			if self.model_to_fit == 'cyton1':
				if self.batch_fit:
					raise NotImplementedError("Fitting multiple conditions is not implemented for Cyton 1 yet")
				elif self.fit_to_total_cells:
					raise NotImplementedError("Fitting to total cell number is not implemented for Cyton 1 yet")
				else:
					self.fitted_params = fit_to_cyton1(self, self.algo_settings)
					self.done()
			elif self.model_to_fit == 'cyton1.5':
				if self.batch_fit:
					# TODO: finish implementing batch fitting feature.
					raise NotImplementedError("This feature is not implemented for Cyton 1.5 yet")
				# TODO: implement 3Factor model for fitting all conditions at once while sharing target parameters
				else:
					self.fitted_params = fit_to_cyton15(self, self.algo_settings, self.fit_to_total_cells)
					self.done()
		except NotImplementedError as ne:
			print("[NOT IMPLEMENTED ERROR] {0}".format(ne))
		except CustomError as ce:
			now = datetime.now().replace(microsecond=0)
			print("[{0}] {1}".format(now, ce.message))
		except Exception as e:
			print("[DEBUG MESSAGE] {0}".format(e))

	def stop(self):
		self.is_running = False

	def done(self):
		self.is_running = False
		now = datetime.now().replace(microsecond=0)
		self.finished.emit("[{0}] Done fitting!".format(now), self.fitted_params)