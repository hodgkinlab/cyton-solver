"""class CustomError

inherit Python built-in Exception class
This module handles errors at various pre-defined 'location' before raising exception.
"""

from PyQt5.QtWidgets import QMessageBox


class CustomError(Exception):
	def __init__(self, message, loc="unknown"):
		self.message = message
		self.loc = loc

		msg = QMessageBox()
		msg.setIcon(QMessageBox.Critical)
		msg.setInformativeText(self.message)
		if loc == 'import':
			msg.setText("Import Error")
			msg.setWindowTitle("Error")
		elif loc == 'reimport':
			msg.setIcon(QMessageBox.Warning)
			msg.setText("Identical File")
			msg.setWindowTitle("Warning")
		elif loc == 'fit':
			msg.setText("No data to fit")
			msg.setWindowTitle("Error")
		elif loc == 'data_manager':
			msg.setText("No data error")
			msg.setWindowTitle("Error")
		# elif loc == 'PLOT':
		#     msg = QMessageBox()
		#     msg.setIcon(QMessageBox.Critical)
		#     msg.setText("No data error")
		#     msg.setInformativeText(self.message)
		#     msg.setWindowTitle("Error")
		#     msg.exec_()
		# elif loc == 'CohortAnalysis':
		#     msg = QMessageBox()
		#     msg.setIcon(QMessageBox.Critical)
		#     msg.setText("No data error")
		#     msg.setInformativeText(self.message)
		#     msg.setWindowTitle("Error")
		#     msg.exec_()
		elif loc == 'fitting':
			msg.setText("No model selected error")
			msg.setWindowTitle("Error")
		elif loc == 'load_params':
			msg.setText("No data error")
			msg.setWindowTitle("Error")
		elif loc == 'compare_data':
			msg.setText("No data error")
			msg.setWindowTitle("Error")
		elif loc == 'compare_data_no_file':
			msg.setText("No saved parameters found")
			msg.setWindowTitle("Error")
		msg.exec_()
