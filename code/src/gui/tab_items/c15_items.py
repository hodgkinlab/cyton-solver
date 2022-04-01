import numpy as np

from PyQt5.QtWidgets import QGroupBox, QGridLayout, QLabel

import src.common.global_vars as gvars


def create_unstimulated_layout(parent):
	groupBox = QGroupBox("Unstimulated")
	layout = QGridLayout()

	parent.unstimMuDeath.setRange(0.001, np.inf)
	parent.unstimMuDeath.setDecimals(3)
	parent.unstimMuDeath.setObjectName("unstimMuDeath")
	parent.unstimMuDeath.setValue(gvars.C15_PARAMS['unstimMuDeath'])
	parent.unstimMuDeath.valueChanged.connect \
		(parent.c15_event_handler.handle_param_value_changed)

	parent.unstimMuDeathLock.setObjectName("unstimMuDeathLock")
	parent.unstimMuDeathLock.toggled.connect \
		(lambda: parent.c15_event_handler.handle_lock_button_state(parent.unstimMuDeathLock))

	parent.unstimMuDeathSlider.setRange(0.0, gvars.C15_UPPER_BOUNDS['unstimMuDeathUpperBound'])
	parent.unstimMuDeathSlider.setValue(gvars.C15_PARAMS['unstimMuDeath'])
	parent.unstimMuDeathSlider.setTickPosition(2)
	parent.unstimMuDeathSlider.setTickInterval(2000)
	parent.unstimMuDeathSlider.setObjectName('unstimMuDeathSlider')
	parent.unstimMuDeathSlider.valueChanged.connect \
		(lambda: parent.c15_event_handler.handle_double_slider(parent.unstimMuDeath))
	parent.unstimMuDeath.valueChanged.connect \
		(parent.unstimMuDeathSlider.setValue)

	parent.unstimMuDeathUpperBound.setObjectName("unstimMuDeathUpperBound")
	parent.unstimMuDeathUpperBound.setRange(0.001, np.inf)
	parent.unstimMuDeathUpperBound.setValue(gvars.C15_UPPER_BOUNDS['unstimMuDeathUpperBound'])
	parent.unstimMuDeathUpperBound.setButtonSymbols(2)
	parent.unstimMuDeathUpperBound.valueChanged.connect \
		(parent.unstimMuDeathSlider.setMaximum)
	parent.unstimMuDeathUpperBound.valueChanged.connect \
		(parent.c15_event_handler.handle_upper_bound_changed)

	parent.unstimSigDeath.setRange(0.001, np.inf)
	parent.unstimSigDeath.setDecimals(3)
	parent.unstimSigDeath.setObjectName("unstimSigDeath")
	parent.unstimSigDeath.setValue(gvars.C15_PARAMS['unstimSigDeath'])
	parent.unstimSigDeath.valueChanged.connect \
		(parent.c15_event_handler.handle_param_value_changed)

	parent.unstimSigDeathLock.setObjectName("unstimSigDeathLock")
	parent.unstimSigDeathLock.toggled.connect \
		(lambda: parent.c15_event_handler.handle_lock_button_state(parent.unstimSigDeathLock))

	parent.unstimSigDeathSlider.setRange(0.0, gvars.C15_UPPER_BOUNDS['unstimSigDeathUpperBound'])
	parent.unstimSigDeathSlider.setValue(gvars.C15_PARAMS['unstimSigDeath'])
	parent.unstimSigDeathSlider.setTickPosition(2)
	parent.unstimSigDeathSlider.setTickInterval(1000)
	parent.unstimSigDeathSlider.setObjectName('unstimSigDeathSlider')
	parent.unstimSigDeathSlider.valueChanged.connect \
		(lambda: parent.c15_event_handler.handle_double_slider(parent.unstimSigDeath))
	parent.unstimSigDeath.valueChanged.connect \
		(parent.unstimSigDeathSlider.setValue)

	parent.unstimSigDeathUpperBound.setObjectName("unstimSigDeathUpperBound")
	parent.unstimSigDeathUpperBound.setButtonSymbols(2)
	parent.unstimSigDeathUpperBound.setRange(0.001, np.inf)
	parent.unstimSigDeathUpperBound.setValue(gvars.C15_UPPER_BOUNDS['unstimSigDeathUpperBound'])
	parent.unstimSigDeathUpperBound.valueChanged.connect \
		(parent.unstimSigDeathSlider.setMaximum)
	parent.unstimSigDeathUpperBound.valueChanged.connect \
		(parent.c15_event_handler.handle_upper_bound_changed)

	# layout.addWidget(QLabel("<p>&mu;<sub>die</sub></p>"), 0, 0)
	layout.addWidget(QLabel("<p>m<sub>die</sub></p>"), 0, 0)
	layout.addWidget(parent.unstimMuDeathSlider, 0, 1)
	layout.addWidget(parent.unstimMuDeathUpperBound, 0, 2)
	layout.addWidget(parent.unstimMuDeath, 0, 3)
	layout.addWidget(parent.unstimMuDeathLock, 0, 4)
	# layout.addWidget(QLabel("<p>&sigma;<sub>die</sub></p>"), 1, 0)
	layout.addWidget(QLabel("<p>s<sub>die</sub></p>"), 1, 0)
	layout.addWidget(parent.unstimSigDeathSlider, 1, 1)
	layout.addWidget(parent.unstimSigDeathUpperBound, 1, 2)
	layout.addWidget(parent.unstimSigDeath, 1, 3)
	layout.addWidget(parent.unstimSigDeathLock, 1, 4)
	layout.setContentsMargins(3, 3, 3, 3)
	layout.setSpacing(5)

	groupBox.setLayout(layout)

	return groupBox


def create_stimulated_layout(parent):
	groupBox = QGroupBox("Stimulated")
	groupBoxProlif = QGroupBox("Proliferation")
	groupBoxProlif.setAlignment(4)
	groupBoxDeath = QGroupBox("Death")
	groupBoxDeath.setAlignment(4)
	groupBoxDD = QGroupBox("Division Destiny")
	groupBoxDD.setAlignment(4)
	layoutProlif = QGridLayout()
	layoutDeath = QGridLayout()
	layoutDD = QGridLayout()

	masterLayout = QGridLayout()

	parent.stimMuDiv.setRange(0.0, np.inf)
	parent.stimMuDiv.setDecimals(3)
	parent.stimMuDiv.setObjectName("stimMuDiv")
	parent.stimMuDiv.setValue(gvars.C15_PARAMS['stimMuDiv'])
	parent.stimMuDiv.valueChanged.connect \
		(parent.c15_event_handler.handle_param_value_changed)

	parent.stimMuDivLock.setObjectName("stimMuDivLock")
	parent.stimMuDivLock.toggled.connect \
		(lambda: parent.c15_event_handler.handle_lock_button_state(parent.stimMuDivLock))

	parent.stimMuDivSlider.setRange(0.0, gvars.C15_UPPER_BOUNDS['stimMuDivUpperBound'])
	parent.stimMuDivSlider.setValue(gvars.C15_PARAMS['stimMuDiv'])
	parent.stimMuDivSlider.setTickPosition(2)
	parent.stimMuDivSlider.setTickInterval(2000)
	parent.stimMuDivSlider.setObjectName('stimMuDivSlider')
	parent.stimMuDivSlider.valueChanged.connect \
		(lambda: parent.c15_event_handler.handle_double_slider(parent.stimMuDiv))
	parent.stimMuDiv.valueChanged.connect \
		(parent.stimMuDivSlider.setValue)

	parent.stimMuDivUpperBound.setObjectName("stimMuDivUpperBound")
	parent.stimMuDivUpperBound.setRange(0.0, np.inf)
	parent.stimMuDivUpperBound.setValue(gvars.C15_UPPER_BOUNDS['stimMuDivUpperBound'])
	parent.stimMuDivUpperBound.setButtonSymbols(2)
	parent.stimMuDivUpperBound.valueChanged.connect \
		(parent.stimMuDivSlider.setMaximum)
	parent.stimMuDivUpperBound.valueChanged.connect \
		(parent.c15_event_handler.handle_upper_bound_changed)

	parent.stimSigDiv.setRange(0.001, np.inf)
	parent.stimSigDiv.setDecimals(3)
	parent.stimSigDiv.setObjectName("stimSigDiv")
	parent.stimSigDiv.setValue(gvars.C15_PARAMS['stimSigDiv'])
	parent.stimSigDiv.valueChanged.connect \
		(parent.c15_event_handler.handle_param_value_changed)

	parent.stimSigDivLock.setObjectName("stimSigDivLock")
	parent.stimSigDivLock.toggled.connect \
		(lambda: parent.c15_event_handler.handle_lock_button_state(parent.stimSigDivLock))

	parent.stimSigDivSlider.setRange(0.0, gvars.C15_UPPER_BOUNDS['stimSigDivUpperBound'])
	parent.stimSigDivSlider.setValue(gvars.C15_PARAMS['stimSigDiv'])
	parent.stimSigDivSlider.setTickPosition(2)
	parent.stimSigDivSlider.setTickInterval(1000)
	parent.stimSigDivSlider.setObjectName('stimSigDivSlider')
	parent.stimSigDivSlider.valueChanged.connect \
		(lambda: parent.c15_event_handler.handle_double_slider(parent.stimSigDiv))
	parent.stimSigDiv.valueChanged.connect \
		(parent.stimSigDivSlider.setValue)

	parent.stimSigDivUpperBound.setObjectName("stimSigDivUpperBound")
	parent.stimSigDivUpperBound.setButtonSymbols(2)
	parent.stimSigDivUpperBound.setRange(0.001, np.inf)
	parent.stimSigDivUpperBound.setValue(gvars.C15_UPPER_BOUNDS['stimSigDivUpperBound'])
	parent.stimSigDivUpperBound.valueChanged.connect \
		(parent.stimSigDivSlider.setMaximum)
	parent.stimSigDivUpperBound.valueChanged.connect \
		(parent.c15_event_handler.handle_upper_bound_changed)

	# layoutProlif.addWidget(QLabel("<p>&mu;<sub>div</sub></p>"), 0, 0)
	layoutProlif.addWidget(QLabel("<p>m<sub>div</sub></p>"), 0, 0)
	layoutProlif.addWidget(parent.stimMuDivSlider, 0, 1)
	layoutProlif.addWidget(parent.stimMuDivUpperBound, 0, 2)
	layoutProlif.addWidget(parent.stimMuDiv, 0, 3)
	layoutProlif.addWidget(parent.stimMuDivLock, 0, 4)
	# layoutProlif.addWidget(QLabel("<p>&sigma;<sub>div</sub></p>"), 1, 0)
	layoutProlif.addWidget(QLabel("<p>s<sub>div</sub></p>"), 1, 0)
	layoutProlif.addWidget(parent.stimSigDivSlider, 1, 1)
	layoutProlif.addWidget(parent.stimSigDivUpperBound, 1, 2)
	layoutProlif.addWidget(parent.stimSigDiv, 1, 3)
	layoutProlif.addWidget(parent.stimSigDivLock, 1, 4)
	layoutProlif.setContentsMargins(3, 3, 3, 3)
	layoutProlif.setSpacing(5)

	parent.stimMuDeath.setRange(0.0, np.inf)
	parent.stimMuDeath.setDecimals(3)
	parent.stimMuDeath.setObjectName("stimMuDeath")
	parent.stimMuDeath.setValue(gvars.C15_PARAMS['stimMuDeath'])
	parent.stimMuDeath.valueChanged.connect \
		(parent.c15_event_handler.handle_param_value_changed)

	parent.stimMuDeathLock.setObjectName("stimMuDeathLock")
	parent.stimMuDeathLock.toggled.connect \
		(lambda: parent.c15_event_handler.handle_lock_button_state(parent.stimMuDeathLock))

	parent.stimMuDeathSlider.setRange(0.0, gvars.C15_UPPER_BOUNDS['stimMuDeathUpperBound'])
	parent.stimMuDeathSlider.setValue(gvars.C15_PARAMS['stimMuDeath'])
	parent.stimMuDeathSlider.setTickPosition(2)
	parent.stimMuDeathSlider.setTickInterval(2000)
	parent.stimMuDeathSlider.setObjectName('stimMuDeathSlider')
	parent.stimMuDeathSlider.valueChanged.connect \
		(lambda: parent.c15_event_handler.handle_double_slider(parent.stimMuDeath))
	parent.stimMuDeath.valueChanged.connect \
		(parent.stimMuDeathSlider.setValue)

	parent.stimMuDeathUpperBound.setObjectName("stimMuDeathUpperBound")
	parent.stimMuDeathUpperBound.setRange(0.0, np.inf)
	parent.stimMuDeathUpperBound.setValue(gvars.C15_UPPER_BOUNDS['stimMuDeathUpperBound'])
	parent.stimMuDeathUpperBound.setButtonSymbols(2)
	parent.stimMuDeathUpperBound.valueChanged.connect \
		(parent.stimMuDeathSlider.setMaximum)
	parent.stimMuDeathUpperBound.valueChanged.connect \
		(parent.c15_event_handler.handle_upper_bound_changed)

	parent.stimSigDeath.setRange(0.001, np.inf)
	parent.stimSigDeath.setDecimals(3)
	parent.stimSigDeath.setObjectName("stimSigDeath")
	parent.stimSigDeath.setValue(gvars.C15_PARAMS['stimSigDeath'])
	parent.stimSigDeath.valueChanged.connect \
		(parent.c15_event_handler.handle_param_value_changed)

	parent.stimSigDeathLock.setObjectName("stimSigDeathLock")
	parent.stimSigDeathLock.toggled.connect \
		(lambda: parent.c15_event_handler.handle_lock_button_state(parent.stimSigDeathLock))

	parent.stimSigDeathSlider.setRange(0.0, gvars.C15_UPPER_BOUNDS['stimSigDeathUpperBound'])
	parent.stimSigDeathSlider.setValue(gvars.C15_PARAMS['stimSigDeath'])
	parent.stimSigDeathSlider.setTickPosition(2)
	parent.stimSigDeathSlider.setTickInterval(1000)
	parent.stimSigDeathSlider.setObjectName('stimSigDeathSlider')
	parent.stimSigDeathSlider.valueChanged.connect \
		(lambda: parent.c15_event_handler.handle_double_slider(parent.stimSigDeath))
	parent.stimSigDeath.valueChanged.connect \
		(parent.stimSigDeathSlider.setValue)

	parent.stimSigDeathUpperBound.setObjectName("stimSigDeathUpperBound")
	parent.stimSigDeathUpperBound.setButtonSymbols(2)
	parent.stimSigDeathUpperBound.setRange(0.001, np.inf)
	parent.stimSigDeathUpperBound.setValue(gvars.C15_UPPER_BOUNDS['stimSigDeathUpperBound'])
	parent.stimSigDeathUpperBound.valueChanged.connect \
		(parent.stimSigDeathSlider.setMaximum)
	parent.stimSigDeathUpperBound.valueChanged.connect \
		(parent.c15_event_handler.handle_upper_bound_changed)

	# layoutDeath.addWidget(QLabel("<p>&mu;<sub>die</sub></p>"), 0, 0)
	layoutDeath.addWidget(QLabel("<p>m<sub>die</sub></p>"), 0, 0)
	layoutDeath.addWidget(parent.stimMuDeathSlider, 0, 1)
	layoutDeath.addWidget(parent.stimMuDeathUpperBound, 0, 2)
	layoutDeath.addWidget(parent.stimMuDeath, 0, 3)
	layoutDeath.addWidget(parent.stimMuDeathLock, 0, 4)
	# layoutDeath.addWidget(QLabel("<p>&sigma;<sub>die</sub></p>"), 1, 0)
	layoutDeath.addWidget(QLabel("<p>s<sub>die</sub></p>"), 1, 0)
	layoutDeath.addWidget(parent.stimSigDeathSlider, 1, 1)
	layoutDeath.addWidget(parent.stimSigDeathUpperBound, 1, 2)
	layoutDeath.addWidget(parent.stimSigDeath, 1, 3)
	layoutDeath.addWidget(parent.stimSigDeathLock, 1, 4)
	layoutDeath.setContentsMargins(3, 3, 3, 3)
	layoutDeath.setSpacing(5)

	parent.stimMuDD.setRange(0.0, np.inf)
	parent.stimMuDD.setDecimals(3)
	parent.stimMuDD.setObjectName("stimMuDD")
	parent.stimMuDD.setValue(gvars.C15_PARAMS['stimMuDD'])
	parent.stimMuDD.valueChanged.connect \
		(parent.c15_event_handler.handle_param_value_changed)

	parent.stimMuDDLock.setObjectName("stimMuDDLock")
	parent.stimMuDDLock.toggled.connect \
		(lambda: parent.c15_event_handler.handle_lock_button_state(parent.stimMuDDLock))

	parent.stimMuDDSlider.setRange(0.0, gvars.C15_UPPER_BOUNDS['stimMuDDUpperBound'])
	parent.stimMuDDSlider.setValue(gvars.C15_PARAMS['stimMuDD'])
	parent.stimMuDDSlider.setTickPosition(2)
	parent.stimMuDDSlider.setTickInterval(2000)
	parent.stimMuDDSlider.setObjectName('stimMuDDSlider')
	parent.stimMuDDSlider.valueChanged.connect \
		(lambda: parent.c15_event_handler.handle_double_slider(parent.stimMuDD))
	parent.stimMuDD.valueChanged.connect \
		(parent.stimMuDDSlider.setValue)

	parent.stimMuDDUpperBound.setObjectName("stimMuDDUpperBound")
	parent.stimMuDDUpperBound.setRange(0.0, np.inf)
	parent.stimMuDDUpperBound.setValue(gvars.C15_UPPER_BOUNDS['stimMuDDUpperBound'])
	parent.stimMuDDUpperBound.setButtonSymbols(2)
	parent.stimMuDDUpperBound.valueChanged.connect \
		(parent.stimMuDDSlider.setMaximum)
	parent.stimMuDDUpperBound.valueChanged.connect \
		(parent.c15_event_handler.handle_upper_bound_changed)

	parent.stimSigDD.setRange(0.001, np.inf)
	parent.stimSigDD.setDecimals(3)
	parent.stimSigDD.setObjectName("stimSigDD")
	parent.stimSigDD.setValue(gvars.C15_PARAMS['stimSigDD'])
	parent.stimSigDD.valueChanged.connect \
		(parent.c15_event_handler.handle_param_value_changed)

	parent.stimSigDDLock.setObjectName("stimSigDDLock")
	parent.stimSigDDLock.toggled.connect \
		(lambda: parent.c15_event_handler.handle_lock_button_state(parent.stimSigDDLock))

	parent.stimSigDDSlider.setRange(0.0, gvars.C15_UPPER_BOUNDS['stimSigDDUpperBound'])
	parent.stimSigDDSlider.setValue(gvars.C15_PARAMS['stimSigDD'])
	parent.stimSigDDSlider.setTickPosition(2)
	parent.stimSigDDSlider.setTickInterval(1000)
	parent.stimSigDDSlider.setObjectName('stimSigDDSlider')
	parent.stimSigDDSlider.valueChanged.connect \
		(lambda: parent.c15_event_handler.handle_double_slider(parent.stimSigDD))
	parent.stimSigDD.valueChanged.connect \
		(parent.stimSigDDSlider.setValue)

	parent.stimSigDDUpperBound.setObjectName("stimSigDDUpperBound")
	parent.stimSigDDUpperBound.setButtonSymbols(2)
	parent.stimSigDDUpperBound.setRange(0.001, np.inf)
	parent.stimSigDDUpperBound.setValue(gvars.C15_UPPER_BOUNDS['stimSigDDUpperBound'])
	parent.stimSigDDUpperBound.valueChanged.connect \
		(parent.stimSigDDSlider.setMaximum)
	parent.stimSigDDUpperBound.valueChanged.connect \
		(parent.c15_event_handler.handle_upper_bound_changed)

	# layoutDD.addWidget(QLabel("<p>&mu;<sub>dd</sub></p>"), 0, 0)
	layoutDD.addWidget(QLabel("<p>m<sub>dd</sub></p>"), 0, 0)
	layoutDD.addWidget(parent.stimMuDDSlider, 0, 1)
	layoutDD.addWidget(parent.stimMuDDUpperBound, 0, 2)
	layoutDD.addWidget(parent.stimMuDD, 0, 3)
	layoutDD.addWidget(parent.stimMuDDLock, 0, 4)
	# layoutDD.addWidget(QLabel("<p>&sigma;<sub>dd</sub></p>"), 1, 0)
	layoutDD.addWidget(QLabel("<p>s<sub>dd</sub></p>"), 1, 0)
	layoutDD.addWidget(parent.stimSigDDSlider, 1, 1)
	layoutDD.addWidget(parent.stimSigDDUpperBound, 1, 2)
	layoutDD.addWidget(parent.stimSigDD, 1, 3)
	layoutDD.addWidget(parent.stimSigDDLock, 1, 4)
	layoutDD.setContentsMargins(3, 3, 3, 3)
	layoutDD.setSpacing(5)

	groupBoxProlif.setLayout(layoutProlif)
	groupBoxDeath.setLayout(layoutDeath)
	groupBoxDD.setLayout(layoutDD)

	masterLayout.addWidget(groupBoxProlif, 0, 0)
	masterLayout.addWidget(groupBoxDeath, 1, 0)
	masterLayout.addWidget(groupBoxDD, 2, 0)
	masterLayout.setContentsMargins(3, 3, 3, 3)
	masterLayout.setSpacing(5)

	groupBox.setLayout(masterLayout)

	return groupBox


def create_ext_layout(parent):
	groupBox = QGroupBox("Miscellaneous")
	layout = QGridLayout()

	parent.SubDivTime.setRange(0.0, np.inf)
	parent.SubDivTime.setDecimals(3)
	parent.SubDivTime.setSingleStep(0.1)
	parent.SubDivTime.setObjectName("SubDivTime")
	parent.SubDivTime.setValue(gvars.C15_PARAMS['SubDivTime'])
	parent.SubDivTime.valueChanged.connect \
		(parent.c15_event_handler.handle_param_value_changed)

	parent.SubDivTimeLock.setObjectName("SubDivTimeLock")
	parent.SubDivTimeLock.toggled.connect \
		(lambda: parent.c15_event_handler.handle_lock_button_state(parent.SubDivTimeLock))

	parent.SubDivTimeSlider.setRange(0.0, 50.0)
	parent.SubDivTimeSlider.setValue(gvars.C15_PARAMS['SubDivTime'])
	parent.SubDivTimeSlider.setTickPosition(2)
	parent.SubDivTimeSlider.setTickInterval(1000)
	parent.SubDivTimeSlider.setObjectName('SubDivTimeSlider')
	parent.SubDivTimeSlider.valueChanged.connect \
		(lambda: parent.c15_event_handler.handle_double_slider(parent.SubDivTime))
	parent.SubDivTime.valueChanged.connect \
		(parent.SubDivTimeSlider.setValue)

	parent.SubDivTimeUpperBound.setObjectName("SubDivTimeUpperBound")
	parent.SubDivTimeUpperBound.setButtonSymbols(2)
	parent.SubDivTimeUpperBound.setValue(gvars.C15_UPPER_BOUNDS['SubDivTimeUpperBound'])
	parent.SubDivTimeUpperBound.setRange(0.0, np.inf)
	parent.SubDivTimeUpperBound.valueChanged.connect \
		(parent.SubDivTimeSlider.setMaximum)
	parent.SubDivTimeUpperBound.valueChanged.connect \
		(parent.c15_event_handler.handle_upper_bound_changed)

	parent.pfrac.setRange(0.0, 1.0)
	parent.pfrac.setDecimals(3)
	parent.pfrac.setSingleStep(0.001)
	parent.pfrac.setObjectName("pfrac")
	parent.pfrac.setValue(gvars.C15_PARAMS['pfrac'])
	parent.pfrac.valueChanged.connect \
		(parent.c15_event_handler.handle_param_value_changed)

	parent.pfracLock.setObjectName("pfracLock")
	parent.pfracLock.toggled.connect \
		(lambda: parent.c15_event_handler.handle_lock_button_state(parent.pfracLock))

	parent.pfracSlider.setRange(0.0, 1.0)
	parent.pfracSlider.setValue(gvars.C15_PARAMS['pfrac'])
	parent.pfracSlider.setTickPosition(2)
	parent.pfracSlider.setTickInterval(1000)
	parent.pfracSlider.setObjectName('pfracSlider')
	parent.pfracSlider.valueChanged.connect \
		(lambda: parent.c15_event_handler.handle_double_slider(parent.pfrac))
	parent.pfrac.valueChanged.connect \
		(parent.pfracSlider.setValue)

	parent.pfracUpperBound.setObjectName("pfracUpperBound")
	parent.pfracUpperBound.setButtonSymbols(2)
	parent.pfracUpperBound.setValue(gvars.C15_UPPER_BOUNDS['pfracUpperBound'])
	parent.pfracUpperBound.setRange(0.0, 1.0)
	parent.pfracUpperBound.setDecimals(3)
	parent.pfracUpperBound.valueChanged.connect \
		(parent.pfracSlider.setMaximum)
	parent.pfracUpperBound.valueChanged.connect \
		(parent.c15_event_handler.handle_upper_bound_changed)

	layout.addWidget(QLabel("b"), 0, 0)
	layout.addWidget(parent.SubDivTimeSlider, 0, 1)
	layout.addWidget(parent.SubDivTimeUpperBound, 0, 2)
	layout.addWidget(parent.SubDivTime, 0, 3)
	layout.addWidget(parent.SubDivTimeLock, 0, 4)
	layout.addWidget(QLabel("pF"), 1, 0)
	layout.addWidget(parent.pfracSlider, 1, 1)
	layout.addWidget(parent.pfracUpperBound, 1, 2)
	layout.addWidget(parent.pfrac, 1, 3)
	layout.addWidget(parent.pfracLock, 1, 4)
	layout.setContentsMargins(3, 3, 3, 3)
	layout.setSpacing(5)

	groupBox.setLayout(layout)

	return groupBox
