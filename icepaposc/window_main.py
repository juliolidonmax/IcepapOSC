#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# This file is part of IcepapOCS link:
#        https://github.com/ALBA-Synchrotron/IcepapOCS
#
# Copyright 2017:
#       MAX IV Laboratory, Lund, Sweden
#       CELLS / ALBA Synchrotron, Bellaterra, Spain
#
# Distributed under the terms of the GNU General Public License,
# either version 3 of the License, or (at your option) any later version.
# See LICENSE.txt for more info.
#
# You should have received a copy of the GNU General Public License
# along with IcepapOCS. If not, see <http://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------

from PyQt4.QtGui import QMainWindow
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QBoxLayout
from PyQt4.QtGui import QColor
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QTimer
from ui.ui_window_main import Ui_WindowMain
from collector import Collector
from dialog_settings import DialogSettings
from settings import Settings
from axis_time import AxisTime
from curve_item import CurveItem
import pyqtgraph as pg
import numpy as np
import collections
import time


class WindowMain(QMainWindow):
    """A dialog for plotting IcePAP signals."""

    def __init__(self, host, port, timeout, siglist, selected_driver=None):
        """
        Initializes an instance of class WindowMain.

        host            - IcePAP system address.
        port            - IcePAP system port number.
        timeout         - Socket timeout.
        siglist         - List of predefined signals.
                            Element Syntax: <driver>:<signal name>:<Y-axis>
                            Example: ["1:PosAxis:1", "1:MeasI:2", "1:MeasVm:3"]
        selected_driver - The driver to display in combobox at startup.
        """
        QMainWindow.__init__(self, None)
        self.ui = Ui_WindowMain()
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.ui.setupUi(self)
        self.setWindowTitle('Oscilloscope  |  ' + host)

        try:
            self.collector = Collector(host,
                                       port,
                                       timeout,
                                       self.callback_collect)
        except Exception as e:
            msg = 'Failed to create main window.\n{}'.format(e)
            print(msg)
            QMessageBox.critical(None, 'Create Main Window', msg)
            return

        self.subscriptions = {}
        self.curve_items = []
        self._paused = False
        self.settings = Settings(self, self.collector)

        # Set up the plot area.
        self.plot_widget = pg.PlotWidget()
        self._plot_item = self.plot_widget.getPlotItem()
        self.view_boxes = [self.plot_widget.getViewBox(),
                           pg.ViewBox(),
                           pg.ViewBox()]
        self.ui.vloCurves.setDirection(QBoxLayout.BottomToTop)
        self.ui.vloCurves.addWidget(self.plot_widget)

        # Set up the X-axis.
        self._plot_item.getAxis('bottom').hide()  # Hide the original X-axis.
        self._axisTime = AxisTime(orientation='bottom')  # Create new X-axis.
        self._axisTime.linkToView(self.view_boxes[0])
        self._plot_item.layout.removeItem(self._plot_item.getAxis('bottom'))
        self._plot_item.layout.addItem(self._axisTime, 3, 1)
        self.now = self.collector.get_current_time()
        self.view_boxes[0].disableAutoRange(axis=self.view_boxes[0].XAxis)
        self.view_boxes[1].disableAutoRange(axis=self.view_boxes[1].XAxis)
        self.view_boxes[2].disableAutoRange(axis=self.view_boxes[2].XAxis)
        self._reset_x()

        # Set up the three Y-axes.
        self._plot_item.showAxis('right')
        self._plot_item.scene().addItem(self.view_boxes[1])
        self._plot_item.scene().addItem(self.view_boxes[2])
        ax3 = pg.AxisItem(orientation='right', linkView=self.view_boxes[2])
        self.axes = [self._plot_item.getAxis('left'),
                     self._plot_item.getAxis('right'), ax3]
        self.axes[1].linkToView(self.view_boxes[1])
        self.view_boxes[1].setXLink(self.view_boxes[0])
        self.view_boxes[2].setXLink(self.view_boxes[0])
        self._plot_item.layout.addItem(self.axes[2], 2, 3)
        self._plot_item.hideButtons()
        self._enable_auto_range_y()

        # Set up the crosshair vertical line.
        self.vertical_line = pg.InfiniteLine(angle=90, movable=False)
        self.view_boxes[0].addItem(self.vertical_line, ignoreBounds=True)

        # Initialize comboboxes and buttons.
        self._fill_combo_box_driver_ids(selected_driver)
        self._fill_combo_box_signals()
        self._select_axis_1()
        self._update_button_status()

        # Set up signalling connections.
        self._connect_signals()
        self.proxy = pg.SignalProxy(self.plot_widget.scene().sigMouseMoved,
                                    rateLimit=60,
                                    slot=self._mouse_moved)

        # Add any predefined signals.
        for sig in siglist:
            lst = sig.split(':')
            if len(lst) != 3:
                msg = 'Bad format of predefined signal "{}".\n' \
                      'It should be: ' \
                      '<driver>:<signal name>:<Y-axis>'.format(sig)
                print(msg)
                QMessageBox.critical(None, 'Bad Signal Syntax', msg)
                return
            self._add_signal(int(lst[0]), lst[1], int(lst[2]))

        # Set up continuous saving of collected signal data.
        self.cont_file_path = self._get_cont_file_path()
        self.cont_save_ticker = QTimer()
        self.cont_save_ticker.timeout.connect(self._continuous_save)
        self.cont_save_interval = 5 * 60 * 1000  # Fixed 5 minutes.
        self.cont_save_time = time.time()
        self.cont_save_ticker.start(self.cont_save_interval)

    def _fill_combo_box_driver_ids(self, selected_driver):
        driver_ids = self.collector.get_available_drivers()
        for driver_id in driver_ids:
            self.ui.cbDrivers.addItem(str(driver_id))
        start_index = 0
        if selected_driver is not None:
            start_index = self.ui.cbDrivers.findText(str(selected_driver))
        self.ui.cbDrivers.setCurrentIndex(start_index)

    def _fill_combo_box_signals(self):
        signals = self.collector.get_available_signals()
        num_colors = len(CurveItem.colors)
        if num_colors < len(signals):
            msg = 'Internal error!\nNew signals added.\nAdd ' \
                  'more colors and pens.'
            print(msg)
            QMessageBox.warning(None, 'Available Signals', msg)
            for i in range(num_colors):
                self.ui.cbSignals.addItem(signals[i])
        else:
            for sig in signals:
                self.ui.cbSignals.addItem(sig)
        self.ui.cbSignals.setCurrentIndex(0)

    def _connect_signals(self):
        self.ui.rbAxis1.clicked.connect(self._select_axis_1)
        self.ui.rbAxis2.clicked.connect(self._select_axis_2)
        self.ui.rbAxis3.clicked.connect(self._select_axis_3)
        self.ui.btnAdd.clicked.connect(self._add_button_clicked)
        self.ui.btnShift.clicked.connect(self._shift_button_clicked)
        self.ui.btnRemoveSel.clicked.connect(self._remove_selected_signal)
        self.ui.btnRemoveAll.clicked.connect(self._remove_all_signals)
        self.ui.btnCLoop.clicked.connect(self._signals_closed_loop)
        self.ui.btnCurrents.clicked.connect(self._signals_currents)
        self.ui.btnTarget.clicked.connect(self._signals_target)
        self.ui.btnClear.clicked.connect(self._clear_all)
        self.ui.btnSeeAll.clicked.connect(self._view_all_data)
        self.ui.btnResetX.clicked.connect(self._reset_x)
        self.ui.btnResetY.clicked.connect(self._enable_auto_range_y)
        self.ui.btnPause.clicked.connect(self._pause_x_axis)
        self.ui.btnNow.clicked.connect(self._goto_now)
        self.ui.btnSave.clicked.connect(self._save_to_file)
        self.ui.actionSave_to_File.triggered.connect(self._save_to_file)
        self.ui.actionSettings.triggered.connect(self._display_settings_dlg)
        self.ui.actionExit.triggered.connect(self.close)
        self.ui.actionClosed_Loop.triggered.connect(self._signals_closed_loop)
        self.ui.actionCurrents.triggered.connect(self._signals_currents)
        self.ui.actionTarget.triggered.connect(self._signals_target)
        self.view_boxes[0].sigResized.connect(self._update_views)

    def closeEvent(self, event):
        """Overloads (QMainWindow) QWidget.closeEvent()."""
        self._remove_all_signals()
        event.accept()

    def _update_views(self):
        """Updates the geometry of the view boxes."""
        self.view_boxes[1].setGeometry(self.view_boxes[0].sceneBoundingRect())
        self.view_boxes[2].setGeometry(self.view_boxes[0].sceneBoundingRect())
        self.view_boxes[1].linkedViewChanged(self.view_boxes[0],
                                             self.view_boxes[1].XAxis)
        self.view_boxes[2].linkedViewChanged(self.view_boxes[0],
                                             self.view_boxes[2].XAxis)

    def _update_button_status(self):
        val = self.ui.lvActiveSig.count() == 0
        self.ui.btnShift.setDisabled(val)
        self.ui.btnRemoveSel.setDisabled(val)
        self.ui.btnRemoveAll.setDisabled(val)

    def _update_plot_axes_labels(self):
        txt = ['', '', '']
        for ci in self.curve_items:
            t = "<span style='font-size: 8pt; " \
                "color: {};'>{}</span>".format(ci.color.name(), ci.signature)
            txt[ci.y_axis - 1] += t
        for i in range(0, len(self.axes)):
            self.axes[i].setLabel(txt[i])

    def _select_axis_1(self):
        self.ui.rbAxis1.setChecked(True)
        self.ui.rbAxis2.setChecked(False)
        self.ui.rbAxis3.setChecked(False)

    def _select_axis_2(self):
        self.ui.rbAxis1.setChecked(False)
        self.ui.rbAxis2.setChecked(True)
        self.ui.rbAxis3.setChecked(False)

    def _select_axis_3(self):
        self.ui.rbAxis1.setChecked(False)
        self.ui.rbAxis2.setChecked(False)
        self.ui.rbAxis3.setChecked(True)

    def _add_button_clicked(self):
        addr = int(self.ui.cbDrivers.currentText())
        my_signal_name = str(self.ui.cbSignals.currentText())
        my_axis = 1
        if self.ui.rbAxis2.isChecked():
            my_axis = 2
        elif self.ui.rbAxis3.isChecked():
            my_axis = 3
        self._add_signal(addr, my_signal_name, my_axis)

    def _add_signal(self, driver_addr, signal_name, y_axis):
        """
        Adds a new curve to the plot area.

        driver_addr - IcePAP driver address.
        signal_name - Signal name.
        y_axis      - Y axis to plot against.
        """
        try:
            subscription_id = self.collector.subscribe(driver_addr,
                                                       signal_name)
        except Exception as e:
            msg = 'Failed to subscribe to signal {} ' \
                  'from driver {}.\n{}'.format(signal_name, driver_addr, e)
            print(msg)
            QMessageBox.critical(None, 'Add Curve', msg)
            return
        try:
            color_idx = self.collector.get_signal_index(signal_name)
        except ValueError as e:
            msg = 'Internal error. Failed to retrieve index ' \
                  'for signal {}.\n{}'.format(signal_name, e)
            print(msg)
            QMessageBox.critical(None, 'Add Curve', msg)
            return
        ci = CurveItem(subscription_id, driver_addr, signal_name,
                       y_axis, color_idx)
        self._add_curve(ci)
        self.curve_items.append(ci)
        self.collector.start(subscription_id)
        self.ui.lvActiveSig.addItem(ci.signature)
        index = len(self.curve_items) - 1
        self.ui.lvActiveSig.setCurrentRow(index)
        self.ui.lvActiveSig.item(index).setForeground(ci.color)
        self.ui.lvActiveSig.item(index).setBackground(QColor(0, 0, 0))
        self._update_plot_axes_labels()
        self._update_button_status()

    def _remove_selected_signal(self):
        self._continuous_save()
        index = self.ui.lvActiveSig.currentRow()
        ci = self.curve_items[index]
        self.collector.unsubscribe(ci.subscription_id)
        self._remove_curve_plot(ci)
        self.ui.lvActiveSig.takeItem(index)
        self.curve_items.remove(ci)
        self._update_plot_axes_labels()
        self._update_button_status()

    def _remove_all_signals(self):
        """Removes all signals."""
        self._continuous_save()
        for ci in self.curve_items:
            self.collector.unsubscribe(ci.subscription_id)
            self._remove_curve_plot(ci)
        self.ui.lvActiveSig.clear()
        self.curve_items = []
        self._update_plot_axes_labels()
        self._update_button_status()

    def _shift_button_clicked(self):
        """Assign a curve to a different y axis."""
        index = self.ui.lvActiveSig.currentRow()
        ci = self.curve_items[index]
        self._remove_curve_plot(ci)
        ci.y_axis = (ci.y_axis % 3) + 1
        ci.update_signature()
        self._add_curve(ci)
        self.ui.lvActiveSig.takeItem(index)
        self.ui.lvActiveSig.insertItem(index, ci.signature)
        self.ui.lvActiveSig.item(index).setForeground(ci.color)
        self.ui.lvActiveSig.item(index).setBackground(QColor(0, 0, 0))
        self.ui.lvActiveSig.setCurrentRow(index)
        self._update_plot_axes_labels()

    def _add_curve(self, ci):
        """
        Create a new curve and add it to a viewbox.

        ci - Curve item that will be the owner.
        """
        my_curve = ci.create_curve()
        self.view_boxes[ci.y_axis - 1].addItem(my_curve)

    def _mouse_moved(self, evt):
        """
        Acts om mouse move.

        evt - Event containing the position of the mouse pointer.
        """
        pos = evt[0]  # The signal proxy turns original arguments into a tuple.
        if self.plot_widget.sceneBoundingRect().contains(pos):
            mouse_point = self.view_boxes[0].mapSceneToView(pos)
            time_value = mouse_point.x()
            try:
                pretty_time = time.strftime("%H:%M:%S",
                                            time.gmtime(time_value))
            except ValueError:  # Time out of range.
                return
            txtmax = ''
            txtnow = ''
            txtmin = ''
            text_size = 10
            for ci in self.curve_items:
                tmp = "<span style='font-size: {}pt; color: {};'>|"
                tmp = tmp.format(text_size, ci.color.name())
                if ci.in_range(time_value):
                    txtmax += "{}{}</span>".format(tmp, ci.val_max)
                    txtnow += "{}{}</span>".format(tmp, ci.get_y(time_value))
                    txtmin += "{}{}</span>".format(tmp, ci.val_min)
            tmp = "|<span style='font-size: {}pt; color: white;'>{}</span>"
            txtnow += tmp.format(text_size, pretty_time)
            title = "<br>{}<br>{}<br>{}".format(txtmax, txtnow, txtmin)
            self.plot_widget.setTitle(title)
            self.vertical_line.setPos(mouse_point.x())

    def _remove_curve_plot(self, ci):
        """
        Remove a curve from the plot area.

        ci - Curve item to remove.
        """
        self.view_boxes[ci.y_axis - 1].removeItem(ci.curve)

    def _signals_closed_loop(self):
        """Display a specific set of curves."""
        self._remove_all_signals()
        drv_addr = int(self.ui.cbDrivers.currentText())
        self._add_signal(drv_addr, 'PosAxis', 1)
        self._add_signal(drv_addr, 'DifAxTgtenc', 2)
        self._add_signal(drv_addr, 'DifAxMotor', 2)
        self._add_signal(drv_addr, 'StatReady', 3)
        self._add_signal(drv_addr, 'StatMoving', 3)
        self._add_signal(drv_addr, 'StatSettling', 3)
        self._add_signal(drv_addr, 'StatOutofwin', 3)

    def _signals_currents(self):
        """Display a specific set of curves."""
        self._remove_all_signals()
        drv_addr = int(self.ui.cbDrivers.currentText())
        self._add_signal(drv_addr, 'PosAxis', 1)
        self._add_signal(drv_addr, 'MeasI', 2)
        self._add_signal(drv_addr, 'MeasVm', 3)

    def _signals_target(self):
        """Display a specific set of curves."""
        self._remove_all_signals()
        drv_addr = int(self.ui.cbDrivers.currentText())
        self._add_signal(drv_addr, 'PosAxis', 1)
        self._add_signal(drv_addr, 'EncTgtenc', 2)

    def _clear_all(self):
        """Clear all the displayed curves."""
        self._continuous_save()
        for ci in self.curve_items:
            ci.clear()

    def _view_all_data(self):
        """Adjust X axis to view all collected data."""
        time_start = self.collector.get_current_time()
        for ci in self.curve_items:
            t = ci.start_time()
            if 0 < t < time_start:
                time_start = t
        self.view_boxes[0].setXRange(time_start,
                                     self.collector.get_current_time(),
                                     padding=0)

    def _reset_x(self):
        """
        Reset the length of the X axis to
        the initial number of seconds (setting).
        """
        now = self.collector.get_current_time()
        start = now - self.settings.default_x_axis_len
        self.view_boxes[0].setXRange(start, now, padding=0)

    def _enable_auto_range_y(self):
        self.view_boxes[0].enableAutoRange(axis=self.view_boxes[0].YAxis)
        self.view_boxes[1].enableAutoRange(axis=self.view_boxes[1].YAxis)
        self.view_boxes[2].enableAutoRange(axis=self.view_boxes[2].YAxis)

    def _pause_x_axis(self):
        """Freeze the X axis."""
        if self._paused:
            self._paused = False
            self.ui.btnPause.setText('Pause')
        else:
            self._paused = True
            self.ui.btnPause.setText('Run')
        self.ui.btnClear.setDisabled(self._paused)

    def _goto_now(self):
        """Pan X axis to display newest values."""
        now = self.collector.get_current_time()
        x_min = self.view_boxes[0].viewRange()[0][0]
        x_max = self.view_boxes[0].viewRange()[0][1]
        self.view_boxes[0].setXRange(now - (x_max - x_min), now, padding=0)

    def enable_action(self, enable=True):
        """Enables or disables menu item File|Settings."""
        self.ui.actionSettings.setEnabled(enable)

    def _save_to_file(self):
        if not self.curve_items:
            return
        capt = "Save to csv file"
        fn = QFileDialog.getSaveFileName(caption=capt, filter="*.csv")
        if not fn:
            return
        if fn[-4:] != ".csv":
            fn = fn + ".csv"
        try:
            f = open(fn, "w+")
        except Exception as e:
            msg = 'Failed to open/create file: {}\n{}'.format(fn, e)
            print(msg)
            QMessageBox.critical(None, 'File Open Failed', msg)
            return
        self._create_csv_file(f)
        f.close()

    def _create_csv_file(self, csv_file):
        my_dict = collections.OrderedDict()
        for ci in self.curve_items:
            header = "time-{}-{}".format(ci.driver_addr, ci.signal_name)
            my_dict[header] = ci.array_time
            header = "val-{}-{}".format(ci.driver_addr, ci.signal_name)
            my_dict[header] = ci.array_val
        key_longest = my_dict.keys()[0]
        for key in my_dict:
            if my_dict[key][0] < my_dict[key_longest][0]:
                key_longest = key
        for key in my_dict:
            delta = len(my_dict[key_longest]) - len(my_dict[key])
            my_dict[key] = delta * [np.nan] + my_dict[key]
        for key in my_dict:
            csv_file.write(",{}".format(key))
        csv_file.write("\n")
        for idx in range(0, len(my_dict[key_longest])):
            line = str(idx)
            for key in my_dict:
                line += ",{}".format(my_dict[key][idx])
            csv_file.write(line + '\n')

    def _get_cont_file_path(self):
        time_str = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        file_name = "IcepapOSC_{}.csv".format(time_str)
        return self.settings.data_folder + '/' + file_name

    def _continuous_save(self):
        if not self.curve_items:
            return
        self.cont_save_ticker.stop()
        new_save_time = time.time()
        fn = self.cont_file_path
        try:
            f = open(fn, "w+")
        except Exception as e:
            msg = 'Failed to create file: {}\n{}'.format(fn, e)
            print(msg)
            QMessageBox.critical(None, 'File Create Failed', msg)
            return
        my_dict = collections.OrderedDict()
        for ci in self.curve_items:
            start_idx = ci.get_time_index(self.cont_save_time)
            header = "time-{}-{}".format(ci.driver_addr, ci.signal_name)
            my_dict[header] = ci.array_time[start_idx:]
            header = "val-{}-{}".format(ci.driver_addr, ci.signal_name)
            my_dict[header] = ci.array_val[start_idx:]
        key_longest = my_dict.keys()[0]
        for key in my_dict:
            if my_dict[key][0] < my_dict[key_longest][0]:
                key_longest = key
        for key in my_dict:
            delta = len(my_dict[key_longest]) - len(my_dict[key])
            my_dict[key] = delta * [np.nan] + my_dict[key]
        for key in my_dict:
            f.write(",{}".format(key))
        f.write("\n")
        for idx in range(0, len(my_dict[key_longest])):
            line = str(idx)
            for key in my_dict:
                line += ",{}".format(my_dict[key][idx])
            f.write(line + '\n')
        f.close()
        self.cont_file_path = self._get_cont_file_path()
        self.cont_save_time = new_save_time
        self.cont_save_ticker.start(self.cont_save_interval)

    def _display_settings_dlg(self):
        self.enable_action(False)
        dlg = DialogSettings(self, self.settings)
        dlg.show()

    def settings_updated(self):
        """Settings have been changed."""
        self._reset_x()

    def callback_collect(self, subscription_id, value_list):
        """
        Callback function that stores the data collected from IcePAP.

        subscription_id - Subscription id.
        value_list - List of tuples (time, value).
        """
        for ci in self.curve_items:
            if ci.subscription_id == subscription_id:
                ci.collect(value_list)
        if not self._paused:
            self._update_view()

    def _update_view(self):
        x_min = self.view_boxes[0].viewRange()[0][0]
        x_max = self.view_boxes[0].viewRange()[0][1]

        # Update the X-axis.
        now_in_range = self.now <= x_max
        self.now = self.collector.get_current_time()
        if now_in_range:
            self.view_boxes[0].setXRange(self.now - (x_max - x_min),
                                         self.now,
                                         padding=0)
        self.ui.btnNow.setDisabled(now_in_range)

        # Update the curves.
        for ci in self.curve_items:
            ci.update_curve(x_min, x_max)
