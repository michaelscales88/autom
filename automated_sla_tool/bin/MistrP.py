import os, sys
from collections import namedtuple
import pyexcel as pe
from PyQt5.QtCore import (pyqtSignal, QSize,
                          Qt)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QAction,
                             qApp, QToolBar, QDesktopWidget,
                             QMessageBox, QApplication, QTabWidget,
                             QTabBar, QMenu, QToolButton,
                             QStyleFactory)
from automated_sla_tool.src import (SettingsWidget, TableWidget, ProcessMenu)


# TODO: fix this shit
# Need to fix Scatterplotitem>Opts = False-> True ** changed to fix qpixmap error **

class MainFrame(QMainWindow):
    application_color = pyqtSignal(str, name='selected color')
    application_font = pyqtSignal(QFont, name='selected font')
    application_style = pyqtSignal(str, name='application style')

    def __init__(self, parent=None):
        super(MainFrame, self).__init__(parent)

        # Main Frame widget
        self.te = QTextEdit(self)
        self.main_widget = self.main_widget_factory()
        self.setCentralWidget(self.main_widget)

        (self.global_constants,
         self.local_constants) = self.constants_factory()

        self.settings_button = self.settings_button_factory()

        self.status_bar()

        # Buttons
        self.report_button = QAction(QIcon(self.global_constants.GO_PIC), "Run Program", self)
        self.report_button.setShortcut('Ctrl+R')
        self.report_button.setStatusTip('Run SLA Program')
        self.report_button.triggered.connect(self.call_sla)

        self.sla_slicer_button = QAction(QIcon(self.global_constants.SEARCH_PIC), "Slicer", self)
        self.sla_slicer_button.setShortcut('Ctrl+S')
        self.sla_slicer_button.setStatusTip('Slice spreadsheets for a given date range.')
        self.sla_slicer_button.triggered.connect(self.sla_slicer)

        self.about_action = QAction("&About", self)
        self.about_action.setStatusTip('Information about this program')
        self.about_action.triggered.connect(self.about)

        self.about_qt_action = QAction("About &Qt", self)
        self.about_qt_action.setStatusTip('GUI application information')
        self.about_qt_action.triggered.connect(qApp.aboutQt)

        self.exit_action = QAction(QIcon(self.global_constants.QUIT_PIC), 'Exit', self)
        self.exit_action.setStatusTip('About Qt library')
        self.exit_action.triggered.connect(self.close)

        # Menus
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(self.report_button)
        file_menu.addAction(self.sla_slicer_button)
        file_menu.addAction(self.exit_action)

        about_menu = menu_bar.addMenu('&About')
        about_menu.addAction(self.about_action)
        about_menu.addAction(self.about_qt_action)

        # Toolbar
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(50, 50))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon | Qt.AlignLeading)
        self.addToolBar(Qt.LeftToolBarArea, toolbar)
        toolbar.addAction(self.report_button)
        toolbar.addAction(self.sla_slicer_button)
        toolbar.addWidget(self.settings_button)
        toolbar.addAction(self.exit_action)

        # Process Window Bindings
        self.sla_calendar = None
        self.sla_slicer = None

        self.reset_binding_dict = {'sla_report.py': 'sla_calendar',
                                   'MSSQLupdater': 'acc_calendar',
                                   'viewer': 'sv_calendar',
                                   'sla_slicer.py': 'sla_slicer'}

        # Main frame layout
        self.resize(1000, 500)
        self.center_frame()
        self.setWindowTitle('Mike\'s Streamlined Reporting Program')

    def center_frame(self):
        screen_dimensions = self.frameGeometry()
        center_dimensions = QDesktopWidget().availableGeometry().center()
        screen_dimensions.moveCenter(center_dimensions)
        self.move(screen_dimensions.topLeft())

    def about(self):
        QMessageBox.about(self,
                          "About MiStRP",
                          "Version 1.0\n"
                          "Developed by Michael Scales\n"
                          "Application to run python modules")

    def status_bar(self):
        self.statusBar().showMessage("Ready")

    def closeEvent(self, event):
        QApplication.quit()
        # if QMessageBox.question(None,
        #                         'Quit MiStRP?',
        #                         "Are you sure to quit?",
        #                         QMessageBox.Yes | QMessageBox.No,
        #                         QMessageBox.No) == QMessageBox.Yes:
        #     QApplication.quit()
        # else:
        #     event.ignore()

    def call_sla(self):
        if self.sla_calendar is None:
            self.sla_calendar = ProcessMenu(parent=self, process='sla_report.py')
            self.sla_calendar.exit_status.connect(self.reset_binding)
        else:
            self.sla_calendar.raise_()

    def sla_slicer(self):
        if self.sla_slicer is None:
            self.sla_slicer = ProcessMenu(parent=self, process='sla_slicer.py')
            self.sla_slicer.exit_status.connect(self.reset_binding)
        else:
            self.sla_slicer.raise_()

    def open_tab(self, args):
        for index in range(self.main_widget.count()):
            if self.main_widget.widget(index).windowTitle() == args.title:
                self.main_widget.setCurrentIndex(index)
                return
        tab = TableWidget(file=args.base, window_title=args.title)
        self.main_widget.addTab(tab, args.title)

    def close_tab(self, index):
        self.main_widget.widget(index).close()
        self.main_widget.removeTab(index)

    def reset_binding(self, process):
        setattr(self, self.reset_binding_dict[process], None)

    def write_to_central_widget(self, string_text):
        cursor = self.te.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(string_text)
        self.te.ensureCursorVisible()

    def main_widget_factory(self):
        main_widget = QTabWidget()
        main_widget.setTabsClosable(True)
        main_widget.tabCloseRequested[int].connect(self.close_tab)
        main_widget.addTab(self.te, "MiStRP")
        main_widget.tabBar().tabButton(0, QTabBar.RightSide).resize(0, 0)
        return main_widget

    def settings_button_factory(self):
        settings_path = r'{0}\settings'.format(self.global_constants.SELF_PATH)
        sla_client_dict_settings_args = self.local_constants(
            file=r'{}\report_settings.xlsx'.format(settings_path),
            title=r'SLA SETTINGS/Client Page'
        )
        sla_settings = QMenu("sla settings", self)
        sla_constants_action = QAction(QIcon(self.global_constants.SETTINGS_PIC), "SLA SETTINGS/CLIENT_DICT", self)
        sla_constants_action.triggered.connect(lambda: self.open_tab(sla_client_dict_settings_args))
        sla_settings.addAction(sla_constants_action)

        self_settings_args = self.local_constants(
            file=r'{}\misterp_settings.xlsx'.format(settings_path),
            title='MiStRP Settings/CONFIG'
        )
        self_settings = QMenu("MiStRP Settings", self)
        self_action = QAction(QIcon(self.global_constants.SETTINGS_PIC), "Self Settings", self)
        self_action.triggered.connect(lambda: self.open_tab(self_settings_args))
        self_settings.addAction(self_action)

        SettingMenu = QMenu()
        SettingMenu.addMenu(sla_settings)
        SettingMenu.addMenu(self_settings)

        SettingButton = QToolButton()
        SettingButton.setIcon(QIcon(self.global_constants.SETTINGS_PIC))
        tab = SettingsWidget(parent=self)
        tab.selected_color.connect(self.application_color.emit)
        tab.selected_font.connect(self.application_font.emit)
        tab.selected_style.connect(self.application_style.emit)
        SettingButton.clicked.connect(lambda: self.main_widget.addTab(tab, 'Display Settings'))
        SettingButton.setPopupMode(1)
        SettingButton.setMenu(SettingMenu)
        return SettingButton

    def constants_factory(self):
        Node = namedtuple('Node', 'title file')
        Node.__new__.__defaults__ = (None,) * len(Node._fields)
        constants = namedtuple('Node',
                               'SELF_PATH GO_PIC ACCUM_PIC QUIT_PIC SEARCH_PIC SETTINGS_PIC')
        constants.__new__.__defaults__ = (None,) * len(constants._fields)
        SELF_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        settings_path = r'{0}\settings'.format(SELF_PATH)
        constants_sheet = pe.get_sheet(file_name=r'{}\misterp_settings.xlsx'.format(settings_path),
                                       name_rows_by_column=0)
        constant_tuple = constants(SELF_PATH=SELF_PATH,
                                   GO_PIC=r'{0}\pics\{1}'.format(settings_path,
                                                                 constants_sheet['GO_PIC', 0]),
                                   ACCUM_PIC=r'{0}\pics\{1}'.format(settings_path,
                                                                    constants_sheet['ACCUM_PIC', 0]),
                                   QUIT_PIC=r'{0}\pics\{1}'.format(settings_path,
                                                                   constants_sheet['QUIT_PIC', 0]),
                                   SEARCH_PIC=r'{0}\pics\{1}'.format(settings_path,
                                                                     constants_sheet['SEARCH_PIC', 0]),
                                   SETTINGS_PIC=r'{0}\pics\{1}'.format(settings_path,
                                                                       constants_sheet['SETTINGS_PIC', 0]))
        return constant_tuple, Node


class MyApplication(QApplication):
    def __init__(self, argv):
        super(MyApplication, self).__init__(argv)
        self.clip = QApplication.clipboard()


def main():
    app = MyApplication(sys.argv)
    ex = MainFrame()
    ex.application_color.connect(app.setStyleSheet)
    ex.application_font.connect(app.setFont)
    ex.application_style.connect(lambda text: app.setStyle(QStyleFactory.create(text)))
    ex.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(path.abspath(__file__)))))
    main()
