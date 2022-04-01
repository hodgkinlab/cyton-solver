import numpy as np
import seaborn as sns
import pyqtgraph as pg
from PyQt5.QtCore import Qt

import src.common.settings as config
import src.common.global_vars as gvars
from src.plot.update import UpdatePDF, UpdateModelCurve


class C1Canvas(UpdatePDF, UpdateModelCurve):
	def __init__(self):
		super().__init__()

		# set general pyqtgraph settings

		# uncomment this for default PyQt5 style
		# pg.setConfigOption('background', 'w')
		# pg.setConfigOption('foreground', 'k')
		pg.setConfigOption('foreground', 'w')
		pg.setConfigOption('leftButtonPan', False)
		pg.setConfigOptions(antialias=True)

		self._init_cyton1_plots()

	@staticmethod
	def remove_plot_item(view, item):
		view.removeItem(item)

	@staticmethod
	def remove_all_plots(view, layout):
		layout.clear()
		view.setCentralItem(None)

	def _init_cyton1_plots(self):
		self.update_cyton1_pdf()
		self.update_cyton1_model()

		# print(self.c1_total_cells)
		# print(len(self.c1_total_cells[1]))
		# probability distribution plot
		self.c1_pdfs = pg.GraphicsView()  # add this component as QWidget

		# prepare for layout - plot item manager
		self.c1_pdfs_layout = pg.GraphicsLayout(border=(0, 0, 0, 0))  # remove curves from this if needed
		self.c1_pdfs.setCentralItem(self.c1_pdfs_layout)  # set the layout as a central item to display
		self.c1_pdfs_in_plot = self.c1_pdfs_layout.addPlot(title='Cyton1: Probability Distribution')
		# self.c1_pdfs_in_plot.showGrid(True, True, 0.5)
		self.c1_pdfs_in_plot.setLabel('bottom', 'time (hrs)')
		self.c1_pdfs_in_plot.getViewBox().setLimits(yMin=-1.0, yMax=1.0)

		# following lines defines 4 unique distribution curves. Update these curves directly (setData method)
		self.c1_div = self.c1_pdfs_in_plot.plot(
			x=self.t,
			y=self.undividedDiv,
			fillLevel=0.0, brush=(0, 0, 255, 100),
			pen=pg.mkPen((0, 0, 255), width=1.5)
		)
		self.c1_die = self.c1_pdfs_in_plot.plot(
			x=self.t,
			y=self.undividedDeath,
			fillLevel=0.0, brush=(255, 0, 0, 100),
			pen=pg.mkPen((255, 0, 0), width=1.5)
		)
		self.c1_sub_div = self.c1_pdfs_in_plot.plot(
			x=self.t,
			y=self.dividedDiv,
			fillLevel=0.0, brush=(35, 107, 142, 100),
			pen=pg.mkPen((35, 107, 142), width=1.5, style=Qt.DashLine)
		)
		self.c1_sub_die = self.c1_pdfs_in_plot.plot(
			x=self.t,
			y=self.dividedDeath,
			fillLevel=0.0, brush=(255, 127, 0, 100),
			pen=pg.mkPen((255, 127, 0), width=1.5, style=Qt.DashLine)
		)
		# add legends for pdfs
		self.c1_pdf_legends = pg.LegendItem()
		self.c1_pdf_legends.setParentItem(self.c1_pdfs_in_plot)
		self.c1_pdf_legends.addItem(self.c1_div, 'First Division')
		self.c1_pdf_legends.addItem(self.c1_die, 'First Death')
		self.c1_pdf_legends.addItem(self.c1_sub_div, 'Subsequent Division')
		self.c1_pdf_legends.addItem(self.c1_sub_die, 'Subsequent Death')
		self.c1_pdf_legends.anchor(itemPos=(0.0, 0.0), parentPos=(1.0, 0.0), offset=(-160, 0))

		#####  Total live cell vs. Time plot - 1. model curve 2. model points at HT (correspond to input data) 3. data curve 4. data points at HT

		# define cyton 1 model Qt view box
		self.c1_livecell = pg.GraphicsView()  # add this component as QWidget

		self.c1_livecell_layout = pg.GraphicsLayout(border=(0, 0, 0, 0))
		self.c1_livecell.setCentralItem(self.c1_livecell_layout)
		self.c1_livecell_in_plot = self.c1_livecell_layout.addPlot(title='Evolution of Total Live Cells')
		# self.c1_livecell_in_plot.showGrid(True, True, 0.5)
		# x, y axis labels
		self.c1_livecell_in_plot.setLabel('left', 'Number of cells')
		self.c1_livecell_in_plot.setLabel('bottom', 'time (hrs)')

		self.c1_livecell_curve = self.c1_livecell_in_plot.plot(
			x=self.model_time,
			y=self.c1_total_cells[0],
			# pen=(0, 0, 0) # uncomment this for default PyQt5 styles
		)
		self.c1_livecell_ht_points = self.c1_livecell_in_plot.plot(
			x=gvars.HT,
			y=self.c1_total_cells[1],
			pen=None, symbol='o', symbolPen=None, symbolSize=7, symbolBrush=(200, 64, 0)
		)
		# add legends to the curves and model points
		self.c1_livecell_legends = pg.LegendItem()
		self.c1_livecell_legends.setParentItem(self.c1_livecell_in_plot)
		self.c1_livecell_legends.addItem(self.c1_livecell_curve, 'model')
		self.c1_livecell_legends.addItem(self.c1_livecell_ht_points, 'HT')
		self.c1_livecell_legends.anchor(itemPos=(0.0, 0.0), parentPos=(1.0, 0.0), offset=(-80, 0))

		# initialise an empty data plot for later
		self.c1_livecell_data = pg.ErrorBarItem(
			x=[], y=[], beam=1.0, pen=(119, 172, 48)
		)
		self.c1_livecell_data_curve = self.c1_livecell_in_plot.plot(
			x=[],
			y=[],
			symbolSize=5,
			symbolBrush=(119, 172, 48),
			pen=(119, 172, 48)
		)
		self.c1_livecell_in_plot.addItem(self.c1_livecell_data)
		# fill between data and model to emphasize difference
		# _c1_fill_bw_model_data = pg.FillBetweenItem(
		# 	# self.c1_livecell_curve, self.c1_livecell_data_curve, brush=(0, 255, 0, 10)
		# 	self.c1_livecell_curve, self.c1_livecell_data_curve, brush=(255, 255, 255, 50)
		# )
		# self.c1_livecell_in_plot.addItem(_c1_fill_bw_model_data)

		# define seaborn color_palette
		sns_color_palette = sns.hls_palette(gvars.MAX_DIV+1, l=.4, s=.5)
		# pyqtgraph requires 3digit rgb values unlike [0, 1] in matplotlib/seaborn
		converted_color_palette = []
		for i, cp in enumerate(sns_color_palette):
			tmp = []
			for j, item in enumerate(cp):
				tmp.append(item * 255.)
			tmp.append(100)  # transparency in percentage
			converted_color_palette.append(tmp)

		self.fill_bw_cell_per_gen_objects = []
		for igen in range(gvars.MAX_DIV+1):
			_c1_fill_bw_cell_per_gen = self.c1_livecell_in_plot.plot(
				x=self.model_time,
				y=self.c1_total_cells[3][igen],
				fillLevel=0.0, brush=converted_color_palette[igen],
				pen=pg.mkPen(converted_color_palette[igen], width=1.5)
			)
			self.fill_bw_cell_per_gen_objects.append(_c1_fill_bw_cell_per_gen)

		#####  Cell number vs. Generation plot for all harvested time points
		self.c1_cellgen = pg.GraphicsView()

		self.c1_cellgen_layout = pg.GraphicsLayout(border=(0, 0, 0, 0))
		self.c1_cellgen.setCentralItem(self.c1_cellgen_layout)
		self.c1_cellgen_layout.addLabel("Live Cells vs. Generations at HT", col=0, colspan=4)
		self.c1_cellgen_layout.nextRow()

		# store all plot objects & curves in itpt orders
		gens = [i for i in range(gvars.MAX_DIV+1)]
		self.c1_cellgen_plot_objects = []
		self.c1_cellgen_model_curves = []
		row, col = 1, 1

		#### problem is that GV.harvested_time_default potentially changes its dimension depending on the condition in the data.
		#### When it initiated with longest GV.harvested_time_default amongst other conditions, they pose no problem but in this case order of initialisation matters. Should the program booted with shorter one, it crashes when a user switched to more HT condition. There are potentially two possible solutions:
		####        1. Remove and redraw everytime user swithces to different condition - might be cleaner option but it could potentially slows down loading other condition
		####        2. Find the longest HT array in the data and initialise with that - this removes possible duplicate code of removing and redrawing section, but it can be really confusing for future maintenance/upgrade.

		for itpt, ht in enumerate(gvars.HT):
			c1_cellgen_in_plot = self.c1_cellgen_layout.addPlot(
				title='time at %s' % ht,
				x=gens,
				row=row, col=col
			)
			# c1_cellgen_in_plot.showGrid(True, True, 0.5)
			c1_cellgen_curve = c1_cellgen_in_plot.plot(
				y=self.c1_total_cells[2][itpt],
				# pen=(0, 0, 0), # Note: uncomment this for default PyQt5 style
				symbolBrush=(200, 64, 0),
				symbolSize=7
			)
			self.c1_cellgen_plot_objects.append(c1_cellgen_in_plot)
			self.c1_cellgen_model_curves.append(c1_cellgen_curve)

			col += 1
			if (itpt + 1) % 3 == 0:
				self.c1_cellgen_layout.nextRow()
				row += 1
				col = 1
		self.c1_cellgen_layout.addLabel('Number of cells', angle=-90, col=0, row=1, rowspan=row + 1)
		self.c1_cellgen_layout.addLabel('Generations', col=1, colspan=4, row=row + 1)

	# thie method removes contents of the plot panel and reinitialise with correct number of HT
	# calls this function when 1.data is imported  2.user swtiched to different condition
	def re_initialise(self):
		self.update_cyton1_pdf()
		self.update_cyton1_model()

		# remove entire c1_cellgen view box and replot it with selected_data
		self.remove_all_plots(self.c1_cellgen, self.c1_cellgen_layout)
		del self.c1_cellgen_layout
		self.c1_cellgen_layout = pg.GraphicsLayout(border=(0, 0, 0, 0))

		self.c1_cellgen.setCentralItem(self.c1_cellgen_layout)

		# redefine/draw Cell number vs. Generation portion of the plot
		self.c1_cellgen_layout.addLabel("Live Cells vs. Generations at HT", row=0, col=0, colspan=4)
		self.c1_cellgen_layout.nextRow()

		self.c1_cellgen_plot_objects = []
		self.c1_cellgen_model_curves = []
		self.c1_cellgen_data = []
		self.c1_cellgen_data_curves = []
		gens = [i for i in range(gvars.MAX_DIV+1)]
		row, col = 1, 1
		for itpt, ht in enumerate(gvars.EXP_HT[gvars.C1_ICND]):
			c1_cellgen_in_plot = self.c1_cellgen_layout.addPlot(
				title='time at %s' % ht,
				x=gens,
				row=row, col=col
			)
			# c1_cellgen_in_plot.showGrid(True, True, 0.5)

			# disable mouse wheel zooming events
			c1_cellgen_in_plot.vb.setMouseEnabled(x=False, y=False)

			c1_cellgen_curve = c1_cellgen_in_plot.plot(
				y=self.c1_total_cells[2][itpt],
				# pen=(0, 0, 0), # Note: uncomment this for default PyQt5 style
				symbolBrush=(200, 64, 0),
				symbolSize=7
			)
			self.c1_cellgen_plot_objects.append(c1_cellgen_in_plot)
			self.c1_cellgen_model_curves.append(c1_cellgen_curve)

			data = pg.ErrorBarItem(
				x=np.asarray(gens),
				y=np.asarray(gvars.CELL_GENS[gvars.C1_ICND][itpt]),
				top=np.asarray(gvars.CELL_GENS_SEM[gvars.C1_ICND][itpt]),
				bottom=np.asarray(gvars.CELL_GENS_SEM[gvars.C1_ICND][itpt]),
				beam=0.15, pen=(119, 172, 48)
			)
			data_curve = c1_cellgen_in_plot.plot(
				y=gvars.CELL_GENS[gvars.C1_ICND][itpt],
				symbolSize=5, symbolBrush=(119, 172, 48), pen=(119, 172, 48)
			)
			self.c1_cellgen_data.append(data)
			self.c1_cellgen_data_curves.append(data_curve)

			c1_cellgen_in_plot.addItem(data)
			col += 1
			if (itpt + 1) % 3 == 0:
				self.c1_cellgen_layout.nextRow()
				row += 1
				col = 1
		self.c1_cellgen_layout.addLabel('Number of cells', angle=-90, col=0, row=1, rowspan=row + 1)
		self.c1_cellgen_layout.addLabel('Generations', col=1, colspan=4, row=row + 1)

		# if there are too many time points in the data, make scroll enabled
		if 9 < gvars.EXP_NUM_TP[gvars.C1_ICND] < 15:
			self.c1_cellgen.setFixedHeight(950)
		elif gvars.EXP_NUM_TP[gvars.C1_ICND] >= 15:
			self.c1_cellgen.setFixedHeight(1300)
		else:
			# TODO: revert to auto resizing
			pass

		# update pdfs
		self.c1_div.setData(x=self.t, y=self.undividedDiv)
		self.c1_die.setData(x=self.t, y=self.undividedDeath)
		self.c1_sub_div.setData(x=self.t, y=self.dividedDiv)
		self.c1_sub_die.setData(x=self.t, y=self.dividedDeath)

		# update cyton model
		self.c1_livecell_curve.setData(x=self.model_time, y=self.c1_total_cells[0])
		self.c1_livecell_ht_points.setData(x=gvars.EXP_HT[gvars.C1_ICND], y=self.c1_total_cells[1])

		# define seaborn color_palette
		sns_color_palette = sns.hls_palette(gvars.MAX_DIV+1, l=.4, s=.5)
		# pyqtgraph requires 3digit rgb values unlike [0, 1] in matplotlib/seaborn
		converted_color_palette = []
		for i, cp in enumerate(sns_color_palette):
			tmp = []
			for j, item in enumerate(cp):
				tmp.append(item * 255.)
			tmp.append(100)  # transparency in percentage
			converted_color_palette.append(tmp)

		self.fill_bw_cell_per_gen_objects = []
		for igen in range(gvars.MAX_DIV+1):
			_c1_fill_bw_cell_per_gen = self.c1_livecell_in_plot.plot(
				x=self.model_time,
				y=self.c1_total_cells[3][igen],
				fillLevel=0.0, brush=converted_color_palette[igen],
				pen=pg.mkPen(converted_color_palette[igen], width=1.5)
			)
			self.fill_bw_cell_per_gen_objects.append(_c1_fill_bw_cell_per_gen)

		# update data & data_curve
		self.c1_livecell_data.setData(
			x=np.asarray(gvars.EXP_HT[gvars.C1_ICND]),
			y=np.asarray(gvars.TOTAL_CELLS[gvars.C1_ICND]),
			top=np.asarray(gvars.TOTAL_CELLS_SEM[gvars.C1_ICND]),
			bottom=np.asarray(gvars.TOTAL_CELLS_SEM[gvars.C1_ICND])
		)
		self.c1_livecell_data_curve.setData(
			x=gvars.EXP_HT[gvars.C1_ICND],
			y=gvars.TOTAL_CELLS[gvars.C1_ICND]
		)

		# regenerate legends corresponding to condition name
		for condition in gvars.CONDITIONS:
			self.c1_livecell_legends.removeItem('data: %s' % condition)
		# redundantly removing and adding 'model' legend but this is only way to make legen box size minimal...
		self.c1_livecell_legends.removeItem('model')
		self.c1_livecell_legends.addItem(self.c1_livecell_curve, 'model')
		self.c1_livecell_legends.removeItem('HT')
		self.c1_livecell_legends.addItem(data_curve, 'data: %s' % gvars.CONDITIONS[gvars.C1_ICND])
		self.c1_livecell_legends.anchor(itemPos=(0.0, 0.0), parentPos=(0.72, 0.0))
		self.c1_livecell_legends.updateSize()

	def update_plot(self):
		# recalculate pdf
		self.update_cyton1_pdf()
		# recalculate model
		self.update_cyton1_model()

		# update pdfs
		self.c1_div.setData(x=self.t, y=self.undividedDiv)
		self.c1_die.setData(x=self.t, y=self.undividedDeath)
		self.c1_sub_div.setData(x=self.t, y=self.dividedDiv)
		self.c1_sub_die.setData(x=self.t, y=self.dividedDeath)

		# update cyton model
		self.c1_livecell_curve.setData(x=self.model_time, y=self.c1_total_cells[0])
		if config.FILE_LOADED and not config.DATA_FREE:
			self.c1_livecell_ht_points.setData(x=gvars.EXP_HT[gvars.C1_ICND], y=self.c1_total_cells[1])
		else:
			self.c1_livecell_ht_points.setData(x=gvars.HT, y=self.c1_total_cells[1])

		# update filled cell number per gen
		for igen in range(gvars.MAX_DIV + 1):
			self.fill_bw_cell_per_gen_objects[igen].setData(x=self.model_time, y=self.c1_total_cells[3][igen])

		# update cellgen
		for itpt in range(len(self.c1_cellgen_plot_objects)):
			if config.FILE_LOADED and not config.DATA_FREE:
				self.c1_cellgen_plot_objects[itpt].setTitle(title="time at %s" % gvars.EXP_HT[gvars.C1_ICND][itpt])
			else:
				self.c1_cellgen_plot_objects[itpt].setTitle(title="time at %s" % gvars.HT[itpt])
			self.c1_cellgen_model_curves[itpt].setData(self.c1_total_cells[2][itpt])

		if config.FILE_LOADED:
			# check for excluded data set
			for itpt, l in enumerate(gvars.C1_CHECK[gvars.C1_ICND]):
				total = 0  # check total number of data : irep + igen
				check = 0  # check number of excluded data points
				for irep, sl in enumerate(l):
					for igen in range(len(sl)):
						total += 1
						check += gvars.C1_CHECK[gvars.C1_ICND][itpt][irep][igen]

				# if all data are excluded for that particular time point, color them as red
				#   NOTE : we know exactly which data are excluded,
				# 		   but pyqtgraph doesn't provide any method to change color of single data point
				# TODO: override this method to change color to specific data point
				# TODO: it's also good to recalculate error range with EXCLUDED data points and update accordingly
				if not check:
					self.c1_cellgen_data[itpt].setData(pen=(255, 0, 0))
					self.c1_cellgen_data_curves[itpt].setPen((255, 0, 0))
					self.c1_cellgen_data_curves[itpt].setSymbolBrush((255, 0, 0))
				# if any of replicates is excluded, color them as yellow
				elif 0 < check < total:
					self.c1_cellgen_data[itpt].setData(pen=(255, 255, 0))
					self.c1_cellgen_data_curves[itpt].setPen((255, 255, 0))
					self.c1_cellgen_data_curves[itpt].setSymbolBrush((255, 255, 0))
				elif check == total:
					self.c1_cellgen_data[itpt].setData(pen=(119, 172, 48))
					self.c1_cellgen_data_curves[itpt].setPen((119, 172, 48))
					self.c1_cellgen_data_curves[itpt].setSymbolBrush((119, 172, 48))

	def data_free_mode(self):
		pass