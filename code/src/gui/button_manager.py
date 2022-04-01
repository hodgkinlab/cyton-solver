import copy
import psutil
from functools import partial
from datetime import datetime
from PyQt5.Qt import Qt, QColor, pyqtSlot
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QGridLayout, \
	QPushButton, QComboBox, QDialog, QSpinBox, QRadioButton, QDoubleSpinBox, QLabel, QSizePolicy, \
	QTableWidget, QTableWidgetItem, QDialogButtonBox, QAbstractItemView, QCheckBox, QLineEdit

import src.common.settings as config
import src.common.global_vars as gvars
from src.IO.error_handler import CustomError
from src.IO.export_params import ExportParams
from src.IO.import_params import ImportParams
from src.IO.export_plots import ExportPlot
from src.qmods.thread import BackThread
from src.qmods.spinbox import SpinBox
# from src.workbench.bootstrap import bootstrap


class ButtonManager:
	def __init__(self, parent=None, model_id=''):
		self.parent = parent
		self.model_id = model_id

		self._button_layout = QHBoxLayout()
		self._button_layout.addWidget(self.create_button_layout())

		self.param_exporter = ExportParams(model_id)
		self.param_loader = ImportParams(model_id, parent)
		self.plot_exporter = ExportPlot(model_id)

		self.boot_settings = {
			'on': False,
			'iter': 0,
			'range': 95,
		}

	def create_button_layout(self):
		if self.model_id == 'cyton1':
			group_box = QGroupBox("Cyton 1 Actions")
		elif self.model_id == 'cyton1.5':
			group_box = QGroupBox("Cyton 1.5 Actions")
		_layout = QGridLayout()

		# calls fit interface
		self.fit_button = QPushButton("Fit")
		self.fit_button.clicked.connect(self.handle_fit_btn)
		# saves current param values to excel file
		save_fit_button = QPushButton("Save Params")
		save_fit_button.clicked.connect(self.handle_save_fit_btn)
		# load saved or existing params
		load_fit_button = QPushButton("Load Params")
		load_fit_button.clicked.connect(self.handle_load_fit_btn)
		# opens data manager
		self.data_manager = QPushButton("Data Inc/Exc")
		self.data_manager.clicked.connect(self.handle_data_manager_btn)

		export_plot = QPushButton("Export Plot")
		export_plot.clicked.connect(self.handle_export_plot_btn)

		group_box2 = QGroupBox("Select Conditions")

		_standalone_layout = QHBoxLayout()
		self.data_select = QComboBox()
		self.data_select.setEnabled(False)

		_standalone_layout.addWidget(self.data_select)
		group_box2.setLayout(_standalone_layout)

		_layout.addWidget(self.fit_button, 0, 0)
		_layout.addWidget(save_fit_button, 0, 1)
		_layout.addWidget(load_fit_button, 0, 2)
		_layout.addWidget(self.data_manager, 1, 0)
		_layout.addWidget(export_plot, 1, 1, 1, 2)
		_layout.addWidget(group_box2, 2, 0, 1, 3)

		_layout.setSpacing(5)
		group_box.setLayout(_layout)

		return group_box

	def handle_save_fit_btn(self):
		# create save parameter interface dialog
		self.param_exporter.interface()

	def handle_load_fit_btn(self):
		self.param_loader.interface()

	def handle_export_plot_btn(self):
		try:
			if not config.FILE_LOADED:
				raise NotImplementedError("Exporting plots without importing data is not supported yet! Please use 'Data Free' mode if you wish to export pure model results.")
			else:
				self.plot_exporter.export_plot_with_data()
		except NotImplementedError as nie:
			print("[NOT IMPLEMENTED ERROR] {0}".format(nie))

	def handle_fit_btn(self):
		def _fit_to_abort(thread):
			fit_palette = self.fit_button.palette()
			role = self.fit_button.foregroundRole()
			fit_palette.setColor(role, QColor('red'))
			self.fit_button.setPalette(fit_palette)
			self.fit_button.setText("Abort Fit")
			self.fit_button.clicked.disconnect()
			self.fit_button.clicked.connect(lambda: abort_fit(thread))

		def _abort_to_fit():
			# revert back to original buttons
			self.fit_button.clicked.disconnect()
			fit_palette = self.fit_button.palette()
			role = self.fit_button.foregroundRole()
			# fit_palette.setColor(role, QColor('black')) # Note: uncomment this for default PyQt5 style
			fit_palette.setColor(role, QColor('white'))
			self.fit_button.setPalette(fit_palette)
			self.fit_button.setText("Fit")
			self.fit_button.clicked.connect(self.handle_fit_btn)

		def algo_option_btn(btn, options):
			obj_name = btn.objectName()
			if obj_name == 'LM':
				for idx, option in reversed(list(enumerate(options))):
					if idx > 7:
						option.hide()
					else:
						option.show()
			elif obj_name == 'DE':
				for idx, option in enumerate(options):
					if idx > 7:
						option.show()
					else:
						option.hide()

		def batch_fit():
			if _batch_fit.isChecked():
				ext_options.show()
				win.adjustSize()
			else:
				ext_options.hide()
				win.adjustSize()

		def compute_ci():
			if _ci.isChecked():
				ci_options.show()
				win.adjustSize()
			else:
				ci_options.hide()
				win.adjustSize()

		@pyqtSlot(str, list)
		def when_fit_finished(msg, result):
			print(msg)

			_abort_to_fit()

			# update QDoubleSpinBox values and sliders locations
			# MUST block signals of params.valueChanged from "handle_param_value_changed" to avoid multiple plot updates
			# NOTE : DO NOT USE BLOCK SIGNALS FOR UPDATING PARAMETERS. THEY DO NOT UPDATE SLIDER's POSITION!
			if self.model_id == 'cyton1':
				for i, key in enumerate(gvars.C1_PARAMS):
					gvars.C1_PARAMS[key] = result[i]

				# update GUI parameters
				for i, item in enumerate(self.parent.params):
					item.valueChanged.disconnect(self.parent.c1_event_handler.handle_param_value_changed)
					item.setValue(result[i])
					item.valueChanged.connect(self.parent.c1_event_handler.handle_param_value_changed)

				self.parent.c1_plot.update_plot()
			elif self.model_id == 'cyton1.5':
				for i, key in enumerate(gvars.C15_PARAMS):
					gvars.C15_PARAMS[key] = result[i]

				# update GUI parameters
				for i, item in enumerate(self.parent.params15):
					item.valueChanged.disconnect(self.parent.c15_event_handler.handle_param_value_changed)
					item.setValue(result[i])
					item.valueChanged.connect(self.parent.c15_event_handler.handle_param_value_changed)

				self.parent.c15_plot.update_plot()

			# TODO: complete the bootstrap function. The core method is implemented and it works on standalone script, however, it fails when the program fork/spawn another processor for some reason.
			try:
				if self.boot_settings['on']:
					raise NotImplementedError("Bootstrapping is not supported yet")
					# bootstrap(gvars.C15_ICND, result, self.boot_settings['iter'], self.boot_settings['range'])
			except NotImplementedError as ne:
				print("[NOT IMPLEMENTED ERROR] {0}".format(ne))

		def abort_fit(thread):
			# send abort signal down to spawned thread -> this is custom method
			thread.stop()
			_abort_to_fit()

		def accept():
			now = datetime.now().replace(microsecond=0)
			if _batch_fit.isChecked():
				conditions = []
				for icnd, cond in enumerate(selectable_conditions):
					if cond.isChecked():
						conditions.append(gvars.CONDITIONS[icnd])
				print("[{0}] Initialising {1} fit sequence for {2}. . .".format(now, self.model_id, conditions))
			else:
				print("[{0}] Initialising {1} fit sequence for [{2}]. . .".format(now, self.model_id, gvars.CONDITIONS[self.data_select.currentIndex()]))
			# prepare algorithm settings -> thread -> init_fit.py
			algo_settings = []
			if _LM.isChecked():
				algo_settings.append('LM')
				algo_settings.append(lm_iter_box.value())
				algo_settings.append(ftol_box.value())
				algo_settings.append(xtol_box.value())
				algo_settings.append(gtol_box.value())
			elif _DE.isChecked():
				algo_settings.append('DE')
				algo_settings.append(de_iter_box.value())
				algo_settings.append(popsize_box.value())
				algo_settings.append(reltol_box.value())
				algo_settings.append(abstol_box.value())

			batch_settings = [_batch_fit.isChecked(), selectable_conditions, self.data_select]
			self.boot_settings['on'] = _ci.isChecked()
			self.boot_settings['iter'] = ci_iter.value()
			self.boot_settings['range'] = ci_range.value()

			fit_total_cells = _fit_to_total_cells.isChecked()

			# spawn a thread to put fitting in background process
			thread = BackThread(self.model_id, algo_settings, batch_settings, fit_total_cells, self.boot_settings)
			thread.finished[str, list].connect(when_fit_finished)
			thread.start()

			# change fit button -> abort fit
			_fit_to_abort(thread)

			win.close()
			config.CONSOLE.show()

		def reject():
			win.close()

		try:
			if config.FILE_LOADED and not config.DATA_FREE:
				win = QDialog()
				win.setModal(True)

				_outer_layout = QVBoxLayout()
				_top_layout = QHBoxLayout()

				group_box = QGroupBox("Choose optimisation algorithm")
				_algo_layout = QHBoxLayout()

				opt_group_box = QGroupBox("Algorithm specific options")
				_opt_layout = QGridLayout()

				# create algorithm option layout

				# Levenberg-Marquardt algorithm
				_LM = QRadioButton("Levenberg-Marquardt")
				_LM.setObjectName('LM')

				# set LM method as a default
				_LM.toggle()
				lm_iter_box_label = QLabel("Iteration number: ")
				lm_iter_box = QSpinBox()
				lm_iter_box.setRange(1, 99999)
				lm_iter_box.setValue(99999)
				ftol_box_label = QLabel("Relative err. in SS: ")
				ftol_box = QDoubleSpinBox()
				ftol_box.setButtonSymbols(2)
				ftol_box.setDecimals(10)
				ftol_box.setValue(1.49012E-08)
				xtol_box_label = QLabel("Relative err. in approx. soln: ")
				xtol_box = QDoubleSpinBox()
				xtol_box.setButtonSymbols(2)
				xtol_box.setDecimals(10)
				xtol_box.setValue(1.49012E-08)
				gtol_box_label = QLabel("Orthogonality b/w fn vector & jac: ")
				gtol_box = QDoubleSpinBox()
				gtol_box.setButtonSymbols(2)
				gtol_box.setDecimals(10)
				gtol_box.setValue(0.0)

				_opt_layout.addWidget(lm_iter_box_label, 0, 0)
				_opt_layout.addWidget(lm_iter_box, 0, 1)
				_opt_layout.addWidget(ftol_box_label, 1, 0)
				_opt_layout.addWidget(ftol_box, 1, 1)
				_opt_layout.addWidget(xtol_box_label, 2, 0)
				_opt_layout.addWidget(xtol_box, 2, 1)
				_opt_layout.addWidget(gtol_box_label, 3, 0)
				_opt_layout.addWidget(gtol_box, 3, 1)

				# Differential Evolution algorithm
				_DE = QRadioButton("Differential Evolution")
				_DE.setObjectName('DE')
				# DE options
				de_iter_box_label = QLabel("Max. generation: ")
				de_iter_box = QSpinBox()
				de_iter_box.setRange(1, 99999)
				de_iter_box.setValue(99999)
				popsize_box_label = QLabel("Population size: ")
				popsize_box = QSpinBox()
				popsize_box.setValue(15)
				popsize_box.setRange(1, 99999)
				reltol_box_label = QLabel("Relative tolerance: ")
				reltol_box = QDoubleSpinBox()
				reltol_box.setButtonSymbols(2)
				reltol_box.setDecimals(5)
				reltol_box.setValue(0.01)
				reltol_box.setRange(1E-10, 99999)
				abstol_box_label = QLabel("Absolute tolerance: ")
				abstol_box = QDoubleSpinBox()
				abstol_box.setButtonSymbols(2)
				abstol_box.setDecimals(5)
				abstol_box.setValue(0)
				abstol_box.setRange(1E-10, 99999)

				_opt_layout.addWidget(de_iter_box_label, 4, 0)
				_opt_layout.addWidget(de_iter_box, 4, 1)
				_opt_layout.addWidget(popsize_box_label, 5, 0)
				_opt_layout.addWidget(popsize_box, 5, 1)
				_opt_layout.addWidget(reltol_box_label, 6, 0)
				_opt_layout.addWidget(reltol_box, 6, 1)
				_opt_layout.addWidget(abstol_box_label, 7, 0)
				_opt_layout.addWidget(abstol_box, 7, 1)
				opt_group_box.setLayout(_opt_layout)

				# collect all options in an array for easy iteration
				options = [
					lm_iter_box_label, lm_iter_box,
					ftol_box_label, ftol_box,
					xtol_box_label, xtol_box,
					gtol_box_label, gtol_box,
					de_iter_box_label, de_iter_box,
					popsize_box_label, popsize_box,
					reltol_box_label, reltol_box,
					abstol_box_label, abstol_box
				]

				opt_group_box.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
				for i, option in enumerate(options):
					if i > 7:
						option.hide()

				_LM.toggled.connect(lambda: algo_option_btn(_LM, options))
				_DE.toggled.connect(lambda: algo_option_btn(_DE, options))

				_algo_layout.addWidget(_LM)
				_algo_layout.addWidget(_DE)
				group_box.setLayout(_algo_layout)

				# give an option to fit multiple conditions
				_ext_option = QGroupBox('Extra options')
				_ext_option_layout = QGridLayout()
				# a checkbox for fitting all conditions one by one (later use multiprocess for faster & efficient fittings)
				_batch_fit = QCheckBox("batch fit")
				_batch_fit.toggled.connect(lambda: batch_fit())
				_ext_option_layout.addWidget(_batch_fit, 0, 0)

				_ci = QCheckBox("CI [Bootstrap]")
				_ci.toggled.connect(lambda: compute_ci())
				_ext_option_layout.addWidget(_ci, 0, 1)

				# construct Total Cell Fitting (instead of fit to cell-gen profile)
				_fit_to_total_cells = QCheckBox("Fit to total cells")
				_ext_option_layout.addWidget(_fit_to_total_cells, 0, 2)

				_ext_option.setLayout(_ext_option_layout)

				_top_layout.addWidget(group_box)
				_top_layout.addWidget(_ext_option)

				# construct option panel for batch fitting
				ext_options = QGroupBox(' > select conditions to batch fit')
				ext_options_layout = QGridLayout()
				row, col = 0, 0
				selectable_conditions = []
				for icnd, cond in enumerate(gvars.CONDITIONS):
					opt = QCheckBox(cond)
					ext_options_layout.addWidget(opt, row, col)
					if icnd == gvars.C1_ICND and self.model_id == 'cyton1':
						opt.setChecked(True)
						opt.setEnabled(False)
					elif icnd == gvars.C15_ICND and self.model_id == 'cyton1.5':
						opt.setChecked(True)
						# ensure at least one condition is checked
						opt.setEnabled(False)
					selectable_conditions.append(opt)
					col += 1
					if col == 4:
						row += 1
						col = 0
				ext_options.setLayout(ext_options_layout)
				ext_options.hide()

				# construct CI option panel
				nc = psutil.cpu_count(logical=False)  # get number of cpu cores (incl. hyper threads)

				ci_options = QGroupBox(' > confidence interval options')
				ci_options_layout = QGridLayout()
				ci_iter_label = QLabel("Bootstrap iteration number [Multiples of {0}]: ".format(nc))
				ci_iter = SpinBox()  # qmod oject -> needed few overrides for number verification
				ci_iter.setRange(1, 99999)
				ci_iter.setValue(nc * 10)
				ci_iter.setSingleStep(nc)
				ci_range_label = QLabel("% Confidence Range: ")
				ci_range = QDoubleSpinBox()
				ci_range.setRange(0, 100)
				ci_range.setButtonSymbols(2)
				ci_range.setDecimals(1)
				ci_range.setSuffix(' %')
				ci_range.setValue(95)

				ci_options_layout.addWidget(ci_iter_label, 0, 0)
				ci_options_layout.addWidget(ci_iter, 0, 1)
				ci_options_layout.addWidget(ci_range_label, 1, 0)
				ci_options_layout.addWidget(ci_range, 1, 1)
				ci_options.setLayout(ci_options_layout)
				ci_options.hide()

				_outer_layout.addLayout(_top_layout)
				_outer_layout.addWidget(ext_options)
				_outer_layout.addWidget(ci_options)
				_outer_layout.addWidget(opt_group_box)

				# execution buttons
				button = QDialogButtonBox(
					QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
					Qt.Horizontal, win
				)
				button.accepted.connect(accept)
				button.rejected.connect(reject)
				_outer_layout.addWidget(button, alignment=Qt.AlignRight)

				win.setLayout(_outer_layout)

				win.setAttribute(Qt.WA_DeleteOnClose)
				win.exec_()
			else:
				if config.DATA_FREE:
					raise CustomError("There's no data to fit in Data Free mode!", loc='fit')
				else:
					raise CustomError("You need to import data first!", loc='fit')
		except CustomError as ce:
			now = datetime.now().replace(microsecond=0)
			print("[{0}] {1}".format(now, ce.message))

	def handle_data_manager_btn(self):
		global tmp_check_matrix

		def accept():
			if self.model_id == 'cyton1':
				gvars.C1_CHECK = tmp_check_matrix
				self.parent.c1_plot.update_plot()
			elif self.model_id == 'cyton1.5':
				gvars.C15_CHECK = tmp_check_matrix
				self.parent.c15_plot.update_plot()
			data_window.close()

		def reject():
			data_window.close()

		def flag_data(btn):
			# get indices of highlighted cells
			rows = sorted(set(index.row() for index in tw_data_handler.selectedIndexes()))
			cols = sorted(set(index.column() for index in tw_data_handler.selectedIndexes()))

			if btn == include_button:
				flag = 1
				# change background color of highlighted cells back to normal to indicate that they are included
				color = QColor(0, 0, 0)
			elif btn == exclude_button:
				flag = 0
				# set background color of those cells to grey color to indicate they are excluded
				color = QColor(128, 128, 128)

			# set background colors accordingly
			for r in rows:
				for c in cols:
					tw_data_handler.item(r, c).setBackground(color)

			tps, reps = [], []
			for c in cols:
				# get time point index
				header = tw_data_handler.horizontalHeaderItem(c).text()
				it = gvars.EXP_HT[icnd].index(float(header))
				tps.append(it)

				# get replicate index
				i = gvars.EXP_HT_REPS[icnd].index(float(header))
				ir = c - i
				reps.append(ir)

			# update check matrix
			for it, tp in enumerate(tps):
				ir = reps[it]
				for igen in rows:
					tmp_check_matrix[icnd][tp][ir][igen] = flag

		# BEGIN DATA MANGER HANDLER FROM HERE
		try:
			if config.FILE_LOADED and not config.DATA_FREE:
				data_window = QDialog()
				data_window.setWindowTitle('Data Selection Window')
				_layout = QGridLayout()
				tw_data_handler = QTableWidget()
				# make table widget uneditable
				tw_data_handler.setEditTriggers(QAbstractItemView.NoEditTriggers)

				if self.model_id == 'cyton1':
					icnd = gvars.C1_ICND
					tmp_check_matrix = copy.deepcopy(gvars.C1_CHECK)
				elif self.model_id == 'cyton1.5':
					icnd = gvars.C15_ICND
					tmp_check_matrix = copy.deepcopy(gvars.C15_CHECK)

				# create vertical labels (i.e. division numbers)
				vheaders = ['Div %s' % i for i in range(gvars.MAX_DIV_PER_CONDITIONS[icnd]+1)]
				tw_data_handler.setRowCount(len(vheaders))
				tw_data_handler.setVerticalHeaderLabels(vheaders)

				# create horizontal labels (i.e. harvested time points)
				hheaders = []
				for ht in gvars.EXP_HT_REPS[icnd]:
					hheaders.append(str(ht))
				tw_data_handler.setColumnCount(len(hheaders))
				tw_data_handler.setHorizontalHeaderLabels(hheaders)

				# populate table widget
				col = 0
				for itpt in range(gvars.EXP_NUM_TP[icnd]):
					for irep, data in enumerate(gvars.CELL_GENS_REPS[icnd][itpt]):
						for row, datum in enumerate(data):
							tw_data_handler.setItem(row, col, QTableWidgetItem(str(datum)))
							# check for excluded data & color them accordingly
							if not tmp_check_matrix[icnd][itpt][irep][row]:
								tw_data_handler.item(row, col).setBackground(QColor(128, 128, 128))
						col += 1
				tw_data_handler.resizeRowsToContents()

				_layout.addWidget(tw_data_handler, 0, 0, 1, 3)
				data_window.setLayout(_layout)
				dialog_height = tw_data_handler.verticalHeader().length() + 100
				data_window.setFixedSize(1100, dialog_height)

				include_button = QPushButton("include")
				include_button.clicked.connect(partial(flag_data, include_button))
				exclude_button = QPushButton("exclude")
				exclude_button.clicked.connect(partial(flag_data, exclude_button))

				button = QDialogButtonBox(
					QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
					Qt.Horizontal, data_window
				)
				button.accepted.connect(accept)
				button.rejected.connect(reject)
				_layout.addWidget(include_button, 1, 0)
				_layout.addWidget(exclude_button, 1, 1)
				_layout.addWidget(button, 1, 2)

				data_window.setAttribute(Qt.WA_DeleteOnClose)
				data_window.exec_()
			else:
				if not config.FILE_LOADED:
					raise CustomError("You need to import data first!", loc='data_manager')
				else:
					raise CustomError("There's no data to include/exclude in Data Free mode!", loc='data_manager')
		except CustomError as ce:
			now = datetime.now().replace(microsecond=0)
			print('[{0}] {1}'.format(now, ce.message))


