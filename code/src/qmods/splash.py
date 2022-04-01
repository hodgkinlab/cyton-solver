# 18-June-2018 : Modified QSplashScreen class
# take GIF image as an input and turn it into splash screen upon initialisation
import os
import sys

from PyQt5.Qt import Qt
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtWidgets import QSplashScreen

# LOADING_SCREEN = 'img/splash_images/c1.gif'
# LOADING_SCREEN = 'img/splash_images/mito.gif'
# LOADING_SCREEN = 'img/splash_images/metaloader2.gif'
# LOADING_SCREEN = 'img/splash_images/awesome.gif'
LOADING_SCREEN = 'img/splash_images/load3.gif'
# LOADING_SCREEN = 'img/splash_images/geometry.gif'


class SplashScreen(QSplashScreen):
	def __init__(self):
		animation = self.resource_path(LOADING_SCREEN)
		flags = Qt.WindowStaysOnTopHint
		# run event dispatching in another thread
		QSplashScreen.__init__(self, QPixmap(), flags)
		self.movie = QMovie(animation)
		self.movie.frameChanged.connect(self.on_next_frame)
		self.movie.start()

	def on_next_frame(self):
		pixmap = self.movie.currentPixmap()
		self.setPixmap(pixmap)
		self.setMask(pixmap.mask())

	# this is a copy of exact function inside MainCytonSolver class
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
