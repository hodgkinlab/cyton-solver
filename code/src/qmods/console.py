from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPlainTextEdit

import src.common.settings as config


class Console(QPlainTextEdit):
	def closeEvent(self, event):
		config.TOGGLE_CONSOLE = False

	def showEvent(self, event):
		config.TOGGLE_CONSOLE = True

	def keyPressEvent(self, event):
		k = event.key()
		kmod = event.modifiers()
		if k == Qt.Key_Escape or ((kmod & Qt.ControlModifier) and k == Qt.Key_C):
			self.close()