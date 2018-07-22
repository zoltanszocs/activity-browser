from ..style import horizontal_line, vertical_line, header
from ..tables import LCAResultsTable
from ..tables.lca_results import InventoryTable
from ..graphics import (
    LCAResultsPlot,
    ProcessContributionPlot,
    ElementaryFlowContributionPlot,
    CorrelationPlot,
)
from ...bwutils.multilca import MLCA
from ...bwutils import commontasks as bc


from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QRadioButton, QSlider, \
    QLabel, QLineEdit, QCheckBox, QPushButton, QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator

from ...signals import signals

# TODO: fix box-in-box of the main space

# TODO: add functionality for actually changing cutoff

class CalculationSetupTab(QTabWidget):
    def __init__(self, parent, name):
        super(CalculationSetupTab, self).__init__(parent)
        self.panel = parent  # e.g. right panel
        self.setup_name = name
        self.method_dict = dict()

        self.setVisible(False)
        self.visible = False

        self.setTabShape(1)  # Triangular-shaped Tabs
        self.setTabPosition(1)  # South-facing Tabs

        self.lcia_results_tab = LCIAAnalysis(self)
        self.process_contributions_tab = ProcessContributions(self)
        self.elementary_flows_tab = ElementaryFlowContributions(self)
        self.correlations_tab = Correlations(self)
        self.inventory_tab = Inventory(self)

        self.update_setup()
        self.connect_signals()

    def connect_signals(self):
        pass

    def update_setup(self):
        self.mlca = MLCA(self.setup_name)
        self.method_dict = bc.get_LCIA_method_name_dict(self.mlca.methods)

        self.lcia_results_tab.update_analysis_tab()

        self.process_contributions_tab.update_analysis_tab()

        self.elementary_flows_tab.update_analysis_tab()

        self.correlations_tab.update_analysis_tab()

        self.inventory_tab.update_analysis_tab()

class AnalysisTab(QWidget):
    def __init__(self, parent, cutoff=None, combobox=None, table=None, plot=None, export=None):
        super(AnalysisTab, self).__init__(parent)
        self.setup = parent

        self.cutoff_menu = cutoff
        self.combobox_menu_combobox = combobox
        self.table = table
        self.plot = plot
        self.export_menu = export

        self.name = str()
        self.header = header(self.name)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(self.header)
        self.layout.addWidget(horizontal_line())

    def connect_analysis_signals(self):
        # Cut-off
        if self.cutoff_menu:
            # Cut-off types
            self.cutoff_type_topx.clicked.connect(self.cutoff_type_topx_check)
            self.cutoff_type_relative.clicked.connect(self.cutoff_type_relative_check)

            # Cut-off slider
            self.cutoff_slider_slider.valueChanged.connect(
                lambda: self.cutoff_slider_check("S"))
            self.cutoff_slider_line.textChanged.connect(
                lambda: self.cutoff_slider_check("L"))

        # Combo box signal
        if self.combobox_menu_combobox != None:
            self.combobox_menu_combobox.currentTextChanged.connect(
                lambda name: self.update_plot(method=name))

        # Mainspace Checkboxes
        self.main_space_tb_grph_table.stateChanged.connect(
            lambda: self.main_space_check(self.main_space_tb_grph_table, self.main_space_tb_grph_plot))
        self.main_space_tb_grph_plot.stateChanged.connect(
            lambda: self.main_space_check(self.main_space_tb_grph_table, self.main_space_tb_grph_plot))

        # Export Table
        if self.table and self.export_menu:
            self.export_table_buttons_copy.clicked.connect(self.table.to_clipboard)
            self.export_table_buttons_csv.clicked.connect(self.table.to_csv)
            self.export_table_buttons_excel.clicked.connect(self.table.to_excel)

        # Export Plot
        if self.plot and self.export_menu:
            self.export_plot_buttons_png.clicked.connect(self.plot.to_png)
            self.export_plot_buttons_svg.clicked.connect(self.plot.to_svg)

    def cutoff_type_relative_check(self):
        """ Work in progress. """
        # set cutoff to some %
        self.cutoff_slider_unit.setText("relative selected, functionality to be added later")

    def cutoff_type_topx_check(self):
        """ Work in progress. """
        # set cutoff to some number
        self.cutoff_slider_unit.setText("top # selected, functionality to be added later")


    def cutoff_slider_check(self, editor):
        cutoff = int
        if editor == "S":
            cutoff = abs(int(self.cutoff_slider_slider.value()))
            self.cutoff_slider_line.setText(str(cutoff))
        elif editor == "L":
            if self.cutoff_slider_line.text() == '-':
                cutoff = self.cutoff_slider_slider.minimum()
                self.cutoff_slider_line.setText(str(self.cutoff_slider_slider.minimum()))
            elif self.cutoff_slider_line.text() == '':
                cutoff = self.cutoff_slider_slider.minimum()
            else:
                cutoff = abs(int(self.cutoff_slider_line.text()))

            if cutoff > self.cutoff_slider_slider.maximum():
                cutoff = self.cutoff_slider_slider.maximum()
                self.cutoff_slider_line.setText(str(cutoff))
            self.cutoff_slider_slider.setValue(int(cutoff))
        self.cutoff_value = cutoff

    def main_space_check(self, table_ch, plot_ch):
        table_state = table_ch.isChecked()
        plot_state = plot_ch.isChecked()

        if table_state and plot_state:
            self.main_space_table.setVisible(True)
            self.main_space_plot.setVisible(True)

        elif not table_state and plot_state:
            self.main_space_table.setVisible(False)
            self.main_space_plot.setVisible(True)

        else:
            self.main_space_tb_grph_table.setChecked(True)
            self.main_space_table.setVisible(True)
            self.main_space_plot.setVisible(False)

    def update_analysis_tab(self):
        if self.table:
            self.update_table()
        if self.plot:
            self.update_plot()
        if self.combobox_menu_combobox != None:
            self.update_combobox()

    def update_table(self):
        self.table.sync(self.setup.mlca)

    def update_combobox(self):
        self.combobox_menu_combobox.clear()
        self.combobox_list = list(self.setup.method_dict.keys())
        self.combobox_menu_combobox.insertItems(0, self.combobox_list)

    def add_cutoff(self):
        self.cutoff_menu = QHBoxLayout()

        # Cut-off types
        self.cutoff_type = QVBoxLayout()
        self.cutoff_type_label = QLabel("Cut-off type")
        self.cutoff_type_relative = QRadioButton("Relative")
        self.cutoff_type_relative.setChecked(True)
        self.cutoff_type_topx = QRadioButton("Top #")

        # Cut-off slider
        self.cutoff_slider = QVBoxLayout()
        self.cutoff_slider_set = QVBoxLayout()
        self.cutoff_slider_label = QLabel("Cut-off level")
        self.cutoff_slider_slider = QSlider(Qt.Horizontal)
        self.cutoff_slider_slider.setMinimum(1)  # temporary
        self.cutoff_slider_slider.setMaximum(99)  # temporary
        self.cutoff_slider_slider.sizeHint()
        self.cutoff_slider_minmax = QHBoxLayout()
        self.cutoff_slider_min = QLabel(str(self.cutoff_slider_slider.minimum()))
        self.cutoff_slider_max = QLabel(str(self.cutoff_slider_slider.maximum()))
        self.cutoff_slider_ledit = QHBoxLayout()
        self.cutoff_slider_line = QLineEdit()
        self.cutoff_validator = QIntValidator(self.cutoff_slider_line)
        self.cutoff_slider_line.setValidator(self.cutoff_validator)
        self.cutoff_value = int()  # set to max when known how to port data to this class
        self.cutoff_slider_unit = QLabel("unit")

        # Assemble types
        self.cutoff_type.addWidget(self.cutoff_type_label)
        self.cutoff_type.addWidget(self.cutoff_type_relative)
        self.cutoff_type.addWidget(self.cutoff_type_topx)

        # Assemble slider set
        self.cutoff_slider_set.addWidget(self.cutoff_slider_label)
        self.cutoff_slider_set.addWidget(self.cutoff_slider_slider)
        self.cutoff_slider_minmax.addWidget(self.cutoff_slider_min)
        self.cutoff_slider_minmax.addStretch()
        self.cutoff_slider_minmax.addWidget(self.cutoff_slider_max)
        self.cutoff_slider_set.addLayout(self.cutoff_slider_minmax)

        self.cutoff_slider_ledit.addWidget(self.cutoff_slider_line)
        self.cutoff_slider_ledit.addWidget(self.cutoff_slider_unit)
        self.cutoff_slider_ledit.addStretch(1)

        self.cutoff_slider.addLayout(self.cutoff_slider_set)
        self.cutoff_slider.addLayout(self.cutoff_slider_ledit)

        # Assemble cut-off menu
        self.cutoff_menu.addLayout(self.cutoff_type)
        self.cutoff_menu.addWidget(vertical_line())
        self.cutoff_menu.addLayout(self.cutoff_slider)
        self.cutoff_menu.addStretch()

        self.layout.addLayout(self.cutoff_menu)
        self.layout.addWidget(horizontal_line())

    def add_combobox(self):
        self.combobox_menu = QHBoxLayout()

        self.combobox_menu_label = QLabel("Assesment method: ")
        self.combobox_menu_combobox = QComboBox()
        self.combobox_menu_combobox.scroll = False

        self.combobox_menu.addWidget(self.combobox_menu_label)
        self.combobox_menu.addWidget(self.combobox_menu_combobox, 1)
        self.combobox_menu.addStretch(1)

        self.layout.addLayout(self.combobox_menu)
        self.layout.addWidget(horizontal_line())

    def add_main_space(self):
        # Generate Table and Plot area
        self.main_space = QScrollArea()
        self.main_space_widget = QWidget()
        self.main_space_widget_layout = QVBoxLayout()
        self.main_space_widget.setLayout(self.main_space_widget_layout)
        self.main_space.setWidget(self.main_space_widget)
        self.main_space.setWidgetResizable(True)
        # Option switch
        self.main_space_tb_grph = QHBoxLayout()
        self.main_space_tb_grph_plot = QCheckBox("Plot")
        self.main_space_tb_grph_plot.setChecked(True)
        self.main_space_tb_grph_table = QCheckBox("Table")
        self.main_space_tb_grph_table.setChecked(True)
        # Plot
        self.main_space_plot = self.plot
        # Table
        self.main_space_table = self.table

        # Assemble option switch
        self.main_space_tb_grph.addWidget(self.main_space_tb_grph_plot)
        self.main_space_tb_grph.addWidget(self.main_space_tb_grph_table)
        self.main_space_tb_grph.addStretch()

        # Assemble Table and Plot area
        if self.table and self.plot:
            self.main_space_widget_layout.addLayout(self.main_space_tb_grph)
        if self.plot:
            self.main_space_widget_layout.addWidget(self.main_space_plot, 1)
        if self.table:
            self.main_space_widget_layout.addWidget(self.main_space_table)
        self.main_space_widget_layout.addStretch()

        self.layout.addWidget(self.main_space)

    def add_export(self):
        self.export_menu = QHBoxLayout()

        # Export Plot
        self.export_plot = QVBoxLayout()
        self.export_plot_label = QLabel("Export plot")
        self.export_plot_buttons = QHBoxLayout()
        self.export_plot_buttons_png = QPushButton(".png")
        self.export_plot_buttons_svg = QPushButton(".svg")
        # Export Table
        self.export_table = QVBoxLayout()
        self.export_table_label = QLabel("Export table")
        self.export_table_buttons = QHBoxLayout()
        self.export_table_buttons_copy = QPushButton("Copy")
        self.export_table_buttons_csv = QPushButton(".csv")
        self.export_table_buttons_excel = QPushButton("Excel")

        # Assemble export plot
        self.export_plot.addWidget(self.export_plot_label)
        self.export_plot_buttons.addWidget(self.export_plot_buttons_png)
        self.export_plot_buttons.addWidget(self.export_plot_buttons_svg)
        self.export_plot.addLayout(self.export_plot_buttons)

        # Assemble export table
        self.export_table.addWidget(self.export_table_label)
        self.export_table_buttons.addWidget(self.export_table_buttons_copy)
        self.export_table_buttons.addWidget(self.export_table_buttons_csv)
        self.export_table_buttons.addWidget(self.export_table_buttons_excel)
        self.export_table.addLayout(self.export_table_buttons)

        # Assemble export menu
        if self.plot:
            self.export_menu.addLayout(self.export_plot)
        if self.table and self.plot:
            self.export_menu_vert_line = vertical_line()
            self.export_menu.addWidget(self.export_menu_vert_line)
        if self.table:
            self.export_menu.addLayout(self.export_table)
        self.export_menu.addStretch()

        self.layout.addWidget(horizontal_line())
        self.layout.addLayout(self.export_menu)

class LCIAAnalysis(AnalysisTab):
    def __init__(self, parent):
        super(LCIAAnalysis, self).__init__(parent)
        self.setup = parent

        self.name = "LCIA Results"
        self.header.setText(self.name)

        self.table = LCAResultsTable()
        self.plot = LCAResultsPlot(self.setup)

        self.add_cutoff()
        self.add_main_space()
        self.add_export()

        self.setup.addTab(self, self.name)

        self.connect_analysis_signals()

    def update_plot(self):
        self.plot.plot(self.setup.mlca)

class ProcessContributions(AnalysisTab):
    def __init__(self, parent):
        super(ProcessContributions, self).__init__(parent)
        self.setup = parent

        self.name = "Process Contributions"
        self.header.setText(self.name)

        self.plot = ProcessContributionPlot(self.setup)

        self.add_cutoff()
        self.add_combobox()
        self.add_main_space()
        self.add_export()

        self.setup.addTab(self, self.name)

        self.connect_analysis_signals()

    def update_plot(self, method=None):
        if method == None:
            method = self.setup.mlca.methods[0]
        else:
            method = self.setup.method_dict[method]
        self.plot.plot(self.setup.mlca, method=method)

class ElementaryFlowContributions(AnalysisTab):
    def __init__(self, parent):
        super(ElementaryFlowContributions, self).__init__(parent)
        self.setup = parent

        self.name = "Elementary Flow Contributions"
        self.header.setText(self.name)

        self.plot = ElementaryFlowContributionPlot(self.setup)

        self.add_cutoff()
        self.add_combobox()
        self.add_main_space()
        self.add_export()

        self.setup.addTab(self, self.name)

        self.connect_analysis_signals()

    def update_plot(self, method=None):
        if method == None:
            method = self.setup.mlca.methods[0]
        else:
            method = self.setup.method_dict[method]
        self.plot.plot(self.setup.mlca, method=method)

class Correlations(AnalysisTab):
    def __init__(self, parent):
        super(Correlations, self).__init__(parent)
        self.setup = parent

        self.name = "Correlations"
        self.header.setText(self.name)

        self.plot = CorrelationPlot(self.setup)

        self.add_main_space()
        self.add_export()

        self.setup.addTab(self, self.name)

        self.connect_analysis_signals()

    def update_plot(self):
        labels = [str(x + 1) for x in range(len(self.setup.mlca.func_units))]
        self.plot.plot(self.setup.mlca, labels)

class Inventory(AnalysisTab):
    def __init__(self, parent):
        super(Inventory, self).__init__(parent)
        self.setup = parent

        self.name = "Inventory"
        self.header.setText(self.name)

        self.table = InventoryTable(self.setup)

        self.add_main_space()
        self.add_export()

        self.setup.addTab(self, self.name)

        self.connect_analysis_signals()
