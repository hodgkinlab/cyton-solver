#! /usr/bin/env python3.6
"""
Last edited: 3-Oct-2018
Author: HoChan Cheon
Email: cheon.h@wehi.edu.au

This is the main entrance of CytonSolver.
Every components of the program will be initiated and constructed when this script is executed in terminal.

For devlopers:
	* project root is defined in line (44) in this file. But I recommend to include it in Python environment for safety.
		root/
			├─── img/            [contains all images used for the program (with bit extras)]
			└─── src/
				├─── common/     [function/variable module; common functions, global variables, program/model settings]
				├─── gui/        [GUI constructor module; visible GUI components & event handlers]
				├─── IO/         [input/ouput module; import data, export plot/parameters, error handler]
				├─── plot/       [plot module; canvas definition for Cyton1 & Cyton1.5, update handler]
				├─── qmods/      [modified pyqt5 module; make minor adjustments to default pyqt5 modules]
				└─── workbench/  [cyton model module; model computation, optimisation]
	* use virtual environment, which should be located at the project root.
	* use "requirements.txt" to install 3rd party libraries used in the program.
		pip install -r requirements.txt
	* interrogate all python scripts in "gui/" module before modifying any of core model functions.
		I recommend look "main_cs.py" first, then "tab_manager.py" (along with tab_items module), then "button_manager.py".
		These three files are essential for constructing visual components. Other functional modules are slotted in between.
		Make sure to understand how signals (or event handling) works in PyQt5.

	* NB: the functions are quite entangled and perhaps it might be overwhelming at first glance. You will probably notice
	sooner or later that the functions are mostly splitted into two parts; for Cyton 1 and Cyton 1.5. Generally speaking,
	they share common logic (therefore variables) except in different names. So to ease out the understanding process,
	I recommend you to follow Cyton 1.5, and ignore Cyton 1.
	There are number of program specific features I implemented (e.g. compare pdfs in Compare tab) that supposedly work
	for both Cyton 1 and Cyton 1.5. However, I dedicated most of my time developing Cyton 1.5, and added the features as
	I needed for analysing data. For the ones that does work for Cyton 1.5 but not Cyton 1, I have put NotImplementedError
	exceptions, so the program does not prematurely terminate. In future, perhaps someone can complete the code for the
	sake of completion. Various to-do notes throughout the program might be helpful to understand what is missing.
"""

# system built-in imports
import copy
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))  # set project root
import time
import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", category=Warning)
import logging
from datetime import datetime
from multiprocessing.dummy import Pool

# 3rd party science library
import numpy as np

# PyQt5 imports
from PyQt5.QtCore import Qt, QEventLoop
from PyQt5.QtGui import QIcon, QTextCursor, QPalette, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QDialog, QAction, QSizePolicy, \
	QVBoxLayout, QGridLayout, QGroupBox, QLabel, QComboBox, QHBoxLayout, QDialogButtonBox, QDoubleSpinBox, \
	QMessageBox
# For Windows OS scaling
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"  # must turn off the auto scaling for multi-screen high dpi setup
if hasattr(Qt, 'AA_EnableHighDpiScaling'):
	QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
	QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

# my modules
import src.common.settings as config
import src.common.global_vars as gvars
from src.common.functions import create_check_matrix, reset_global_vars
from src.qmods.console import Console
from src.qmods.splash import SplashScreen
from src.IO.file_reader import ReadData
from src.IO.console_logger import ConsoleLogger
from src.IO.error_handler import CustomError
from src.workbench.data_manager import compute_total_cells, sort_cell_generations
from src.gui.tab_manager import TabManager

version = '1.1.3\u03b2'


class MainCytonSolver(QMainWindow, TabManager):
	def __init__(self):
		super().__init__()
		self.title = 'CytonSolver v{0}'.format(version)
		self.left, self.top, self.width, self.height = 0, 0, width, height
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)

		# this is required for windows, otherwise it literally covers the entire screen!
		self.showMaximized()

		# global components
		config.CONSOLE = Console()
		config.CONSOLE.resize(1120, 500)
		self.last_path = None

		# construct all UI elements -> cascading down to individual components
		self.create_menu_bar()
		self.create_console()

		self.setCentralWidget(self.main_tabs)  # NOTE: self.main_tabs are inherited component from TabManager

	@staticmethod
	def resource_path(relative_path):
		""" Get absolute path to resource, works for dev and for PyInstaller """
		try:
			# Note : PyInstaller creates a temp folder and stores path in _MEIPASS
			base_path = sys._MEIPASS
		except Exception:
			# if not production mode, return project root folder
			base_path = os.path.abspath(".")
		return os.path.join(base_path, relative_path)

	# custom shortcuts
	def keyPressEvent(self, event):
		k = event.key()
		kmod = event.modifiers()
		# Press "CMD+O" import new data file
		if (kmod & Qt.ControlModifier) and k == Qt.Key_O:
			self.handle_import_data()
		# Press "CMD+M" brings model setting dialog
		elif (kmod & Qt.ControlModifier) and k == Qt.Key_M:
			self.handle_model_settings()
		# Press "CMD+C" toggles console log on & off
		elif (kmod & Qt.ControlModifier) and k == Qt.Key_C:
			if config.TOGGLE_CONSOLE:
				config.CONSOLE.close()
			else:
				config.CONSOLE.show()

	def create_menu_bar(self):
		menu_bar = self.menuBar()

		# first 'File' menu
		file_menu = menu_bar.addMenu("File")

		# import data
		import_action = QAction(QIcon(self.resource_path('img/gui_icons/import.png')), ' Open...\tCtrl+O', self)
		import_action.triggered.connect(self.handle_import_data)

		# exit protocol
		exit_action = QAction(' Exit', self)
		exit_action.triggered.connect(cs_app.quit)

		file_menu.addAction(import_action)
		file_menu.addSeparator()
		file_menu.addAction(exit_action)

		# extra menu for GUI interfaces
		tool_menu = menu_bar.addMenu("Tools")
		console_action = QAction(QIcon(self.resource_path('img/gui_icons/console.png')), 'Console\tCtrl+C', self)
		console_action.triggered.connect(self._console_handler)

		cs_setting_action = QAction(QIcon(self.resource_path('img/gui_icons/settings.png')), 'Model Settings\tCtrl+M', self)
		cs_setting_action.triggered.connect(self.handle_model_settings)

		tool_menu.addAction(console_action)
		tool_menu.addAction(cs_setting_action)

	@staticmethod
	def create_console():
		def auto_scroller(text):
			cursor = config.CONSOLE.textCursor()
			cursor.movePosition(QTextCursor.End)
			cursor.insertText(text)

			config.CONSOLE.setTextCursor(cursor)
			config.CONSOLE.ensureCursorVisible()

		config.CONSOLE.setWindowTitle("Console Log")
		config.CONSOLE.setReadOnly(True)

		config.CONSOLE.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
		ConsoleLogger.stdout().messageWritten.connect(auto_scroller)
		ConsoleLogger.stderr().messageWritten.connect(auto_scroller)

	# handler for show/hide console output
	@staticmethod
	def _console_handler():
		if config.TOGGLE_CONSOLE:
			config.CONSOLE.close()
		else:
			config.CONSOLE.show()

	def handle_model_settings(self):
		def accept():
			try:
				# sanity check on input settings
				if end_time_value.value() <= gvars.HT[-2]:
					raise CustomError("End time must be greater than your second last time point!")
				else:
					gvars.HT[-1] = float(end_time_value.value())

				# update global time increment variable
				gvars.TIME_INC = float(dt_value.currentText())

				tmp = gvars.INIT_CELL
				if config.FILE_LOADED and not config.DATA_FREE and np.round(tmp) != init_cell_value.value():
					now = datetime.now().replace(microsecond=0)
					print("[{0}] Applying new initial cell number. Default was {1}.".format(now, gvars.INIT_CELL))
					config.CONSOLE.show()
					gvars.INIT_CELL = init_cell_value.value()
				elif config.FILE_LOADED and config.DATA_FREE:
					gvars.INIT_CELL = init_cell_value.value()
				else:
					gvars.INIT_CELL = init_cell_value.value()

				config.CYTON1_CONFIG['first_div'] = first_div.currentText()
				config.CYTON1_CONFIG['first_die'] = first_die.currentText()
				config.CYTON1_CONFIG['subsq_div'] = subsq_div.currentText()
				config.CYTON1_CONFIG['subsq_die'] = subsq_die.currentText()

				config.CYTON15_CONFIG['unstim_die'] = unstim_die.currentText()
				config.CYTON15_CONFIG['stim_div'] = stim_div.currentText()
				config.CYTON15_CONFIG['stim_die'] = stim_die.currentText()
				config.CYTON15_CONFIG['stim_dd'] = stim_dd.currentText()

				self.c1_plot.update_plot()
				self.c15_plot.update_plot()
			except CustomError as ce:
				now = datetime.now().replace(microsecond=0)
				print("[{0}] {1}".format(now, ce.message))
			finally:
				modal.close()

		def reject():
			modal.close()

		modal = QDialog()
		modal.setWindowTitle("Cyton Model Settings")
		modal_layout = QVBoxLayout()

		# create general settings section
		general_settings = QGroupBox("General Settings")
		general_settings_layout = QGridLayout()

		# add delta-t for discretisation of time array
		dt_label = QLabel("Time Increment (hrs):")
		dt_value = QComboBox()  # let user to choose from specified(allowed) time increment

		# check if file is loaded
		if config.FILE_LOADED:
			dt_value.clear()
			avail_dt_list = [1., .5, .25]
			tmp = [dt for dt in avail_dt_list if all(t % dt == 0 for t in gvars.HT)]  # only allow dt that also includes HTs
			dt_value.addItems([str(time_inc) for time_inc in tmp])
			dt_value.setCurrentText(str(gvars.TIME_INC))
		else:
			dt_value.addItems([str(1.), str(.5), str(.25)])  # finer the better but let's only give 3 options (in unit of hrs)

		init_cell_label = QLabel("Initial cell number:")
		init_cell_value = QDoubleSpinBox()
		init_cell_value.setDecimals(0)
		init_cell_value.setRange(0, np.inf)
		init_cell_value.setButtonSymbols(2)
		init_cell_value.setValue(gvars.INIT_CELL)

		begin_time_label = QLabel('Model begin time:')
		begin_time_value = QDoubleSpinBox()
		begin_time_value.setDecimals(0)
		begin_time_value.setButtonSymbols(2)
		begin_time_value.setValue(0)
		begin_time_value.setStyleSheet('color: rgb(105, 105, 105);')
		begin_time_value.setReadOnly(True)
		begin_time_value.setEnabled(False)

		end_time_label = QLabel("Model end time:")
		end_time_value = QDoubleSpinBox()
		end_time_value.setDecimals(0)
		end_time_value.setRange(0, np.inf)
		end_time_value.setButtonSymbols(2)
		end_time_value.setValue(gvars.HT[-1])

		# create Cyton 1 & Cyton 1.5 model settings (option to change PDFs)
		pdf_options = ['Gaussian', 'Lognormal']

		model_layout = QHBoxLayout()

		# Cyton 1
		c1_settings = QGroupBox("Cyton 1 : Distributions")
		c1_settings_layout = QGridLayout()

		first_div = QComboBox()
		first_div.addItems(pdf_options)
		first_div.setCurrentText(config.CYTON1_CONFIG['first_div'])

		first_die = QComboBox()
		first_die.addItems(pdf_options)
		first_die.setCurrentText(config.CYTON1_CONFIG['first_die'])

		subsq_div = QComboBox()
		subsq_div.addItems(pdf_options)
		subsq_div.setCurrentText(config.CYTON1_CONFIG['subsq_div'])

		subsq_die = QComboBox()
		subsq_die.addItems(pdf_options)
		subsq_die.setCurrentText(config.CYTON1_CONFIG['subsq_die'])

		# Cyton 1.5
		c15_settings = QGroupBox("Cyton 1.5 : Distributions")
		c15_settings_layout = QGridLayout()

		unstim_die = QComboBox()
		unstim_die.addItems(pdf_options)
		unstim_die.setCurrentText(config.CYTON15_CONFIG['unstim_die'])

		stim_div = QComboBox()
		stim_div.addItems(pdf_options)
		stim_div.setCurrentText(config.CYTON15_CONFIG['stim_div'])

		stim_die = QComboBox()
		stim_die.addItems(pdf_options)
		stim_die.setCurrentText(config.CYTON15_CONFIG['stim_die'])

		stim_dd = QComboBox()
		stim_dd.addItems(pdf_options)
		stim_dd.setCurrentText(config.CYTON15_CONFIG['stim_dd'])

		# add all widgets defined above
		general_settings_layout.addWidget(dt_label, 0, 0)
		general_settings_layout.addWidget(dt_value, 0, 1)
		general_settings_layout.addWidget(init_cell_label, 1, 0)
		general_settings_layout.addWidget(init_cell_value, 1, 1)
		general_settings_layout.addWidget(begin_time_label, 2, 0)
		general_settings_layout.addWidget(begin_time_value, 2, 1)
		general_settings_layout.addWidget(end_time_label, 3, 0)
		general_settings_layout.addWidget(end_time_value, 3, 1)
		general_settings.setLayout(general_settings_layout)
		modal_layout.addWidget(general_settings)

		c1_settings_layout.addWidget(QLabel("1st Div Proliferation:"), 0, 0)
		c1_settings_layout.addWidget(first_div, 0, 1)
		c1_settings_layout.addWidget(QLabel("1st Div Death:"), 1, 0)
		c1_settings_layout.addWidget(first_die, 1, 1)
		c1_settings_layout.addWidget(QLabel('Sub Div Proliferation:'), 2, 0)
		c1_settings_layout.addWidget(subsq_div, 2, 1)
		c1_settings_layout.addWidget(QLabel('Sub Div Death:'), 3, 0)
		c1_settings_layout.addWidget(subsq_die, 3, 1)
		c1_settings.setLayout(c1_settings_layout)
		model_layout.addWidget(c1_settings)

		c15_settings_layout.addWidget(QLabel("Unstimulated Death:"), 0, 0)
		c15_settings_layout.addWidget(unstim_die, 0, 1)
		c15_settings_layout.addWidget(QLabel("Stimulated Proliferation:"), 1, 0)
		c15_settings_layout.addWidget(stim_div, 1, 1)
		c15_settings_layout.addWidget(QLabel("Stimulated Death:"), 2, 0)
		c15_settings_layout.addWidget(stim_die, 2, 1)
		c15_settings_layout.addWidget(QLabel("Stimulated Division Destiny:"), 3, 0)
		c15_settings_layout.addWidget(stim_dd, 3, 1)
		c15_settings.setLayout(c15_settings_layout)
		model_layout.addWidget(c15_settings)

		modal_layout.addLayout(model_layout)
		modal.setLayout(modal_layout)

		# create buttons
		button = QDialogButtonBox(
			QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
			Qt.Horizontal, modal
		)
		button.accepted.connect(accept)
		button.rejected.connect(reject)
		modal_layout.addWidget(button)

		modal.setAttribute(Qt.WA_DeleteOnClose)  # make sure modal object is destroyed to free up memory
		modal.exec_()

	# handler for importing data
	def handle_import_data(self, re_init=False):
		try:
			# check for any existing data
			if not config.FILE_LOADED or re_init:
				# remember last import path otherwise set default to home folder
				if self.last_path is None:
					default_path = os.path.expanduser('~')
				else:
					default_path = self.last_path

				# construct file select dialog
				options = QFileDialog.Options()
				options |= QFileDialog.DontUseNativeDialog  # use PyQt5 style (faster)
				file, _ = QFileDialog.getOpenFileName(
					caption="Import Data",
					directory=default_path,
					filter="Excel Files (*.xlsx);; All files(*.*)",
					options=options
				)

				# no file selected
				if len(file) == 0:
					pass
				else:
					# split file name and extension for further check
					file_path, file_ext = os.path.splitext(file)
					file_name = os.path.splitext(os.path.basename(file))[0]
					# Openpyxl can only accept 'xlsx' file NOT 'csv'
					if file_ext == '.xlsx':
						# up to this point file's accepted!

						# process input file
						data_reader = ReadData(file)

						# invoke reinitialisation protocol for importing other data file
						if re_init:
							# check if user imported same exact file
							if config.FULL_FILE_PATH == file:
								raise CustomError("You are importing the same file.", loc='reimport')
							elif config.DATA_FREE:
								raise CustomError("Please exit Data Free mode to import new data file!")
							else:
								# remove legends from previous dataset
								self.c1_plot.c1_livecell_legends.removeItem(
									'data: {0}'.format(gvars.CONDITIONS[gvars.C1_ICND])
								)
								self.c15_plot.c15_livecell_legends.removeItem(
									'data: {0}'.format(gvars.CONDITIONS[gvars.C15_ICND])
								)

								# temporarily disconnect condition selector so that it won't update plots multiple times
								self.cyton1_buttons.data_select.disconnect()
								self.cyton15_buttons.data_select.disconnect()

								# reset variables
								reset_global_vars(gvars=gvars)

						# save processed data to global variables
						gvars.EXP_HT = data_reader.harvested_times
						gvars.EXP_HT_REPS = data_reader.harvested_times_reps
						gvars.MAX_DIV_PER_CONDITIONS = data_reader.generation_per_condition
						gvars.CONDITIONS = data_reader.condition_names
						gvars.EXP_NUM_TP = data_reader.num_time_points

						# compute total cell number. returns a tuple (average, replicate, SEM)
						gvars.TOTAL_CELLS, gvars.TOTAL_CELLS_REPS, gvars.TOTAL_CELLS_SEM = compute_total_cells(
							data_reader.data,
							data_reader.condition_names,
							data_reader.num_time_points,
							data_reader.generation_per_condition
						)

						gvars.CELL_GENS, gvars.CELL_GENS_REPS, gvars.CELL_GENS_SEM = sort_cell_generations(
							data_reader.data,
							data_reader.condition_names,
							data_reader.num_time_points,
							data_reader.generation_per_condition
						)

						# create a check matrix that has exactly same dimension & size of original data matrix
						gvars.C1_CHECK = create_check_matrix(copy.deepcopy(gvars.CELL_GENS_REPS))
						gvars.C15_CHECK = create_check_matrix(copy.deepcopy(gvars.CELL_GENS_REPS))

						# save file paths for export files later
						config.FULL_FILE_PATH = file
						config.FILE_PATH = os.path.dirname(file) + '/'
						config.FILE_NAME = file_name
						self.last_path = config.FILE_PATH

						# update program status variables
						config.FILE_LOADED = True
						config.DATA_FREE = False

						# self.c15_plot.re_initialise()
						self.update_ui()

						# dereference ReadData object
						del data_reader

						now = datetime.now().replace(microsecond=0)
						print("[{0}] Successfully imported {1}".format(now, file_name + file_ext))

						self.setWindowTitle('CytonSolver v{0} [{1}{2}]'.format(version, file_name, file_ext))
						config.CONSOLE.setWindowTitle('Console Log [{0}{1}]'.format(file_name, file_ext))
						config.CONSOLE.show()
					else:
						# error for non-xlsx files
						config.CONSOLE.show()
						raise CustomError("Choose xlsx files!", loc='import')
			else:
				# warn the user about data existence and bring up new file dialog to import and overwrite
				msg = QMessageBox()
				button_reply = msg.question(
					msg,
					'Import Data',
					'You have already imported a data file. \n'
					'Would you like to open a new file? \n\n'
					'This will overwrite current working space.'
				)
				if button_reply == QMessageBox.Yes:
					self.handle_import_data(re_init=True)
				else:
					pass
		except CustomError as ce:
			now = datetime.now().replace(microsecond=0)
			print("[{0}] {1}".format(now, ce.message))
		except IndexError as ie:
			print("[INDEX ERROR] {0}".format(ie))
		except ArithmeticError as ae:
			print("[ARITHMETIC ERROR] {0}".format(ae))
		except Exception as e:
			print("[ERROR] {0}".format(e))

	def update_ui(self):
		# compute possible dt from the list -> choose the fastest possible case
		dt_list = [1., .5, .25]
		for dt in dt_list:
			if all(t % dt == 0 for t in gvars.EXP_HT[gvars.C15_ICND]):
				gvars.TIME_INC = dt
				break

		# define data selector object (declared in tab_manager.py within button_manager object) and its functions
		self.cyton1_buttons.data_select.clear()
		self.cyton1_buttons.data_select.setEnabled(True)
		self.cyton1_buttons.data_select.setObjectName('cyton1_data_selector')
		self.cyton1_buttons.data_select.currentIndexChanged.connect(self.handle_data_select)

		self.cyton15_buttons.data_select.clear()
		self.cyton15_buttons.data_select.setEnabled(True)
		self.cyton15_buttons.data_select.setObjectName('cyton1.5_data_selector')
		self.cyton15_buttons.data_select.currentIndexChanged.connect(self.handle_data_select)

		# populate drop down menu with condition names
		for cond in gvars.CONDITIONS:
			self.cyton1_buttons.data_select.addItem(str(cond))
			self.cyton15_buttons.data_select.addItem(str(cond))
		self.cyton1_buttons.data_select.addItem(str("Data Free"))
		self.cyton15_buttons.data_select.addItem(str("Data Free"))

		# set default condition
		gvars.C1_ICND = self.cyton1_buttons.data_select.currentIndex()
		gvars.C15_ICND = self.cyton15_buttons.data_select.currentIndex()

		# enable data exclude/include button
		self.cyton1_buttons.data_manager.setEnabled(True)
		self.cyton15_buttons.data_manager.setEnabled(True)

	def handle_data_select(self):
		try:
			sender = self.sender().objectName()
			if sender == 'cyton1_data_selector':
				# TODO: make sure to fix this part when data free mode is implemented
				gvars.C1_ICND = self.cyton1_buttons.data_select.currentIndex()
				gvars.HT = gvars.EXP_HT[gvars.C1_ICND].copy()
				gvars.MAX_DIV = gvars.MAX_DIV_PER_CONDITIONS[gvars.C1_ICND]
				gvars.INIT_CELL = gvars.TOTAL_CELLS[gvars.C1_ICND][0]

				self.c1_plot.re_initialise()
				# self.c1_plot.update_plot()
			elif sender == 'cyton1.5_data_selector':
				gvars.C15_ICND = self.cyton15_buttons.data_select.currentIndex()
				if gvars.C15_ICND == len(gvars.CONDITIONS):
					# initiate data free mode method
					config.DATA_FREE = True
					self.c15_plot.data_free_mode()
				else:
					gvars.HT = gvars.EXP_HT[gvars.C15_ICND].copy()
					gvars.MAX_DIV = gvars.MAX_DIV_PER_CONDITIONS[gvars.C15_ICND]
					gvars.INIT_CELL = gvars.TOTAL_CELLS[gvars.C15_ICND][0]

					config.DATA_FREE = False

					self.c15_plot.re_initialise()
					# self.c15_plot.update_plot()
		except CustomError as ce:
			now = datetime.now().replace(microsecond=0)
			print("[{0}] {1}".format(now, ce.message))
		except Exception as e:
			print("[ERROR] {0}".format(e))


# This is a dummy initialisation function for splash screen
def init(arg):
	time.sleep(arg)
	return 0


# MAIN ENTRY POINT - INITIALISE THE ENTIRE PROGRAM
if __name__ == '__main__':
	logging.basicConfig()
	logger = logging.getLogger(__name__)

	cs_app = QApplication(sys.argv)

	# create and display the splash screen
	splash = SplashScreen()
	splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)  # put splash screen on top
	splash.show()

	# this event loop is needed for dispatching Qt events
	init_loop = QEventLoop()
	pool = Pool()
	pool.apply_async(init, [2], callback=lambda exit_code: init_loop.exit(exit_code))
	init_loop.exec_()

	# Fusion dark theme - ref 'https://gist.github.com/gph03n1x/7281135'
	cs_app.setStyle('Fusion')
	palette = QPalette()
	palette.setColor(QPalette.Window, QColor(53, 53, 53))
	palette.setColor(QPalette.WindowText, Qt.white)
	palette.setColor(QPalette.Base, QColor(15, 15, 15))
	palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
	palette.setColor(QPalette.ToolTipBase, Qt.black)
	palette.setColor(QPalette.ToolTipText, Qt.white)
	palette.setColor(QPalette.Text, Qt.white)
	palette.setColor(QPalette.Button, QColor(53, 53, 53))
	palette.setColor(QPalette.ButtonText, Qt.white)
	palette.setColor(QPalette.BrightText, Qt.red)

	palette.setColor(QPalette.Highlight, QColor(153, 0, 0).lighter())
	palette.setColor(QPalette.HighlightedText, Qt.black)
	cs_app.setPalette(palette)

	# get system resolution
	screen_resolution = cs_app.desktop().screenGeometry()
	width, height = screen_resolution.width(), screen_resolution.height()

	ex = MainCytonSolver()  # initialise Cyton Solver object
	ex.show()
	splash.finish(ex)

	sys.exit(cs_app.exec())
