import datetime
import pyexcel as pe
from collections import defaultdict
from PyQt5.QtWidgets import (
    QMainWindow,
    QDesktopWidget,
    QPushButton
)
from PyQt5.QtCore import (pyqtSignal, Qt)
from automated_sla_tool.src import (
    DockWidget,
    SplitterFrameWidget,
    ProcessObject,
    # ProcessWorker
)


class ProcessMenu(QMainWindow):
    exit_status = pyqtSignal(str, name='exit_status')
    save_items = pyqtSignal(defaultdict, name='save_items')
    return_save_info = pyqtSignal(defaultdict, name='return_save_info')
    progress_update = pyqtSignal(float, name='progress_made')
    tab_data = pyqtSignal(pe.sheets.sheet.Sheet, name='tab_data')

    def __init__(self, parent=None, process=None):
        super().__init__(parent)

        # Member Attributes
        self.process = self.init_process(process)

        # Bindings
        self.__excel_dock = ExcelDockWidget(self,
                                            excl_title='Excel Dock',
                                            excl_widget=self.process.get_data_widget(),
                                            excl_shw_btn='Show Excel')
        self.__buttons = ButtonsDockWidget(self,
                                           btn_title='Button Dock',
                                           prcs_widget=self.process.get_ui(),
                                           prcs_shw_btn='Show Buttons')
        self.__calendar_dock = CalendarDockWidget(self,
                                                  cal_title='Calendar Dock',
                                                  cal_one=self.process.get_cal_one(),
                                                  cal_two=self.process.get_cal_two(),
                                                  run_btn=QPushButton('Run Report'),
                                                  cal_shw_btn='Show Calendars')
        self.__save_dock = SaveDockWidget(self,
                                          save_title='File Saver Dock',
                                          save_widget=self.process.get_save_widget(),
                                          run_btn=QPushButton('Save'),
                                          save_shw_btn='Save Files')

        # Connections
        self.__calendar_dock.ready_to_send.connect(self.execute_process)
        self.tab_data.connect(self.process.add_data)

        # Widget Layout
        # splitter = SplitterFrameWidget(self,
        #                                widget1=self.process.get_progress_bar(),
        #                                widget2=self.process.get_err(),
        #                                orientation='Vertical',
        #                                arrow_direction='left')
        # self.setCentralWidget(splitter)
        self.addDockWidget(Qt.RightDockWidgetArea, self.__buttons)
        self.addDockWidget(Qt.RightDockWidgetArea, self.__save_dock)
        self.addDockWidget(Qt.TopDockWidgetArea, self.__excel_dock)
        self.addDockWidget(Qt.TopDockWidgetArea, self.__calendar_dock)
        self.tabifyDockWidget(self.__save_dock, self.__buttons)
        self.tabifyDockWidget(self.__excel_dock, self.__calendar_dock)

        # Display
        self.setDockOptions(QMainWindow.AnimatedDocks |
                            QMainWindow.AllowTabbedDocks |
                            QMainWindow.ForceTabbedDocks)
        self.center_frame()
        self.show()

    def init_process(self, proc):
        return ProcessObject(process=proc)

    def execute_process(self):
        print('Executing process...')
        # proc_worker = ProcessWorker(proc=self.process)
        # proc_worker.start()
        # proc_worker.transmit_report.connect(self.tab_data.emit)

    def closeEvent(self, event):
        self.exit_status.emit(self.process.get_name())
        event.accept()

    def center_frame(self):
        screen_dimensions = self.frameGeometry()
        center_dimensions = QDesktopWidget().availableGeometry().center()
        screen_dimensions.moveCenter(center_dimensions)
        self.move(screen_dimensions.topLeft())


class ButtonsDockWidget(DockWidget):
    def __init__(self, parent,
                 btn_title=None,
                 prcs_widget=None,
                 prcs_shw_btn=None):
        super().__init__(parent, window_name=btn_title, widget1=prcs_widget,
                         widget2=None, button=None, hide_button_name=prcs_shw_btn)


class CalendarDockWidget(DockWidget):
    calendar_date_range = pyqtSignal(datetime.date, datetime.date, name='calendar_date_range')
    ready_to_send = pyqtSignal(bool, name='ready_to_send')

    def __init__(self, parent,
                 cal_title=None,
                 cal_one=None,
                 cal_two=None,
                 run_btn=None,
                 cal_shw_btn=None):
        super().__init__(parent=parent, window_name=cal_title, widget1=cal_one,
                         widget2=cal_two, button=run_btn, hide_button_name=cal_shw_btn)
        run_btn.clicked.connect(self.close)
        run_btn.clicked.connect(self.ready_to_send.emit)


class ExcelDockWidget(DockWidget):
    tab_container_data = pyqtSignal(list, name='tab_container_data')

    def __init__(self, parent,
                 excl_title=None,
                 excl_widget=None,
                 excl_shw_btn=None):
        super().__init__(parent, window_name=excl_title, widget1=excl_widget,
                         widget2=None, button=None, hide_button_name=excl_shw_btn)
        excl_widget.emit_dict.connect(lambda stuff: self.tab_container_data.emit(stuff))


class SaveDockWidget(DockWidget):
    def __init__(self, parent,
                 save_title=None,
                 save_widget=None,
                 run_btn=None,
                 save_shw_btn=None):
        super().__init__(parent, window_name=save_title, widget1=save_widget,
                         widget2=None, button=run_btn, hide_button_name=save_shw_btn)
