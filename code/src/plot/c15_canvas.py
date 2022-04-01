import numpy as np
import seaborn as sns
import pyqtgraph as pg
from PyQt5.QtCore import Qt

import src.common.settings as config
import src.common.global_vars as gvars
from src.plot.update import UpdatePDF, UpdateModelCurve


class C15Canvas(UpdatePDF, UpdateModelCurve):
	def __init__(self):
		super().__init__()

		# set general pyqtgraph settings

		# uncomment this for default PyQt5 style
		# pg.setConfigOption('background', 'w')
		# pg.setConfigOption('foreground', 'k')
		pg.setConfigOption('foreground', 'w')
		pg.setConfigOption('leftButtonPan', False)
		pg.setConfigOptions(antialias=True)

		self._init_cyton15_plots()

	@staticmethod
	def remove_plot_item(view, item):
		view.removeItem(item)

	@staticmethod
	def remove_all_plots(view, layout):
		layout.clear()
		view.setCentralItem(None)

	def _init_cyton15_plots(self):
		self.update_cyton15_pdf()
		self.update_cyton15_model()

		"""Probability distribution plot"""
		self.c15_pdfs = pg.GraphicsView()

		self.c15_pdfs_layout = pg.GraphicsLayout(border=(0, 0, 0, 0))
		self.c15_pdfs.setCentralItem(self.c15_pdfs_layout)

		self.c15_pdfs_in_plot = self.c15_pdfs_layout.addPlot(title='Cyton1.5: Probability Distribution')
		# self.c15_pdfs_in_plot.showGrid(True, True, 0.5)
		self.c15_pdfs_in_plot.setLabel('bottom', 'time (hrs)')
		self.c15_pdfs_in_plot.getViewBox().setLimits(yMin=-1.0, yMax=1.0)  # set min/max visible range

		self.c15_unstim_die = self.c15_pdfs_in_plot.plot(
			x=self.t,
			y=self.unstimDeath,
			fillLevel=0.0, brush=(255, 127, 0, 100),
			pen=pg.mkPen((255, 127, 0), width=1.5, style=Qt.DashLine)
		)
		self.c15_tfd = self.c15_pdfs_in_plot.plot(
			x=self.t,
			y=self.stimDiv,
			fillLevel=0.0, brush=(0, 0, 255, 100),
			pen=pg.mkPen((0, 0, 255), width=1.5)
		)
		self.c15_die = self.c15_pdfs_in_plot.plot(
			x=self.t,
			y=self.stimDeath,
			fillLevel=0.0, brush=(255, 0, 0, 100),
			pen=pg.mkPen((255, 0, 0), width=1.5)
		)
		self.c15_dd = self.c15_pdfs_in_plot.plot(
			x=self.t,
			y=self.stimDD,
			fillLevel=0.0, brush=(0, 153, 0, 100),
			pen=pg.mkPen((0, 153, 0), width=1.5)
		)

		# add an infinite line for indicating division 2
		self.c15_b = pg.InfiniteLine(
			pos=gvars.C15_PARAMS['stimMuDiv'] + gvars.C15_PARAMS['SubDivTime'],
			label='b (Sub. Div.)', labelOpts={'movable': True, 'position': 0.95},
			pen=pg.mkPen((135, 206, 255), style=Qt.DashLine),
		)
		self.c15_pdfs_in_plot.addItem(self.c15_b)

		# self.b_lines = []
		# for igen in range(1, gvars.MAX_DIV+1):
		# 	pos = 0.6+0.35*(igen)/(gvars.MAX_DIV+1)
		# 	b = pg.InfiniteLine(
		# 		pos=gvars.C15_PARAMS['stimMuDiv']+igen*gvars.C15_PARAMS['SubDivTime'],  # div2 = median_div + b
		# 		label='div {0}'.format(igen+1), labelOpts={'movable': True, 'position': pos},
		# 		pen=pg.mkPen((135/(igen+1), 206/(igen+1), 255/(igen+1)), style=Qt.DashLine)
		# 	)
		# 	self.c15_pdfs_in_plot.addItem(b)
		# 	self.b_lines.append(b)
		self.c15_pdf_legends = pg.LegendItem()
		self.c15_pdf_legends.setParentItem(self.c15_pdfs_in_plot)
		self.c15_pdf_legends.addItem(self.c15_unstim_die, 'Unstimulated Death')
		self.c15_pdf_legends.addItem(self.c15_tfd, 'Stimulated Division')
		self.c15_pdf_legends.addItem(self.c15_die, 'Stimulated Death')
		self.c15_pdf_legends.addItem(self.c15_dd, 'Stimulated Destiny')
		self.c15_pdf_legends.anchor(itemPos=(0.0, 0.0), parentPos=(1.0, 0.0), offset=(-160, 0))

		"""Total live cell vs. Time plot"""
		self.c15_livecell = pg.GraphicsView()

		self.c15_livecell_layout = pg.GraphicsLayout(border=(0, 0, 0, 0))
		self.c15_livecell.setCentralItem(self.c15_livecell_layout)
		self.c15_livecell_in_plot = self.c15_livecell_layout.addPlot(title='Evolution of Total Live Cells')
		# self.c15_livecell_in_plot.showGrid(True, True, 0.5)

		self.c15_livecell_in_plot.setLabel('left', 'Number of cells')
		self.c15_livecell_in_plot.setLabel('bottom', 'time (hrs)')
		self.c15_livecell_curve = self.c15_livecell_in_plot.plot(
			x=self.model_time,
			y=self.c15_total_cells[1][0],
			# pen=(0, 0, 0) # Note: uncomment this for default PyQt5 style
		)
		self.c15_livecell_ht_points = self.c15_livecell_in_plot.plot(
			x=gvars.HT,
			y=self.c15_total_cells[0][0],
			pen=None, symbol='o', symbolPen=None, symbolSize=7, symbolBrush=(200, 64, 0)
		)
		# compute for cumulative live cells -> easy to visualise transition from dividing -> destiny
		# cumulative_dividing = np.zeros(shape=self.model_time.size)
		# cumulative_destiny = np.zeros(shape=self.model_time.size)
		# for j in range(self.model_time.size):
		# 	for igen in range(gvars.MAX_DIV+1):
		# 		cumulative_dividing[j] += self.c15_total_cells[1][2][igen, j]
		# 		cumulative_destiny[j] += self.c15_total_cells[1][3][igen, j]
		# self.c15_dividing = self.c15_livecell_in_plot.plot(
		# 	x=self.model_time,
		# 	y=cumulative_dividing,
		# 	pen=pg.mkPen(color=(99, 184, 255), style=Qt.DashLine, width=1.5)
		# )
		# self.c15_destiny = self.c15_livecell_in_plot.plot(
		# 	x=self.model_time,
		# 	y=cumulative_destiny,
		# 	pen=pg.mkPen(color=(0, 153, 0), style=Qt.DashLine, width=1.5)
		# )
		# self.c15_unstim = self.c15_livecell_in_plot.plot(
		# 	x=self.model_time,
		# 	y=self.c15_total_cells[1][4],
		# 	pen=pg.mkPen(color=(255, 127, 0), style=Qt.DotLine, width=1.5)
		# )

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
			_c15_fill_bw_cell_per_gen = self.c15_livecell_in_plot.plot(
				x=self.model_time,
				y=self.c15_total_cells[1][1][igen],
				fillLevel=0.0, brush=converted_color_palette[igen],
				pen=pg.mkPen(converted_color_palette[igen], width=1.5)
			)
			self.fill_bw_cell_per_gen_objects.append(_c15_fill_bw_cell_per_gen)

		self.c15_livecell_legends = pg.LegendItem()
		self.c15_livecell_legends.setParentItem(self.c15_livecell_in_plot)
		self.c15_livecell_legends.addItem(self.c15_livecell_curve, 'model')
		self.c15_livecell_legends.addItem(self.c15_livecell_ht_points, 'HT')
		self.c15_livecell_legends.anchor(itemPos=(0.0, 0.0), parentPos=(1.0, 0.0), offset=(-80, 0))

		# initialise empty data array for later use
		self.c15_livecell_data = pg.ErrorBarItem(x=[], y=[], beam=1.0, pen=(119, 172, 48))
		self.c15_livecell_data_curve = self.c15_livecell_in_plot.plot(x=[], y=[], symbolSize=5, symbolBrush=(119, 172, 48), pen=(119, 172, 48))
		self.c15_livecell_in_plot.addItem(self.c15_livecell_data)

		# _c15_fill_bw_model_data = pg.FillBetweenItem(
		# 	# self.c15_livecell_curve, self.c15_livecell_data_curve, brush=(0, 255, 0, 10)
		# 	self.c15_livecell_curve, self.c15_livecell_data_curve, brush=(255, 255, 255, 30)
		# )
		# self.c15_livecell_in_plot.addItem(_c15_fill_bw_model_data)

		"""Cell number vs. Generation plot for all harvested time points"""
		self.c15_cellgen = pg.GraphicsView()

		self.c15_cellgen_layout = pg.GraphicsLayout(border=(0, 0, 0, 0))
		self.c15_cellgen.setCentralItem(self.c15_cellgen_layout)
		self.c15_cellgen_layout.addLabel("Live Cells vs. Generations at HT", col=0, colspan=4)
		self.c15_cellgen_layout.nextRow()

		gens = [i for i in range(0, gvars.MAX_DIV+1)]
		self.c15_cellgen_plot_objects = []
		self.c15_cellgen_model_curves = []
		row, col = 1, 1

		for itpt, ht in enumerate(gvars.HT):
			c15_cellgen_in_plot = self.c15_cellgen_layout.addPlot(
				title='time at %s' % ht,
				x=gens,
				row=row, col=col
			)
			# c15_cellgen_in_plot.showGrid(True, True, 0.5)
			c15_cellgen_cruve = c15_cellgen_in_plot.plot(
				y=self.c15_total_cells[0][1][itpt],
				# pen=(0, 0, 0), # Note: uncomment this for default PyQt5 style
				symbolBrush=(200, 64, 0),
				symbolSize=7
			)
			self.c15_cellgen_plot_objects.append(c15_cellgen_in_plot)
			self.c15_cellgen_model_curves.append(c15_cellgen_cruve)

			col += 1
			if (itpt + 1) % 3 == 0:
				self.c15_cellgen_layout.nextRow()
				row += 1
				col = 1
		self.c15_cellgen_layout.addLabel('Number of cells', angle=-90, col=0, row=1, rowspan=row+1)
		self.c15_cellgen_layout.addLabel('Generations', col=1, colspan=4, row=row+1)

	def re_initialise(self):
		# recalculate Cyton 1.5 model results
		self.update_cyton15_pdf()
		self.update_cyton15_model()

		# remove entire c1_cellgen view box and replot it with selected_data
		self.remove_all_plots(self.c15_cellgen, self.c15_cellgen_layout)
		del self.c15_cellgen_layout

		self.c15_cellgen_layout = pg.GraphicsLayout(border=(0, 0, 0, 0))
		self.c15_cellgen.setCentralItem(self.c15_cellgen_layout)

		# redefine/draw Cell number vs. Generation portion of the plot
		self.c15_cellgen_layout.addLabel("Live Cells vs. Generations at HT", row=0, col=0, colspan=4)
		self.c15_cellgen_layout.nextRow()

		self.c15_cellgen_plot_objects = []
		self.c15_cellgen_model_curves = []
		self.c15_cellgen_data = []
		self.c15_cellgen_data_curves = []
		gens = [i for i in range(0, gvars.MAX_DIV+1)]
		row, col = 1, 1

		for itpt, ht in enumerate(gvars.EXP_HT[gvars.C15_ICND]):
			c15_cellgen_in_plot = self.c15_cellgen_layout.addPlot(
				title='time at %s' % ht,
				x=gens,
				row=row, col=col
			)
			# c15_cellgen_in_plot.showGrid(True, True, 0.5)

			# disable mouse wheel zooming events
			c15_cellgen_in_plot.vb.setMouseEnabled(x=False, y=False)
			c15_cellgen_curve = c15_cellgen_in_plot.plot(
				y=self.c15_total_cells[0][1][itpt],
				# pen=(0, 0, 0), # Note: uncomment this for default PyQt5 style
				symbolBrush=(200, 64, 0),
				symbolSize=7
			)
			self.c15_cellgen_plot_objects.append(c15_cellgen_in_plot)
			self.c15_cellgen_model_curves.append(c15_cellgen_curve)

			data = pg.ErrorBarItem(
				x=np.asarray(gens),
				y=np.asarray(gvars.CELL_GENS[gvars.C15_ICND][itpt]),
				top=np.asarray(gvars.CELL_GENS_SEM[gvars.C15_ICND][itpt]),
				bottom=np.asarray(gvars.CELL_GENS_SEM[gvars.C15_ICND][itpt]),
				beam=0.15, pen=(119, 172, 48),
			)
			data_curve = c15_cellgen_in_plot.plot(
				y=gvars.CELL_GENS[gvars.C15_ICND][itpt],
				symbolSize=5, symbolBrush=(119, 172, 48), pen=(119, 172, 48)
			)
			self.c15_cellgen_data.append(data)
			self.c15_cellgen_data_curves.append(data_curve)

			c15_cellgen_in_plot.addItem(data)
			col += 1
			if (itpt + 1) % 3 == 0:
				self.c15_cellgen_layout.nextRow()
				row += 1
				col = 1
		self.c15_cellgen_layout.addLabel('Number of cells', angle=-90, col=0, row=1, rowspan=row+1)
		self.c15_cellgen_layout.addLabel('Generations', col=1, colspan=4, row=row+1)

		if 9 < gvars.EXP_NUM_TP[gvars.C15_ICND] < 15:
			self.c15_cellgen.setFixedHeight(950)
		elif gvars.EXP_NUM_TP[gvars.C15_ICND] >= 15:
			self.c15_cellgen.setFixedHeight(1300)
		else:
			# TODO: revert to autoresize
			pass

		# update pdfs
		self.c15_unstim_die.setData(x=self.t, y=self.unstimDeath)
		self.c15_tfd.setData(x=self.t, y=self.stimDiv)
		self.c15_die.setData(x=self.t, y=self.stimDeath)
		self.c15_dd.setData(x=self.t, y=self.stimDD)

		# update cyton model
		self.c15_livecell_curve.setData(x=self.model_time, y=self.c15_total_cells[1][0])
		# compute for cumulative live cells -> easy to visualise transition from dividing -> destiny
		# cumulative_dividing = np.zeros(shape=self.model_time.size)
		# cumulative_destiny = np.zeros(shape=self.model_time.size)
		# for j in range(self.model_time.size):
		# 	for igen in range(gvars.MAX_DIV + 1):
		# 		cumulative_dividing[j] += self.c15_total_cells[1][2][igen, j]
		# 		cumulative_destiny[j] += self.c15_total_cells[1][3][igen, j]
		# self.c15_dividing.setData(x=self.model_time, y=cumulative_dividing)
		# self.c15_destiny.setData(x=self.model_time, y=cumulative_destiny)
		# self.c15_unstim.setData(x=self.model_time, y=self.c15_total_cells[1][4])
		self.c15_livecell_ht_points.setData(x=gvars.EXP_HT[gvars.C15_ICND], y=self.c15_total_cells[0][0])

		# remove filled plot item
		for plot_item in self.fill_bw_cell_per_gen_objects:
			self.c15_livecell_in_plot.removeItem(plot_item)

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
			_c15_fill_bw_cell_per_gen = self.c15_livecell_in_plot.plot(
				x=self.model_time,
				y=self.c15_total_cells[1][1][igen],
				fillLevel=0.0, brush=converted_color_palette[igen],
				pen=pg.mkPen(converted_color_palette[igen], width=1.5)
			)
			self.fill_bw_cell_per_gen_objects.append(_c15_fill_bw_cell_per_gen)

		# update data & data_curve
		self.c15_livecell_data.setData(
			x=np.asarray(gvars.EXP_HT[gvars.C15_ICND]),
			y=np.asarray(gvars.TOTAL_CELLS[gvars.C15_ICND]),
			top=np.asarray(gvars.TOTAL_CELLS_SEM[gvars.C15_ICND]),
			bottom=np.asarray(gvars.TOTAL_CELLS_SEM[gvars.C15_ICND])
		)
		self.c15_livecell_data_curve.setData(
			x=gvars.EXP_HT[gvars.C15_ICND],
			y=gvars.TOTAL_CELLS[gvars.C15_ICND]
		)

		# regenerate legends corresponding to condition name
		for condition in gvars.CONDITIONS:
			self.c15_livecell_legends.removeItem('data: %s' % condition)
		# redundantly removing and adding 'model' legend but this is only way to make legen box size minimal...
		self.c15_livecell_legends.removeItem('model')
		self.c15_livecell_legends.addItem(self.c15_livecell_curve, 'model')
		self.c15_livecell_legends.removeItem('HT')
		self.c15_livecell_legends.addItem(data_curve, 'data: %s' % gvars.CONDITIONS[gvars.C15_ICND])
		self.c15_livecell_legends.anchor(itemPos=(0.0, 0.0), parentPos=(0.72, 0.0))
		self.c15_livecell_legends.updateSize()

	def update_plot(self):
		# recalculate pdf
		self.update_cyton15_pdf()
		# recalculate model
		self.update_cyton15_model()

		# update pdfs
		self.c15_unstim_die.setData(x=self.t, y=self.unstimDeath)
		self.c15_tfd.setData(x=self.t, y=self.stimDiv)
		self.c15_die.setData(x=self.t, y=self.stimDeath)
		self.c15_dd.setData(x=self.t, y=self.stimDD)

		self.c15_b.setPos(gvars.C15_PARAMS['stimMuDiv'] + gvars.C15_PARAMS['SubDivTime'])
		# for b_line, igen in zip(self.b_lines, range(1, gvars.MAX_DIV+1)):
		# 	b_line.setValue(gvars.C15_PARAMS['stimMuDiv']+igen*gvars.C15_PARAMS['SubDivTime'])

		# update cyton model
		self.c15_livecell_curve.setData(x=self.model_time, y=self.c15_total_cells[1][0])
		# compute for cumulative live cells -> easy to visualise transition from dividing -> destiny
		# cumulative_dividing = np.zeros(shape=self.model_time.size)
		# cumulative_destiny = np.zeros(shape=self.model_time.size)
		# for j in range(self.model_time.size):
		# 	for igen in range(gvars.MAX_DIV+1):
		# 		cumulative_dividing[j] += self.c15_total_cells[1][2][igen, j]
		# 		cumulative_destiny[j] += self.c15_total_cells[1][3][igen, j]
		# self.c15_dividing.setData(x=self.model_time, y=cumulative_dividing)
		# self.c15_destiny.setData(x=self.model_time, y=cumulative_destiny)
		# self.c15_unstim.setData(x=self.model_time, y=self.c15_total_cells[1][4])
		if config.FILE_LOADED and not config.DATA_FREE:
			self.c15_livecell_ht_points.setData(x=gvars.EXP_HT[gvars.C15_ICND], y=self.c15_total_cells[0][0])
		else:
			self.c15_livecell_ht_points.setData(x=gvars.HT, y=self.c15_total_cells[0][0])

		# update filled cell number per gen
		for igen in range(gvars.MAX_DIV+1):
			self.fill_bw_cell_per_gen_objects[igen].setData(x=self.model_time, y=self.c15_total_cells[1][1][igen])

		# update cellgen
		for itpt in range(len(self.c15_cellgen_plot_objects)):
			if config.FILE_LOADED and not config.DATA_FREE:
				self.c15_cellgen_plot_objects[itpt].setTitle(title="time at %s" % gvars.EXP_HT[gvars.C15_ICND][itpt])
			else:
				self.c15_cellgen_plot_objects[itpt].setTitle(title="time at %s" % gvars.HT[itpt])
			self.c15_cellgen_model_curves[itpt].setData(self.c15_total_cells[0][1][itpt])

		if config.FILE_LOADED and not config.DATA_FREE:
			# check for excluded data set
			for itpt, l in enumerate(gvars.C15_CHECK[gvars.C15_ICND]):
				total = 0  # check total number of data : irep + igen
				check = 0  # check number of excluded data points
				for irep, sl in enumerate(l):
					for igen in range(len(sl)):
						total += 1
						check += gvars.C15_CHECK[gvars.C15_ICND][itpt][irep][igen]

				# if all data are excluded for that particular time point, color them as red
				#   NOTE : we know exactly which data are excluded,
				# 		   but pyqtgraph doesn't provide any method to change color of single data point
				# TODO: override this method to change color to specific data point
				# TODO: it's also good to recalculate error range with EXCLUDED data points and update accordingly
				if not check:
					self.c15_cellgen_data[itpt].setData(pen=(255, 0, 0))
					self.c15_cellgen_data_curves[itpt].setPen((255, 0, 0))
					self.c15_cellgen_data_curves[itpt].setSymbolBrush((255, 0, 0))
				# if any of replicates is excluded, color them as yellow
				elif 0 < check < total:
					self.c15_cellgen_data[itpt].setData(pen=(255, 255, 0))
					self.c15_cellgen_data_curves[itpt].setPen((255, 255, 0))
					self.c15_cellgen_data_curves[itpt].setSymbolBrush((255, 255, 0))
				elif check == total:
					self.c15_cellgen_data[itpt].setData(pen=(119, 172, 48))
					self.c15_cellgen_data_curves[itpt].setPen((119, 172, 48))
					self.c15_cellgen_data_curves[itpt].setSymbolBrush((119, 172, 48))

	def data_free_mode(self):
		# recalculate Cyton 1 model results
		self.update_cyton15_pdf()
		self.update_cyton15_model()

		# remove entire c1_cellgen view box and replot it with selected_data
		self.remove_all_plots(self.c15_cellgen, self.c15_cellgen_layout)
		del self.c15_cellgen_layout

		self.c15_cellgen_layout = pg.GraphicsLayout(border=(0, 0, 0, 0))
		self.c15_cellgen.setCentralItem(self.c15_cellgen_layout)

		# redefine/draw Cell number vs. Generation portion of the plot
		self.c15_cellgen_layout.addLabel("Live Cells vs. Generations at HT", row=0, col=0, colspan=4)
		self.c15_cellgen_layout.nextRow()

		self.c15_cellgen_plot_objects = []
		self.c15_cellgen_model_curves = []

		gens = [i for i in range(gvars.MAX_DIV+1)]
		row, col = 1, 1
		for itpt, ht in enumerate(gvars.HT):
			c15_cellgen_in_plot = self.c15_cellgen_layout.addPlot(
				title='time at %s' % ht,
				x=gens,
				row=row, col=col
			)
			# c15_cellgen_in_plot.showGrid(True, True, 0.5)

			# disable mouse wheel zooming events
			c15_cellgen_in_plot.vb.setMouseEnabled(x=False, y=False)
			c15_cellgen_curve = c15_cellgen_in_plot.plot(
				y=self.c15_total_cells[0][1][itpt],
				# pen=(0, 0, 0), # Note: uncomment this for default PyQt5 style
				symbolBrush=(200, 64, 0),
				symbolSize=7
			)
			self.c15_cellgen_plot_objects.append(c15_cellgen_in_plot)
			self.c15_cellgen_model_curves.append(c15_cellgen_curve)

			col += 1
			if (itpt + 1) % 3 == 0:
				self.c15_cellgen_layout.nextRow()
				row += 1
				col = 1
		self.c15_cellgen_layout.addLabel('Number of cells', angle=-90, col=0, row=1, rowspan=row + 1)
		self.c15_cellgen_layout.addLabel('Generations', col=1, colspan=4, row=row + 1)

		if 9 < len(gvars.HT) < 15:
			self.c15_cellgen.setFixedHeight(950)
		elif len(gvars.HT) >= 15:
			self.c15_cellgen.setFixedHeight(1300)
		else:
			# TODO: revert to autoresize
			pass

		# update pdfs
		self.c15_unstim_die.setData(x=self.t, y=self.unstimDeath)
		self.c15_tfd.setData(x=self.t, y=self.stimDiv)
		self.c15_die.setData(x=self.t, y=self.stimDeath)
		self.c15_dd.setData(x=self.t, y=self.stimDD)

		# update cyton model
		self.c15_livecell_curve.setData(x=self.model_time, y=self.c15_total_cells[1][0])
		self.c15_livecell_ht_points.setData(x=gvars.HT, y=self.c15_total_cells[0][0])

		# remove filled plot item
		for plot_item in self.fill_bw_cell_per_gen_objects:
			self.c15_livecell_in_plot.removeItem(plot_item)

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
			_c15_fill_bw_cell_per_gen = self.c15_livecell_in_plot.plot(
				x=self.model_time,
				y=self.c15_total_cells[1][1][igen],
				fillLevel=0.0, brush=converted_color_palette[igen],
				pen=pg.mkPen(converted_color_palette[igen], width=1.5)
			)
			self.fill_bw_cell_per_gen_objects.append(_c15_fill_bw_cell_per_gen)

		# remove data & data_curve
		self.c15_livecell_data.setData(x=np.asarray([]), y=np.asarray([]), top=np.asarray([]), bottom=np.asarray([]))
		self.c15_livecell_data_curve.setData(x=np.asarray([]), y=np.asarray([]))

		# regenerate legends corresponding to condition name
		for condition in gvars.CONDITIONS:
			self.c15_livecell_legends.removeItem('data: %s' % condition)
		# redundantly removing and adding 'model' legend but this is only way to make legen box size minimal...
		self.c15_livecell_legends.removeItem('model')
		self.c15_livecell_legends.addItem(self.c15_livecell_curve, 'model')
		self.c15_livecell_legends.removeItem('HT')
		self.c15_livecell_legends.addItem(self.c15_livecell_ht_points, 'HT')
		self.c15_livecell_legends.anchor(itemPos=(0.0, 0.0), parentPos=(0.72, 0.0))
		self.c15_livecell_legends.updateSize()
