from PyQt5.Qt import pyqtSignal
from PyQt5.QtWidgets import QWidget

import src.common.global_vars as gvars


class C1EventHandler(QWidget):

	param_changed = pyqtSignal(dict)

	def __init__(self):
		super(QWidget, self).__init__()

	def handle_param_value_changed(self, val):
		gvars.C1_PARAMS[self.sender().objectName()] = val
		self.param_changed.emit(gvars.C1_PARAMS)

	def handle_lock_button_state(self, lock):
		if lock.isChecked():
			gvars.C1_VARY_PARAMS[self.sender().objectName()] = False
		else:
			gvars.C1_VARY_PARAMS[self.sender().objectName()] = True

	def handle_double_slider(self, param):
		param.setValue(self.sender().value())

	def handle_upper_bound_changed(self, val):
		gvars.C1_UPPER_BOUNDS[self.sender().objectName()] = val


class C15EventHandler(QWidget):

	param_changed15 = pyqtSignal(dict)

	def __init__(self):
		super(QWidget, self).__init__()

	def handle_param_value_changed(self, val):
		gvars.C15_PARAMS[self.sender().objectName()] = val
		self.param_changed15.emit(gvars.C15_PARAMS)

	def handle_lock_button_state(self, lock):
		if lock.isChecked():
			gvars.C15_VARY_PARAMS[self.sender().objectName()] = False
		else:
			gvars.C15_VARY_PARAMS[self.sender().objectName()] = True

	def handle_double_slider(self, param):
		param.setValue(self.sender().value())

	def handle_upper_bound_changed(self, val):
		gvars.C15_UPPER_BOUNDS[self.sender().objectName()] = val
