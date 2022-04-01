import seaborn as sns
import numpy as np
import pyqtgraph as pg
from scipy.stats import lognorm, norm, expon

import src.common.settings as config
import src.common.global_vars as gvars


# dummy_conds = ['1uM', '2uM', '3uM', '4uM']
# dummy1 = [6.716670121, 0.996282134, 30.63254258, 0.199823017, 97.74594867, 0.4323829, 62.02651313, 0.142707133, 8.895420531, 0.593791461]
# dummy2 = [9.982050803, 0.937825409, 30.31091794, 0.185904705, 83.29674347, 0.211535504, 60.71342901, 0.156441588, 8.896531459, 0.573571075]
# dummy3 = [6.685804666, 0.403712223, 30.44335837, 0.203092555, 74.09788198, 0.188111203, 63.19713693, 0.155063427, 9.1431577, 0.684493019]
# dummy4 = [8.532879928, 0.181725034, 32.98518426, 0.185298332, 70.66097386, 0.163106559, 64.79250151, 0.151527834, 9.402838675, 0.718928848]


class CompareCanvas:
	def __init__(self):
		super().__init__()

		# set general pyqtgraph settings

		# uncomment this for default PyQt5 style
		# pg.setConfigOption('background', 'w')
		# pg.setConfigOption('foreground', 'k')
		pg.setConfigOption('foreground', 'w')
		pg.setConfigOption('leftButtonPan', False)
		pg.setConfigOptions(antialias=True)

		# update variables
		self.curr_cond = []
		self.params = []

		self.pdf1_items = []
		self.pdf2_items = []
		self.pdf3_items = []
		self.pdf4_items = []

		# plot setting variables
		self.tf = 200.

		self._init_compare()

	def _init_compare(self):
		self.pdf1 = pg.GraphicsView()
		self.pdf1_layout = pg.GraphicsLayout(border=(0, 0, 0, 0))
		self.pdf1.setCentralItem(self.pdf1_layout)
		self.pdf1_in_plot = self.pdf1_layout.addPlot(title='Unstimulated Death')
		# self.pdf1_in_plot.showGrid(True, True, 0.5)
		self.pdf1_in_plot.setLabel('bottom', 'time (hrs)')
		self.pdf1_legends = pg.LegendItem()
		self.pdf1_legends.setParentItem(self.pdf1_in_plot)
		self.pdf1_legends.anchor(itemPos=(0.0, 0.0), parentPos=(1.0, 0.0), offset=(-160, 0))

		self.pdf2 = pg.GraphicsView()
		self.pdf2_layout = pg.GraphicsLayout(border=(0, 0, 0, 0))
		self.pdf2.setCentralItem(self.pdf2_layout)
		self.pdf2_in_plot = self.pdf2_layout.addPlot(title='Time to First Division')
		# self.pdf2_in_plot.showGrid(True, True, 0.5)
		self.pdf2_in_plot.setLabel('bottom', 'time (hrs)')
		self.pdf2_legends = pg.LegendItem()
		self.pdf2_legends.setParentItem(self.pdf2_in_plot)
		self.pdf2_legends.anchor(itemPos=(0.0, 0.0), parentPos=(1.0, 0.0), offset=(-160, 0))

		self.pdf3 = pg.GraphicsView()
		self.pdf3_layout = pg.GraphicsLayout(border=(0, 0, 0, 0))
		self.pdf3.setCentralItem(self.pdf3_layout)
		self.pdf3_in_plot = self.pdf3_layout.addPlot(title='Stimulated Death')
		# self.pdf3_in_plot.showGrid(True, True, 0.5)
		self.pdf3_in_plot.setLabel('bottom', 'time (hrs)')
		self.pdf3_legends = pg.LegendItem()
		self.pdf3_legends.setParentItem(self.pdf3_in_plot)
		self.pdf3_legends.anchor(itemPos=(0.0, 0.0), parentPos=(1.0, 0.0), offset=(-160, 0))

		self.pdf4 = pg.GraphicsView()
		self.pdf4_layout = pg.GraphicsLayout(border=(0, 0, 0, 0))
		self.pdf4.setCentralItem(self.pdf4_layout)
		self.pdf4_in_plot = self.pdf4_layout.addPlot(title='Division Destiny')
		# self.pdf4_in_plot.showGrid(True, True, 0.5)
		self.pdf4_in_plot.setLabel('bottom', 'time (hrs)')
		self.pdf4_legends = pg.LegendItem()
		self.pdf4_legends.setParentItem(self.pdf4_in_plot)
		self.pdf4_legends.anchor(itemPos=(0.0, 0.0), parentPos=(1.0, 0.0), offset=(-160, 0))

		# params = [dummy1, dummy2, dummy3, dummy4]
		# self._compare_pdfs(self.tf, params, dummy_conds)

	def _compute_pdf(self, t, m, s, pdf_type='Lognormal'):
		if pdf_type == 'Lognormal':
			return lognorm.pdf(t, s, scale=np.exp(np.log(m)))
		elif pdf_type == 'Gaussian':
			return norm.pdf(t, loc=m, scale=s)
		elif pdf_type == 'Exponential':
			raise NotImplementedError("Exponential distribution is not implemented")

	def _compare_pdfs(self, tf, params, conditions):
		# define seaborn color_palette
		sns_color_palette = sns.hls_palette(len(conditions), l=.3, s=.5)
		# pyqtgraph requires 3digit rgb values unlike [0, 1] in matplotlib/seaborn
		converted_color_palette = []
		for i, cp in enumerate(sns_color_palette):
			tmp = []
			for j, item in enumerate(cp):
				tmp.append(item * 255.)
			tmp.append(150)  # transparency in percentage
			converted_color_palette.append(tmp)

		times = np.linspace(0, tf, num=1000, dtype=float)

		for icnd, par in enumerate(params):
			unst_die_pdf = self._compute_pdf(times, par[0], par[1], config.CYTON15_CONFIG['unstim_die'])
			stim_div_pdf = self._compute_pdf(times, par[2], par[3], config.CYTON15_CONFIG['stim_div'])
			stim_die_pdf = self._compute_pdf(times, par[4], par[5], config.CYTON15_CONFIG['stim_die'])
			stim_dd_pdf = self._compute_pdf(times, par[6], par[7], config.CYTON15_CONFIG['stim_dd'])

			a = self.pdf1_in_plot.plot(
				x=times, y=unst_die_pdf,
				fillLevel=0, brush=converted_color_palette[icnd],
				pen=pg.mkPen(converted_color_palette[icnd], width=1.5)
			)
			b = self.pdf2_in_plot.plot(
				x=times, y=stim_div_pdf,
				fillLevel=0, brush=converted_color_palette[icnd],
				pen=pg.mkPen(converted_color_palette[icnd], width=1.5)
			)
			c = self.pdf3_in_plot.plot(
				x=times, y=stim_die_pdf,
				fillLevel=0, brush=converted_color_palette[icnd],
				pen=pg.mkPen(converted_color_palette[icnd], width=1.5)
			)
			d = self.pdf4_in_plot.plot(
				x=times, y=stim_dd_pdf,
				fillLevel=0, brush=converted_color_palette[icnd],
				pen=pg.mkPen(converted_color_palette[icnd], width=1.5)
			)

			self.pdf1_items.append(a)
			self.pdf2_items.append(b)
			self.pdf3_items.append(c)
			self.pdf4_items.append(d)

			self.pdf1_legends.addItem(a, '{0}'.format(conditions[icnd]))
			self.pdf2_legends.addItem(b, '{0}'.format(conditions[icnd]))
			self.pdf3_legends.addItem(c, '{0}'.format(conditions[icnd]))
			self.pdf4_legends.addItem(d, '{0}'.format(conditions[icnd]))

		# save params in this class for updating plots
		self.params = params

	def _compare_params(self, comparant, params, conditions):
		pass

	def clear_all(self):
		# clear plot items
		self.pdf1_in_plot.clear()
		self.pdf2_in_plot.clear()
		self.pdf3_in_plot.clear()
		self.pdf4_in_plot.clear()

		# remove legends
		for cond in self.curr_cond:
			self.pdf1_legends.removeItem(cond)
			self.pdf2_legends.removeItem(cond)
			self.pdf3_legends.removeItem(cond)
			self.pdf4_legends.removeItem(cond)

	def apply_plot_settings(self, incs):
		self.tf = incs

		times = np.linspace(0, self.tf, num=1000, dtype=float)

		for i, par in enumerate(self.params):
			unst_die_pdf = self._compute_pdf(times, par[0], par[1])
			stim_div_pdf = self._compute_pdf(times, par[2], par[3])
			stim_die_pdf = self._compute_pdf(times, par[4], par[5])
			stim_dd_pdf = self._compute_pdf(times, par[6], par[7])

			self.pdf1_items[i].setData(x=times, y=unst_die_pdf)
			self.pdf2_items[i].setData(x=times, y=stim_div_pdf)
			self.pdf3_items[i].setData(x=times, y=stim_die_pdf)
			self.pdf4_items[i].setData(x=times, y=stim_dd_pdf)

	def update(self, data):
		self.clear_all()

		# sort data
		tmp_cond, parse_pars = [], []
		for datum in data:
			# TODO: add check in case condition names are the same
			datum = list(datum)
			tmp_cond.append(datum[0])
			parse_pars.append(datum[2:len(datum)-1])  # slice only relevent part
		self.curr_cond = tmp_cond

		self._compare_pdfs(self.tf, parse_pars, tmp_cond)
