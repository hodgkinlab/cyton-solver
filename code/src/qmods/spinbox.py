import psutil
from PyQt5.QtWidgets import QSpinBox

NC = psutil.cpu_count(logical=True)


class SpinBox(QSpinBox):

	def __init__(self, parent=None):
		super(SpinBox, self).__init__(parent=parent)

		self.setKeyboardTracking(False)
		self.valueChanged.connect(self.onValueChanged)
		self.before_value = self.value()

	def onValueChanged(self, new_value):
		if not self.isValid(new_value):
			self.setValue(self.before_value)
		else:
			self.before_value = new_value

	def isValid(self, value):
		if value % NC == 0:
			return True
		return False
