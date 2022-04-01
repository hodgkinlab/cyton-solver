import numpy as np

from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QGridLayout, QLabel

import src.common.global_vars as gvars


def create_undivided_layout(parent):
    group_box = QGroupBox("First Division")
    group_box_prolif = QGroupBox("Proliferation")
    group_box_prolif.setAlignment(4)
    group_box_death = QGroupBox("Death")
    group_box_death.setAlignment(4)
    _master_layout = QVBoxLayout()
    _layout_prolif = QGridLayout()
    _layout_death = QGridLayout()

    ############################################################
    #   Undivided cells (first division) - MU - DIVIDE
    #       mu0div
    ############################################################
    parent.mu0div.setRange(0.001, np.inf)
    parent.mu0div.setDecimals(3)
    parent.mu0div.setObjectName("mu0div")
    parent.mu0div.setValue(gvars.C1_PARAMS['mu0div'])
    parent.mu0div.setSingleStep(0.1)
    parent.mu0div.valueChanged.connect \
        (parent.c1_event_handler.handle_param_value_changed)

    parent.mu0divLock.setObjectName("mu0divLock")
    parent.mu0divLock.toggled.connect \
        (lambda: parent.c1_event_handler.handle_lock_button_state(parent.mu0divLock))

    parent.mu0divSlider.setRange(0.0, 100.0)
    parent.mu0divSlider.setValue(gvars.C1_PARAMS['mu0div'])
    parent.mu0divSlider.setTickPosition(2)
    parent.mu0divSlider.setTickInterval(2000)
    parent.mu0divSlider.setObjectName('mu0divSlider')
    parent.mu0divSlider.valueChanged.connect \
        (lambda: parent.c1_event_handler.handle_double_slider(parent.mu0div))
    parent.mu0div.valueChanged.connect \
        (parent.mu0divSlider.setValue)

    parent.mu0divUpperBound.setObjectName("mu0divUpperBound")
    parent.mu0divUpperBound.setDecimals(3)
    parent.mu0divUpperBound.setRange(0.001, np.inf)
    parent.mu0divUpperBound.setValue(gvars.C1_UPPER_BOUNDS['mu0divUpperBound'])
    parent.mu0divUpperBound.setButtonSymbols(2)
    parent.mu0divUpperBound.valueChanged.connect \
        (parent.mu0divSlider.setMaximum)
    parent.mu0divUpperBound.valueChanged.connect \
        (parent.c1_event_handler.handle_upper_bound_changed)

    ############################################################
    #   Undivided cells (first division) - SIGMA - DIVIDE
    #       sig0div
    ############################################################
    parent.sig0div.setRange(0.001, np.inf)
    parent.sig0div.setDecimals(3)
    parent.sig0div.setObjectName("sig0div")
    parent.sig0div.setValue(gvars.C1_PARAMS['sig0div'])
    parent.sig0div.valueChanged.connect \
        (parent.c1_event_handler.handle_param_value_changed)

    parent.sig0divLock.setObjectName("sig0divLock")
    parent.sig0divLock.toggled.connect \
        (lambda: parent.c1_event_handler.handle_lock_button_state(parent.sig0divLock))

    parent.sig0divSlider.setRange(0.0, 1.0)
    parent.sig0divSlider.setValue(gvars.C1_PARAMS['sig0div'])
    parent.sig0divSlider.setTickPosition(2)
    parent.sig0divSlider.setTickInterval(1000)
    parent.sig0divSlider.setObjectName('sig0divSlider')
    parent.sig0divSlider.valueChanged.connect \
        (lambda: parent.c1_event_handler.handle_double_slider(parent.sig0div))
    parent.sig0div.valueChanged.connect \
        (parent.sig0divSlider.setValue)

    parent.sig0divUpperBound.setObjectName("sig0divUpperBound")
    parent.sig0divUpperBound.setDecimals(3)
    parent.sig0divUpperBound.setButtonSymbols(2)
    parent.sig0divUpperBound.setValue(gvars.C1_UPPER_BOUNDS['sig0divUpperBound'])
    parent.sig0divUpperBound.setRange(0.001, np.inf)
    parent.sig0divUpperBound.valueChanged.connect \
        (parent.sig0divSlider.setMaximum)
    parent.sig0divUpperBound.valueChanged.connect \
        (parent.c1_event_handler.handle_upper_bound_changed)

    ############################################################
    #   Undivided cells (first division) - MU - DEATH
    #       mu0death
    ############################################################
    parent.mu0death.setRange(0.001, np.inf)
    parent.mu0death.setDecimals(3)
    parent.mu0death.setObjectName("mu0death")
    parent.mu0death.setValue(gvars.C1_PARAMS['mu0death'])
    parent.mu0death.valueChanged.connect \
        (parent.c1_event_handler.handle_param_value_changed)

    parent.mu0deathLock.setObjectName("mu0deathLock")
    parent.mu0deathLock.toggled.connect \
        (lambda: parent.c1_event_handler.handle_lock_button_state(parent.mu0deathLock))

    parent.mu0deathSlider.setRange(0.0, 100.0)
    parent.mu0deathSlider.setValue(gvars.C1_PARAMS['mu0death'])
    parent.mu0deathSlider.setTickPosition(2)
    parent.mu0deathSlider.setTickInterval(2000)
    parent.mu0deathSlider.setObjectName('mu0deathSlider')
    parent.mu0deathSlider.valueChanged.connect \
        (lambda: parent.c1_event_handler.handle_double_slider(parent.mu0death))
    parent.mu0death.valueChanged.connect \
        (parent.mu0deathSlider.setValue)

    parent.mu0deathUpperBound.setObjectName("mu0deathUpperBound")
    parent.mu0deathUpperBound.setDecimals(3)
    parent.mu0deathUpperBound.setRange(0.001, np.inf)
    parent.mu0deathUpperBound.setValue(gvars.C1_UPPER_BOUNDS['mu0deathUpperBound'])
    parent.mu0deathUpperBound.setButtonSymbols(2)
    parent.mu0deathUpperBound.valueChanged.connect \
        (parent.mu0deathSlider.setMaximum)
    parent.mu0deathUpperBound.valueChanged.connect \
        (parent.c1_event_handler.handle_upper_bound_changed)

    ############################################################
    #   Undivided cells (first division) - SIGMA - DEATH
    #       sig0death
    ############################################################
    parent.sig0death.setRange(0.001, np.inf)
    parent.sig0death.setDecimals(3)
    parent.sig0death.setObjectName("sig0death")
    parent.sig0death.setValue(gvars.C1_PARAMS['sig0death'])
    parent.sig0death.valueChanged.connect \
        (parent.c1_event_handler.handle_param_value_changed)

    parent.sig0deathLock.setObjectName("sig0deathLock")
    parent.sig0deathLock.toggled.connect \
        (lambda: parent.c1_event_handler.handle_lock_button_state(parent.sig0deathLock))

    parent.sig0deathSlider.setRange(0.0, 1.0)
    parent.sig0deathSlider.setValue(gvars.C1_PARAMS['sig0death'])
    parent.sig0deathSlider.setTickPosition(2)
    parent.sig0deathSlider.setTickInterval(1000)
    parent.sig0deathSlider.setObjectName('sig0deathSlider')
    parent.sig0deathSlider.valueChanged.connect \
        (lambda: parent.c1_event_handler.handle_double_slider(parent.sig0death))
    parent.sig0death.valueChanged.connect \
        (parent.sig0deathSlider.setValue)

    parent.sig0deathUpperBound.setObjectName("sig0deathUpperBound")
    parent.sig0deathUpperBound.setDecimals(3)
    parent.sig0deathUpperBound.setButtonSymbols(2)
    parent.sig0deathUpperBound.setValue(gvars.C1_UPPER_BOUNDS['sig0deathUpperBound'])
    parent.sig0deathUpperBound.setRange(0.001, np.inf)
    parent.sig0deathUpperBound.valueChanged.connect \
        (parent.sig0deathSlider.setMaximum)
    parent.sig0deathUpperBound.valueChanged.connect \
        (parent.c1_event_handler.handle_upper_bound_changed)

    # add widgets to "undivided" groupbox layout
    _layout_prolif.addWidget(QLabel("<p>&mu;<sub>div</sub></p>"), 0, 0)
    _layout_prolif.addWidget(parent.mu0divSlider, 0, 1)
    _layout_prolif.addWidget(parent.mu0divUpperBound, 0, 2)
    _layout_prolif.addWidget(parent.mu0div, 0, 3)
    _layout_prolif.addWidget(parent.mu0divLock, 0, 4)
    _layout_prolif.addWidget(QLabel("<p>&sigma;<sub>div</sub></p>"), 1, 0)
    _layout_prolif.addWidget(parent.sig0divSlider, 1, 1)
    _layout_prolif.addWidget(parent.sig0divUpperBound, 1, 2)
    _layout_prolif.addWidget(parent.sig0div, 1, 3)
    _layout_prolif.addWidget(parent.sig0divLock, 1, 4)
    _layout_prolif.setContentsMargins(1, 3, 3, 3)
    _layout_prolif.setSpacing(5)

    _layout_death.addWidget(QLabel("<p>&mu;<sub>die</sub></p>"), 0, 0)
    _layout_death.addWidget(parent.mu0deathSlider, 0, 1)
    _layout_death.addWidget(parent.mu0deathUpperBound, 0, 2)
    _layout_death.addWidget(parent.mu0death, 0, 3)
    _layout_death.addWidget(parent.mu0deathLock, 0, 4)
    _layout_death.addWidget(QLabel("<p>&sigma;<sub>die</sub></p>"), 1, 0)
    _layout_death.addWidget(parent.sig0deathSlider, 1, 1)
    _layout_death.addWidget(parent.sig0deathUpperBound, 1, 2)
    _layout_death.addWidget(parent.sig0death, 1, 3)
    _layout_death.addWidget(parent.sig0deathLock, 1, 4)
    _layout_death.setContentsMargins(1, 3, 3, 3)
    _layout_death.setSpacing(5)

    group_box_prolif.setLayout(_layout_prolif)
    group_box_death.setLayout(_layout_death)

    _master_layout.addWidget(group_box_prolif)
    _master_layout.addWidget(group_box_death)
    _master_layout.setContentsMargins(5, 5, 5, 5)

    group_box.setLayout(_master_layout)
    return group_box


def create_dividing_layout(parent):
    group_box = QGroupBox("Subsequent Division")
    group_box_prolif = QGroupBox("Proliferation")
    group_box_prolif.setAlignment(4)
    group_box_death = QGroupBox("Death")
    group_box_death.setAlignment(4)
    _master_layout = QVBoxLayout()
    _layout_prolif = QGridLayout()
    _layout_death = QGridLayout()

    ############################################################
    #   Dividing cells (subsequent division) - MU - DIVIDE
    #       muSubdiv
    ############################################################
    parent.muSubdiv.setRange(0.001, np.inf)
    parent.muSubdiv.setDecimals(3)
    parent.muSubdiv.setObjectName("muSubdiv")
    parent.muSubdiv.setValue(gvars.C1_PARAMS['muSubdiv'])
    parent.muSubdiv.valueChanged.connect \
        (parent.c1_event_handler.handle_param_value_changed)

    parent.muSubdivLock.setObjectName("muSubdivLock")
    parent.muSubdivLock.toggled.connect \
        (lambda: parent.c1_event_handler.handle_lock_button_state(parent.muSubdivLock))

    parent.muSubdivSlider.setRange(0, 100)
    parent.muSubdivSlider.setValue(gvars.C1_PARAMS['muSubdiv'])
    parent.muSubdivSlider.setTickPosition(2)
    parent.muSubdivSlider.setTickInterval(2000)
    parent.muSubdivSlider.setObjectName('muSubdivSlider')
    parent.muSubdivSlider.valueChanged.connect \
        (lambda: parent.c1_event_handler.handle_double_slider(parent.muSubdiv))
    parent.muSubdiv.valueChanged.connect \
        (parent.muSubdivSlider.setValue)

    parent.muSubdivUpperBound.setObjectName("muSubdivUpperBound")
    parent.muSubdivUpperBound.setDecimals(3)
    parent.muSubdivUpperBound.setRange(0.001, np.inf)
    parent.muSubdivUpperBound.setValue(gvars.C1_UPPER_BOUNDS['muSubdivUpperBound'])
    parent.muSubdivUpperBound.setButtonSymbols(2)
    parent.muSubdivUpperBound.valueChanged.connect \
        (parent.muSubdivSlider.setMaximum)
    parent.muSubdivUpperBound.valueChanged.connect \
        (parent.c1_event_handler.handle_upper_bound_changed)

    ############################################################
    #   Dividing cells (subsequent division) - SIGMA - DIVIDE
    #       sigSubdiv
    ############################################################
    parent.sigSubdiv.setRange(0.001, np.inf)
    parent.sigSubdiv.setDecimals(3)
    parent.sigSubdiv.setObjectName("sigSubdiv")
    parent.sigSubdiv.setValue(gvars.C1_PARAMS['sigSubdiv'])
    parent.sigSubdiv.valueChanged.connect \
        (parent.c1_event_handler.handle_param_value_changed)

    parent.sigSubdivLock.setObjectName("sigSubdivLock")
    parent.sigSubdivLock.toggled.connect \
        (lambda: parent.c1_event_handler.handle_lock_button_state(parent.sigSubdivLock))

    parent.sigSubdivSlider.setRange(0.0, 1.0)
    parent.sigSubdivSlider.setValue(gvars.C1_PARAMS['sigSubdiv'])
    parent.sigSubdivSlider.setTickPosition(2)
    parent.sigSubdivSlider.setTickInterval(1000)
    parent.sigSubdivSlider.setObjectName('sigSubdivSlider')
    parent.sigSubdivSlider.valueChanged.connect \
        (lambda: parent.c1_event_handler.handle_double_slider(parent.sigSubdiv))
    parent.sigSubdiv.valueChanged.connect \
        (parent.sigSubdivSlider.setValue)

    parent.sigSubdivUpperBound.setObjectName("sigSubdivUpperBound")
    parent.sigSubdivUpperBound.setDecimals(3)
    parent.sigSubdivUpperBound.setButtonSymbols(2)
    parent.sigSubdivUpperBound.setValue(gvars.C1_UPPER_BOUNDS['sigSubdivUpperBound'])
    parent.sigSubdivUpperBound.setRange(0.001, np.inf)
    parent.sigSubdivUpperBound.valueChanged.connect \
        (parent.sigSubdivSlider.setMaximum)
    parent.sigSubdivUpperBound.valueChanged.connect \
        (parent.c1_event_handler.handle_upper_bound_changed)

    ############################################################
    #   Dividing cells (subsequent division) - MU - DEATH
    #       muSubdeath
    ############################################################
    parent.muSubdeath.setRange(0.001, np.inf)
    parent.muSubdeath.setDecimals(3)
    parent.muSubdeath.setObjectName("muSubdeath")
    parent.muSubdeath.setValue(gvars.C1_PARAMS['muSubdeath'])
    parent.muSubdeath.valueChanged.connect \
        (parent.c1_event_handler.handle_param_value_changed)

    parent.muSubdeathLock.setObjectName("muSubdeathLock")
    parent.muSubdeathLock.toggled.connect \
        (lambda: parent.c1_event_handler.handle_lock_button_state(parent.muSubdeathLock))

    parent.muSubdeathSlider.setRange(0, 100)
    parent.muSubdeathSlider.setValue(gvars.C1_PARAMS['muSubdeath'])
    parent.muSubdeathSlider.setTickPosition(2)
    parent.muSubdeathSlider.setTickInterval(2000)
    parent.muSubdeathSlider.setObjectName('muSubdeathSlider')
    parent.muSubdeathSlider.valueChanged.connect \
        (lambda: parent.c1_event_handler.handle_double_slider(parent.muSubdeath))
    parent.muSubdeath.valueChanged.connect \
        (parent.muSubdeathSlider.setValue)

    parent.muSubdeathUpperBound.setObjectName("muSubdeathUpperBound")
    parent.muSubdeathUpperBound.setDecimals(3)
    parent.muSubdeathUpperBound.setRange(0.001, np.inf)
    parent.muSubdeathUpperBound.setValue(gvars.C1_UPPER_BOUNDS['muSubdeathUpperBound'])
    parent.muSubdeathUpperBound.setButtonSymbols(2)
    parent.muSubdeathUpperBound.valueChanged.connect \
        (parent.muSubdeathSlider.setMaximum)
    parent.muSubdeathUpperBound.valueChanged.connect \
        (parent.c1_event_handler.handle_upper_bound_changed)

    ############################################################
    #   Dividing cells (subsequent division) - SIGMA - DEATH
    #       sigSubdeath
    ############################################################
    parent.sigSubdeath.setRange(0.001, np.inf)
    parent.sigSubdeath.setDecimals(3)
    parent.sigSubdeath.setObjectName("sigSubdeath")
    parent.sigSubdeath.setValue(gvars.C1_PARAMS['sigSubdeath'])
    parent.sigSubdeath.valueChanged.connect \
        (parent.c1_event_handler.handle_param_value_changed)

    parent.sigSubdeathLock.setObjectName("sigSubdeathLock")
    parent.sigSubdeathLock.toggled.connect \
        (lambda: parent.c1_event_handler.handle_lock_button_state(parent.sigSubdeathLock))

    parent.sigSubdeathSlider.setRange(0.0, 1.0)
    parent.sigSubdeathSlider.setValue(gvars.C1_PARAMS['sigSubdeath'])
    parent.sigSubdeathSlider.setTickPosition(2)
    parent.sigSubdeathSlider.setTickInterval(1000)
    parent.sigSubdeathSlider.setObjectName('sigSubdeathSlider')
    parent.sigSubdeathSlider.valueChanged.connect \
        (lambda: parent.c1_event_handler.handle_double_slider(parent.sigSubdeath))
    parent.sigSubdeath.valueChanged.connect(parent.sigSubdeathSlider.setValue)

    parent.sigSubdeathUpperBound.setObjectName("sigSubdeathUpperBound")
    parent.sigSubdeathUpperBound.setDecimals(3)
    parent.sigSubdeathUpperBound.setButtonSymbols(2)
    parent.sigSubdeathUpperBound.setValue(gvars.C1_UPPER_BOUNDS['sigSubdeathUpperBound'])
    parent.sigSubdeathUpperBound.setRange(0.001, np.inf)
    parent.sigSubdeathUpperBound.valueChanged.connect \
        (parent.sigSubdeathSlider.setMaximum)
    parent.sigSubdeathUpperBound.valueChanged.connect \
        (parent.c1_event_handler.handle_upper_bound_changed)

    _layout_prolif.addWidget(QLabel("<p>&mu;<sub>div</sub></p>"), 0, 0)
    _layout_prolif.addWidget(parent.muSubdivSlider, 0, 1)
    _layout_prolif.addWidget(parent.muSubdivUpperBound, 0, 2)
    _layout_prolif.addWidget(parent.muSubdiv, 0, 3)
    _layout_prolif.addWidget(parent.muSubdivLock, 0, 4)
    _layout_prolif.addWidget(QLabel("<p>&sigma;<sub>div</sub></p>"), 1, 0)
    _layout_prolif.addWidget(parent.sigSubdivSlider, 1, 1)
    _layout_prolif.addWidget(parent.sigSubdivUpperBound, 1, 2)
    _layout_prolif.addWidget(parent.sigSubdiv, 1, 3)
    _layout_prolif.addWidget(parent.sigSubdivLock, 1, 4)
    _layout_prolif.setContentsMargins(3, 3, 3, 3)
    _layout_prolif.setSpacing(5)

    _layout_death.addWidget(QLabel("<p>&mu;<sub>die</sub></p>"), 0, 0)
    _layout_death.addWidget(parent.muSubdeathSlider, 0, 1)
    _layout_death.addWidget(parent.muSubdeathUpperBound, 0, 2)
    _layout_death.addWidget(parent.muSubdeath, 0, 3)
    _layout_death.addWidget(parent.muSubdeathLock, 0, 4)
    _layout_death.addWidget(QLabel("<p>&sigma;<sub>die</sub></p>"), 1, 0)
    _layout_death.addWidget(parent.sigSubdeathSlider, 1, 1)
    _layout_death.addWidget(parent.sigSubdeathUpperBound, 1, 2)
    _layout_death.addWidget(parent.sigSubdeath, 1, 3)
    _layout_death.addWidget(parent.sigSubdeathLock, 1, 4)
    _layout_death.setContentsMargins(3, 3, 3, 3)
    _layout_death.setSpacing(5)

    group_box_prolif.setLayout(_layout_prolif)
    group_box_death.setLayout(_layout_death)

    _master_layout.addWidget(group_box_prolif)
    _master_layout.addWidget(group_box_death)
    _master_layout.setContentsMargins(5, 5, 5, 5)

    group_box.setLayout(_master_layout)
    return group_box


def create_misc_layout(parent):
    group_box = QGroupBox("Miscellaneous")
    group_box_pf = QGroupBox("Progressor Fraction")
    group_box_pf.setAlignment(4)
    group_box_mech = QGroupBox("Mechanical Death")
    group_box_mech.setAlignment(4)

    _layout_pf = QGridLayout()
    _layout_mech = QGridLayout()
    _layout = QGridLayout()

    ############################################################
    #   Progress fraction div0 -> div1
    #       pf0
    ############################################################
    parent.pf0.setRange(0.0, 1.0)
    parent.pf0.setDecimals(3)
    parent.pf0.setObjectName("pf0")
    parent.pf0.setValue(gvars.C1_PARAMS['pf0'])
    parent.pf0.setSingleStep(0.01)
    parent.pf0.valueChanged.connect \
        (parent.c1_event_handler.handle_param_value_changed)

    parent.pf0Lock.setObjectName("pf0Lock")
    parent.pf0Lock.toggled.connect \
        (lambda: parent.c1_event_handler.handle_lock_button_state(parent.pf0Lock))

    parent.pf0Slider.setRange(0.0, 1.0)
    parent.pf0Slider.setValue(gvars.C1_PARAMS['pf0'])
    parent.pf0Slider.setTickPosition(2)
    parent.pf0Slider.setTickInterval(1000)
    parent.pf0Slider.setObjectName('pf0Slider')
    parent.pf0Slider.valueChanged.connect \
        (lambda: parent.c1_event_handler.handle_double_slider(parent.pf0))
    parent.pf0.valueChanged.connect \
        (parent.pf0Slider.setValue)

    parent.pf0UpperBound.setObjectName("pf0UpperBound")
    parent.pf0UpperBound.setDecimals(3)
    parent.pf0UpperBound.setButtonSymbols(2)
    parent.pf0UpperBound.setValue(gvars.C1_UPPER_BOUNDS['pf0UpperBound'])
    parent.pf0UpperBound.setRange(0.0, 1.0)
    parent.pf0UpperBound.valueChanged.connect \
        (parent.pf0Slider.setMaximum)
    parent.pf0UpperBound.valueChanged.connect \
        (parent.c1_event_handler.handle_upper_bound_changed)

    ############################################################
    #   Progress fraction - MU - subsequent division
    #       pfmu
    ############################################################
    parent.pfmu.setRange(0.0, np.inf)
    parent.pfmu.setDecimals(3)
    parent.pfmu.setObjectName("pfmu")
    parent.pfmu.setValue(gvars.C1_PARAMS['pfmu'])
    parent.pfmu.setSingleStep(1.0)
    parent.pfmu.valueChanged.connect \
        (parent.c1_event_handler.handle_param_value_changed)

    parent.pfmuLock.setObjectName("pfmuLock")
    parent.pfmuLock.toggled.connect \
        (lambda: parent.c1_event_handler.handle_lock_button_state(parent.pfmuLock))

    parent.pfmuSlider.setRange(0.0, 50.0)
    parent.pfmuSlider.setValue(gvars.C1_PARAMS['pfmu'])
    parent.pfmuSlider.setTickPosition(2)
    parent.pfmuSlider.setTickInterval(2000)
    parent.pfmuSlider.setObjectName('pfmuSlider')
    parent.pfmuSlider.valueChanged.connect \
        (lambda: parent.c1_event_handler.handle_double_slider(parent.pfmu))
    parent.pfmu.valueChanged.connect \
        (parent.pfmuSlider.setValue)

    parent.pfmuUpperBound.setObjectName("pfmuUpperBound")
    parent.pfmuUpperBound.setDecimals(3)
    parent.pfmuUpperBound.setButtonSymbols(2)
    parent.pfmuUpperBound.setValue(gvars.C1_UPPER_BOUNDS['pfmuUpperBound'])
    parent.pfmuUpperBound.setRange(0.0, np.inf)
    parent.pfmuUpperBound.valueChanged.connect \
        (parent.pfmuSlider.setMaximum)
    parent.pfmuUpperBound.valueChanged.connect \
        (parent.c1_event_handler.handle_upper_bound_changed)

    ############################################################
    #   Progress fraction - SIGMA - subsequent division
    #       pfsig
    ############################################################
    parent.pfsig.setRange(0.001, np.inf)
    parent.pfsig.setDecimals(3)
    parent.pfsig.setObjectName("pfsig")
    parent.pfsig.setValue(gvars.C1_PARAMS['pfsig'])
    parent.pfsig.setSingleStep(0.1)
    parent.pfsig.valueChanged.connect \
        (parent.c1_event_handler.handle_param_value_changed)

    parent.pfsigLock.setObjectName("pfsigLock")
    parent.pfsigLock.toggled.connect \
        (lambda: parent.c1_event_handler.handle_lock_button_state(parent.pfsigLock))

    parent.pfsigSlider.setRange(0.0, 5.0)
    parent.pfsigSlider.setValue(gvars.C1_PARAMS['pfsig'])
    parent.pfsigSlider.setTickPosition(2)
    parent.pfsigSlider.setTickInterval(1000)
    parent.pfsigSlider.setObjectName('pfsigSlider')
    parent.pfsigSlider.valueChanged.connect \
        (lambda: parent.c1_event_handler.handle_double_slider(parent.pfsig))
    parent.pfsig.valueChanged.connect \
        (parent.pfsigSlider.setValue)

    parent.pfsigUpperBound.setObjectName("pfsigUpperBound")
    parent.pfsigUpperBound.setDecimals(3)
    parent.pfsigUpperBound.setButtonSymbols(2)
    parent.pfsigUpperBound.setValue(gvars.C1_UPPER_BOUNDS['pfsigUpperBound'])
    parent.pfsigUpperBound.setRange(0.001, np.inf)
    parent.pfsigUpperBound.valueChanged.connect \
        (parent.pfsigSlider.setMaximum)
    parent.pfsigUpperBound.valueChanged.connect \
        (parent.c1_event_handler.handle_upper_bound_changed)

    _layout_pf.addWidget(QLabel("pf0"), 0, 0)
    _layout_pf.addWidget(parent.pf0Slider, 0, 1)
    _layout_pf.addWidget(parent.pf0UpperBound, 0, 2)
    _layout_pf.addWidget(parent.pf0, 0, 3)
    _layout_pf.addWidget(parent.pf0Lock, 0, 4)
    _layout_pf.addWidget(QLabel("<p>&mu;<sub>pf</sub></p>"), 1, 0)
    _layout_pf.addWidget(parent.pfmuSlider, 1, 1)
    _layout_pf.addWidget(parent.pfmuUpperBound, 1, 2)
    _layout_pf.addWidget(parent.pfmu, 1, 3)
    _layout_pf.addWidget(parent.pfmuLock, 1, 4)
    _layout_pf.addWidget(QLabel("<p>&sigma;<sub>pf</sub></p>"), 2, 0)
    _layout_pf.addWidget(parent.pfsigSlider, 2, 1)
    _layout_pf.addWidget(parent.pfsigUpperBound, 2, 2)
    _layout_pf.addWidget(parent.pfsig, 2, 3)
    _layout_pf.addWidget(parent.pfsigLock, 2, 4)
    _layout_pf.setContentsMargins(3, 3, 3, 3)
    _layout_pf.setSpacing(5)

    group_box_pf.setLayout(_layout_pf)

    ############################################################
    #   Mechanical death proportion
    #       MechProp
    ############################################################
    parent.MechProp.setRange(0.0, 1.0)
    parent.MechProp.setDecimals(2)
    parent.MechProp.setObjectName("MechProp")
    parent.MechProp.setValue(gvars.C1_PARAMS['MechProp'])
    parent.MechProp.setSingleStep(0.01)
    parent.MechProp.valueChanged.connect \
        (parent.c1_event_handler.handle_param_value_changed)

    parent.MechPropLock.setObjectName("MechPropLock")
    parent.MechPropLock.toggled.connect \
        (lambda: parent.c1_event_handler.handle_lock_button_state(parent.MechPropLock))

    parent.MechPropSlider.setRange(0.0, 1.0)
    parent.MechPropSlider.setValue(gvars.C1_PARAMS['MechProp'])
    parent.MechPropSlider.setTickPosition(2)
    parent.MechPropSlider.setTickInterval(1000)
    parent.MechPropSlider.setObjectName('MechPropSlider')
    parent.MechPropSlider.valueChanged.connect \
        (lambda: parent.c1_event_handler.handle_double_slider(parent.MechProp))
    parent.MechProp.valueChanged.connect \
        (parent.MechPropSlider.setValue)

    parent.MechPropUpperBound.setObjectName("MechPropUpperBound")
    parent.MechPropUpperBound.setButtonSymbols(2)
    parent.MechPropUpperBound.setValue(gvars.C1_UPPER_BOUNDS['MechPropUpperBound'])
    parent.MechPropUpperBound.setRange(0.0, 1.0)
    parent.MechPropUpperBound.valueChanged.connect \
        (parent.MechPropSlider.setMaximum)
    parent.MechPropUpperBound.valueChanged.connect \
        (parent.c1_event_handler.handle_upper_bound_changed)

    ############################################################
    #   Mechanical death decay constant
    #       MechDecayConst
    ############################################################
    parent.MechDecayConst.setRange(0.0, 1.0)
    parent.MechDecayConst.setDecimals(2)
    parent.MechDecayConst.setObjectName("MechDecayConst")
    parent.MechDecayConst.setValue(gvars.C1_PARAMS['MechDecayConst'])
    parent.MechDecayConst.setSingleStep(0.01)
    parent.MechDecayConst.valueChanged.connect \
        (parent.c1_event_handler.handle_param_value_changed)

    parent.MechDecayConstLock.setObjectName("MechDecayConstLock")
    parent.MechDecayConstLock.toggled.connect \
        (lambda: parent.c1_event_handler.handle_lock_button_state(parent.MechDecayConstLock))

    parent.MechDecayConstSlider.setRange(0.0, 1.0)
    parent.MechDecayConstSlider.setValue(gvars.C1_PARAMS['MechDecayConst'])
    parent.MechDecayConstSlider.setTickPosition(2)
    parent.MechDecayConstSlider.setTickInterval(1000)
    parent.MechDecayConstSlider.setObjectName('MechDecayConstSlider')
    parent.MechDecayConstSlider.valueChanged.connect \
        (lambda: parent.c1_event_handler.handle_double_slider(parent.MechDecayConst))
    parent.MechDecayConst.valueChanged.connect \
        (parent.MechDecayConstSlider.setValue)

    parent.MechDecayConstUpperBound.setObjectName("MechDecayConstUpperBound")
    parent.MechDecayConstUpperBound.setButtonSymbols(2)
    parent.MechDecayConstUpperBound.setValue(gvars.C1_UPPER_BOUNDS['MechDecayConstUpperBound'])
    parent.MechDecayConstUpperBound.setRange(0.0, 1.0)
    parent.MechDecayConstUpperBound.valueChanged.connect \
        (parent.MechDecayConstSlider.setMaximum)
    parent.MechDecayConstUpperBound.valueChanged.connect \
        (parent.c1_event_handler.handle_upper_bound_changed)

    _layout_mech.addWidget(QLabel("Prop."), 0, 0)
    _layout_mech.addWidget(parent.MechPropSlider, 0, 1)
    _layout_mech.addWidget(parent.MechPropUpperBound, 0, 2)
    _layout_mech.addWidget(parent.MechProp, 0, 3)
    _layout_mech.addWidget(parent.MechPropLock, 0, 4)
    _layout_mech.addWidget(QLabel("Decay"), 1, 0)
    _layout_mech.addWidget(parent.MechDecayConstSlider, 1, 1)
    _layout_mech.addWidget(parent.MechDecayConstUpperBound, 1, 2)
    _layout_mech.addWidget(parent.MechDecayConst, 1, 3)
    _layout_mech.addWidget(parent.MechDecayConstLock, 1, 4)
    _layout_mech.setContentsMargins(3, 3, 3, 3)
    _layout_mech.setSpacing(5)

    group_box_mech.setLayout(_layout_mech)

    _layout.addWidget(group_box_pf)
    _layout.addWidget(group_box_mech)
    _layout.setContentsMargins(5, 5, 5, 5)
    group_box.setLayout(_layout)

    return group_box