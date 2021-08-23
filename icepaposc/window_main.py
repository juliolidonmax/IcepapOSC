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
import os.path

import pyqtgraph as pg
import numpy as np
import collections
import time
import datetime
from PyQt5 import QtWidgets, Qt, QtCore, uic, QtGui
from PyQt5.QtWidgets import QFileDialog
from pkg_resources import resource_filename
from .collector import Collector
from .dialog_settings import DialogSettings
from .settings import Settings
from .axis_time import AxisTime
from .curve_item import CurveItem


class WindowMain(QtWidgets.QMainWindow):
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
        QtWidgets.QMainWindow.__init__(self, None)

        ui_filename = resource_filename('icepaposc.ui', 'window_main.ui')
        self.ui = self
        uic.loadUi(ui_filename, baseinstance=self.ui,
                   package="icepaposc.custom_widgets")

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.setWindowTitle('Oscilloscope | {}'.format(host))
        self.settings = Settings()

        try:
            self.collector = Collector(host,
                                       port,
                                       timeout,
                                       self.settings,
                                       self.callback_collect)
        except Exception as e:
            msg = 'Failed to create main window.\n{}'.format(e)
            print(msg)
            QtWidgets.QMessageBox.critical(self, 'Create Main Window', msg)
            return

        self.subscriptions = {}
        self.curve_items = []
        self._paused = False

        # Switch to using white background and black foreground
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        self.fgcolor = QtGui.QColor(0, 0, 0)

        # Set up the plot area.
        self.plot_widget = pg.PlotWidget()
        self._plot_item = self.plot_widget.getPlotItem()
        self.view_boxes = [self.plot_widget.getViewBox(),
                           pg.ViewBox(),
                           pg.ViewBox()]
        self.ui.vloCurves.setDirection(QtWidgets.QBoxLayout.BottomToTop)
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
        self._update_button_status()
        self.ui.red_radio.setChecked(True)
        self.ui.solidline_radio.setChecked(True)
        self.ui.nomarker_radio.setChecked(True)

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
                QtWidgets.QMessageBox.critical(self, 'Bad Signal Syntax', msg)
                return

        # encoder count to motor step conversion factor measurement
        self.ecpmt_just_enabled = False
        self.step_ini = 0
        self.enc_ini = 0

        # Set up auto save of collected signal data.
        self._save_ticker = QtCore.QTimer()
        self._save_ticker.timeout.connect(self._auto_save)
        self._save_time = None
        self._idx = 0
        self._settings_updated = False
        self._file_path = None
        self._old_use_append = self.settings.use_append
        self._prepare_next_auto_save()

    def _fill_combo_box_driver_ids(self, selected_driver):
        driver_ids = self.collector.get_available_drivers()
        for driver_id in driver_ids:
            self.ui.cbDrivers.addItem(str(driver_id))
        if selected_driver is not None:
            start_index = self.ui.cbDrivers.findText(str(selected_driver))
        # maybe the selected_driver is not available;
        # then just take the first one
        if start_index == -1:
            start_index = 0
        self.ui.cbDrivers.setCurrentIndex(start_index)

    def _fill_combo_box_signals(self):
        signals = self.collector.get_available_signals()
        for sig in signals:
            self.ui.cbSignals.addItem(sig)

        self.ui.cbSignals.setCurrentIndex(0)

    def _connect_signals(self):
        self.ui.sbAxis.valueChanged.connect(self._select_axis)
        self.ui.btnAdd.clicked.connect(self._add_button_clicked)
        self.ui.btnShift.clicked.connect(self._shift_button_clicked)
        self.ui.btnRemoveSel.clicked.connect(self._remove_selected_signal)
        self.ui.btnRemoveAll.clicked.connect(self._remove_all_signals)
        self.ui.btnCLoop.setDefaultAction(self.ui.actionClosed_Loop)
        self.ui.btnVelocities.setDefaultAction(self.ui.actionVelocities)
        self.ui.btnCurrents.setDefaultAction(self.ui.actionCurrents)
        self.ui.btnTarget.setDefaultAction(self.ui.actionTarget)
        self.ui.btnClear.clicked.connect(self._clear_all)
        self.ui.btnSeeAll.clicked.connect(self._view_all_data)
        self.ui.btnResetX.clicked.connect(self._reset_x)
        self.ui.btnResetY.clicked.connect(self._enable_auto_range_y)
        self.ui.btnPause.clicked.connect(self._pause_x_axis)
        self.ui.btnNow.clicked.connect(self._goto_now)
        self.ui.actionSave_to_File.triggered.connect(self._save_to_file)
        self.ui.actionSettings.triggered.connect(self._display_settings_dlg)
        self.ui.actionExit.triggered.connect(self.close)
        self.ui.actionClosed_Loop.triggered.connect(self._signals_closed_loop)
        self.ui.actionExport_Set.triggered.connect(self._export_signal_set)
        self.ui.actionImport_Set.triggered.connect(self._import_signal_set)
        self.ui.actionVelocities.triggered.connect(self._signals_velocities)
        self.ui.actionCurrents.triggered.connect(self._signals_currents)
        self.ui.actionTarget.triggered.connect(self._signals_target)
        self.view_boxes[0].sigResized.connect(self._update_views)
        self.ui.chkEctsTurn.stateChanged.connect(
            self.enable_ects_per_turn_calculation)
        self.ui.btnAxisScaleAuto.clicked.connect(self._set_axis_autoscale)
        self.ui.btnAxisOffsIncrease.clicked.connect(self._axis_offs_pp)
        self.ui.btnAxisOffsDecrease.clicked.connect(self._axis_offs_mm)
        self.ui.btnAxisScaleIncrease.clicked.connect(self._axis_scale_pp)
        self.ui.btnAxisScaleDecrease.clicked.connect(self._axis_scale_mm)
        self.ui.btnWhitebg.clicked.connect(self._do_white_background)
        self.ui.btnGreybg.clicked.connect(self._do_grey_background)
        self.ui.btnBlackbg.clicked.connect(self._do_black_background)

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

    def _select_axis(self):
        pass

    def _add_button_clicked(self):
        addr = int(self.ui.cbDrivers.currentText())
        my_signal_name = str(self.ui.cbSignals.currentText())
        my_axis = self.ui.sbAxis.value()
        my_linecolor = self._get_line_color()
        my_linestyle = self._get_line_style()
        my_linemarker = self._get_line_marker()
        self._add_signal(addr, my_signal_name, my_axis,
                         my_linecolor, my_linestyle, my_linemarker)

    def _get_line_color(self):
        the_btn = self.ui.color_radio_group.checkedButton()
        if the_btn:
            return the_btn.palette().color(QtGui.QPalette.WindowText)
        else:
            return QtGui.QColor(0, 0, 0)

    def _get_line_marker(self):
        the_btn = self.ui.marker_radio_group.checkedButton()
        if the_btn:
            return str(the_btn.text())
        else:
            return ''

    def _get_line_style(self):
        if self.ui.solidline_radio.isChecked():
            return QtCore.Qt.SolidLine
        elif self.ui.dottedline_radio.isChecked():
            return QtCore.Qt.DotLine
        else:
            return QtCore.Qt.SolidLine

    def _add_signal(self, driver_addr, signal_name, y_axis, linecolor,
                    linestyle, linemarker, auto_save=False):
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
            QtWidgets.QMessageBox.critical(self, 'Add Curve', msg)
            return
        ci = CurveItem(subscription_id, driver_addr, signal_name,
                       y_axis, linecolor, linestyle, linemarker)
        self._add_curve(ci)
        self.curve_items.append(ci)
        self.collector.start(subscription_id)
        self.ui.lvActiveSig.addItem(ci.signature)
        index = len(self.curve_items) - 1
        self.ui.lvActiveSig.setCurrentRow(index)
        self.ui.lvActiveSig.item(index).setForeground(ci.color)
        self.ui.lvActiveSig.item(index).setBackground(Qt.QColor(0, 0, 0))
        self._update_plot_axes_labels()
        self._update_button_status()
        if auto_save:
            self._auto_save(True)

    def _remove_selected_signal(self):
        self._auto_save(True)
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
        self._auto_save(True)
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
        self.ui.lvActiveSig.item(index).setBackground(Qt.QColor(0, 0, 0))
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
                date = datetime.datetime.fromtimestamp(time_value)
                pretty_time = date.strftime("%H:%M:%S.%f")[:-3]
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
            tmp = "|<span style='font-size: {}pt; color: {};'>{}</span>"
            txtnow += tmp.format(text_size,
                                 str(self.fgcolor.name()), pretty_time)
            title = "<br>{}<br>{}<br>{}".format(txtmax, txtnow, txtmin)
            self.plot_widget.setTitle(title)
            self.vertical_line.setPos(mouse_point.x())

    def _remove_curve_plot(self, ci):
        """
        Remove a curve from the plot area.

        ci - Curve item to remove.
        """
        self.view_boxes[ci.y_axis - 1].removeItem(ci.curve)

    def _do_white_background(self):
        color_axes = QtGui.QColor(0, 0, 0)
        color_plot = QtGui.QColor(255, 255, 255)
        self._set_plot_colors(color_axes, color_plot)

    def _do_grey_background(self):
        color_axes = QtGui.QColor(0, 0, 0)
        color_plot = QtGui.QColor(230, 230, 230)
        self._set_plot_colors(color_axes, color_plot)

    def _do_black_background(self):
        color_axes = QtGui.QColor(255, 255, 255)
        color_plot = QtGui.QColor(0, 0, 0)
        self._set_plot_colors(color_axes, color_plot)

    def _set_plot_colors(self, color_axes, color_plot):
        self.plot_widget.setBackground(color_plot)
        for i in range(3):
            self.axes[i].setPen(color_axes)
            self.axes[i].setTextPen(color_axes)
        self._axisTime.setPen(color_axes)
        self._axisTime.setTextPen(color_axes)
        self.fgcolor = color_axes

    def _signals_closed_loop(self):
        """Display a specific set of curves."""
        self._remove_all_signals()
        drv_addr = int(self.ui.cbDrivers.currentText())
        self._add_signal(drv_addr, 'PosAxis', 1, QtGui.QColor(
            255, 0, 0), QtCore.Qt.SolidLine, '')
        self._add_signal(drv_addr, 'DifAxTgtenc', 2, QtGui.QColor(
            0, 255, 0), QtCore.Qt.SolidLine, '')
        self._add_signal(drv_addr, 'DifAxMotor', 2, QtGui.QColor(
            0, 127, 255), QtCore.Qt.SolidLine, '')
        self._add_signal(drv_addr, 'StatReady', 3, QtGui.QColor(
            0, 255, 255), QtCore.Qt.DotLine, '')
        self._add_signal(drv_addr, 'StatMoving', 3, QtGui.QColor(
            255, 192, 203), QtCore.Qt.DotLine, '')
        self._add_signal(drv_addr, 'StatSettling', 3, QtGui.QColor(
            255, 255, 0), QtCore.Qt.DotLine, '')
        self._add_signal(drv_addr, 'StatOutofwin', 3,
                         QtGui.QColor(128, 0, 0), QtCore.Qt.DotLine, '')
        self._add_signal(drv_addr, 'StatWarning', 3,
                         QtGui.QColor(0, 128, 0), QtCore.Qt.DotLine, '')
        self._add_signal(drv_addr, 'StatStopcode', 3,
                         QtGui.QColor(255, 0, 0), QtCore.Qt.DotLine, '')
        self.view_boxes[0].enableAutoRange(axis=self.view_boxes[0].YAxis)
        self.view_boxes[1].disableAutoRange(axis=self.view_boxes[1].YAxis)
        self.view_boxes[1].setYRange(-30, 70, padding=0)
        self.view_boxes[2].disableAutoRange(axis=self.view_boxes[2].YAxis)
        self.view_boxes[2].setYRange(-1, 20, padding=0)

    def _signals_currents(self):
        """Display a specific set of curves."""
        self._remove_all_signals()
        drv_addr = int(self.ui.cbDrivers.currentText())
        self._add_signal(drv_addr, 'PosAxis', 1, QtGui.QColor(
            255, 0, 0), QtCore.Qt.SolidLine, '')
        self._add_signal(drv_addr, 'MeasI', 2, QtGui.QColor(
            0, 255, 0), QtCore.Qt.SolidLine, '')
        self._add_signal(drv_addr, 'MeasVm', 3, QtGui.QColor(
            0, 127, 255), QtCore.Qt.SolidLine, '')
        # Ajust plot axis
        self.view_boxes[0].enableAutoRange(axis=self.view_boxes[0].YAxis)
        self.view_boxes[1].disableAutoRange(axis=self.view_boxes[1].YAxis)
        self.view_boxes[1].setYRange(-9, 10, padding=0)
        self.view_boxes[2].enableAutoRange(axis=self.view_boxes[2].YAxis)

    def _signals_velocities(self):
        """Display a specific set of curves."""
        self._remove_all_signals()
        drv_addr = int(self.ui.cbDrivers.currentText())
        self._add_signal(drv_addr, 'PosAxis', 1, QtGui.QColor(
            255, 0, 0), QtCore.Qt.SolidLine, '')
        self._add_signal(drv_addr, 'VelCurrent', 2, QtGui.QColor(
            0, 255, 0), QtCore.Qt.SolidLine, '')
        self._add_signal(drv_addr, 'VelMotor', 2, QtGui.QColor(
            0, 127, 255), QtCore.Qt.SolidLine, '')
        # Ajust plot axis
        self.view_boxes[0].enableAutoRange(axis=self.view_boxes[0].YAxis)
        self.view_boxes[1].enableAutoRange(axis=self.view_boxes[1].YAxis)
        #self.view_boxes[1].disableAutoRange(axis=self.view_boxes[1].YAxis)
        #self.view_boxes[1].setYRange(-9, 10, padding=0)
        self.view_boxes[2].enableAutoRange(axis=self.view_boxes[2].YAxis)

    def _signals_target(self):
        """Display a specific set of curves."""
        self._remove_all_signals()
        drv_addr = int(self.ui.cbDrivers.currentText())
        self._add_signal(drv_addr, 'PosAxis', 1, QtGui.QColor(
            255, 0, 0), QtCore.Qt.SolidLine, '')
        self._add_signal(drv_addr, 'EncTgtenc', 2, QtGui.QColor(
            0, 255, 0), QtCore.Qt.SolidLine, '')

    def _clear_all(self):
        """Clear all the displayed curves."""
        self._auto_save()
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

    def _import_signal_set(self):
        fname = QFileDialog.getOpenFileName(
            self, "Import Signal Set",
            filter="Signal Set Files Files (*.lst);;All Files (*)",
            directory=self.settings.signals_set_folder)
        if fname:
            self._remove_all_signals()
            drv_addr = int(self.ui.cbDrivers.currentText())
            with open(fname[0], 'r') as f:
                for ll in f:
                    tokens = ll.split()
                    if len(tokens) < 4:
                        continue
                    elif len(tokens) > 4:
                        line_marker = tokens[4]
                    else:
                        line_marker = ''
                    self._add_signal(drv_addr, tokens[0], int(tokens[1]),
                                     QtGui.QColor(tokens[2]),
                                     int(tokens[3]), line_marker)

    def _export_signal_set(self):
        file_name = os.path.join(self.settings.signals_set_folder,
                                 'SignalSet.lst')
        fname = QFileDialog.getSaveFileName(
            self, "Export Signal Set", file_name,
            filter="Signal Set Files Files (*.lst);;All Files (*)",
            )
        if fname:
            with open(fname[0], 'w') as f:
                for ci in self.curve_items:
                    line = '{} {} {} {} {}\n'.format(ci.signal_name,
                                                     ci.y_axis,
                                                     ci.color.name(),
                                                     ci.pen['style'],
                                                     ci.symbol)
                    f.write(line)

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
        fa = QtWidgets.QFileDialog.getSaveFileName(caption=capt,
                                                   filter="*.csv")
        fn = str(fa[0])
        if not fn:
            return
        if fn[-4:] != ".csv":
            fn = fn + ".csv"
        try:
            f = open(fn, "w+")
        except Exception as e:
            msg = 'Failed to open/create file: {}\n{}'.format(fn, e)
            print(msg)
            QtWidgets.QMessageBox.critical(self, 'File Open Failed', msg)
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
        key_longest = list(my_dict.keys())[0]
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

    def _auto_save(self, use_new_file=False):
        if not self.curve_items or not self._file_path:
            return
        if not self._settings_updated and not self.settings.use_auto_save:
            return
        self._save_ticker.stop()

        # Create matrix.
        my_dict = collections.OrderedDict()
        for ci in self.curve_items:
            start_idx = ci.get_time_index(self._save_time)
            header = "time-{}-{}".format(ci.driver_addr, ci.signal_name)
            my_dict[header] = ci.array_time[start_idx:]
            header = "val-{}-{}".format(ci.driver_addr, ci.signal_name)
            my_dict[header] = ci.array_val[start_idx:]
        key_longest = None
        for key in my_dict:  # Find a non empty list.
            if my_dict[key]:
                key_longest = key
                break
        if not key_longest:
            self._prepare_next_auto_save(True)
            return
        for key in my_dict:  # Find the longest list.
            if my_dict[key] and my_dict[key][0] < my_dict[key_longest][0]:
                key_longest = key
        for key in my_dict:  # Fill up the shorter lists with nan.
            delta = len(my_dict[key_longest]) - len(my_dict[key])
            my_dict[key] = delta * [np.nan] + my_dict[key]

        # Write matrix to file.
        try:
            f = open(self._file_path, self._get_write_mode())
        except Exception as e:
            msg = 'Failed to open file: {}\n{}'.format(self._file_path, e)
            print(msg)
            QtWidgets.QMessageBox.critical(self, 'File Open Failed', msg)
            return
        if self._idx == 0:
            for key in my_dict:
                f.write(",{}".format(key))
            f.write("\n")
        for i in range(0, len(my_dict[key_longest])):
            line = str(self._idx)
            self._idx += 1
            for key in my_dict:
                line += ",{}".format(my_dict[key][i])
            f.write(line + '\n')
        f.close()

        self._prepare_next_auto_save(use_new_file)

    def _prepare_next_auto_save(self, use_new_file=False):
        if self.settings.use_auto_save:
            if use_new_file or not self.settings.use_append or \
                    not self._file_path or self._settings_updated:
                self._set_new_file_path()
            self._save_time = time.time()
            self._save_ticker.start(60000 * self.settings.saving_interval)
        else:
            self._save_time = None
            self._file_path = None

    def _set_new_file_path(self):
        self._idx = 0
        time_str = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        file_name = "IcepapOSC_{}.csv".format(time_str)
        self._file_path = self.settings.saving_folder + '/' + file_name

    def _get_write_mode(self):
        do_append = self.settings.use_append
        if self._settings_updated:
            do_append = self._old_use_append
        return "a+" if do_append else "w+"

    def _display_settings_dlg(self):
        self.enable_action(False)
        dlg = DialogSettings(self, self.settings)
        dlg.show()

    def settings_updated(self):
        """Settings have been changed."""
        self._settings_updated = True
        if self._file_path:
            self._auto_save(True)
        else:
            self._prepare_next_auto_save()
        self._old_use_append = self.settings.use_append
        self._settings_updated = False
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

        try:
            # retrieve POS and ENC affine corrections
            self.collector.poscorr_a = float(self.ui.txt_poscorr_a.text())
            self.collector.poscorr_b = float(self.ui.txt_poscorr_b.text())
            self.collector.enccorr_a = float(self.ui.txt_enccorr_a.text())
            self.collector.enccorr_b = float(self.ui.txt_enccorr_b.text())
        except ValueError:
            pass

        # Update the curves.
        for ci in self.curve_items:
            ci.update_curve(x_min, x_max)

        # Update encoder count to motor step conversion factor measurement
        if self.ui.chkEctsTurn.isChecked():
            addr = self.collector.channels[
                self.collector.current_channel].icepap_address
            step_now = self.collector.icepap_system[addr].get_pos("AXIS")
            cfgANSTEP = int(
                self.collector.icepap_system[addr].get_cfg("ANSTEP")["ANSTEP"])
            cfgANTURN = int(
                self.collector.icepap_system[addr].get_cfg("ANTURN")["ANTURN"])
            enc_sel = str(self.ui.cb_enc_sel.currentText())
            try:
                enc_now = self.collector.icepap_system[addr].get_enc(enc_sel)
            except Exception as e:
                msg = 'Error querying encoder.\n{}'.format(e)
                print(msg)
                return
            if self.ecpmt_just_enabled:
                self.step_ini = step_now
                self.enc_ini = enc_now
                self.ecpmt_just_enabled = False
                print(self.step_ini, self.enc_ini)
            if (step_now - self.step_ini) != 0:
                enc_cts_per_motor_turn = \
                    (enc_now - self.enc_ini) * 1.0 * cfgANSTEP \
                    / ((step_now - self.step_ini) * cfgANTURN)
            else:
                enc_cts_per_motor_turn = 0
            self.ui.txtEctsTurn.setText(str(enc_cts_per_motor_turn))

    def enable_ects_per_turn_calculation(self):
        if self.ui.chkEctsTurn.isChecked():
            self.ecpmt_just_enabled = True

    def _set_axis_autoscale(self):
        axis = self.ui.cbAxisCtrlSelect.currentIndex()
        if axis < 3:
            # Yn axis
            self.view_boxes[axis].enableAutoRange(
                axis=self.view_boxes[axis].YAxis)
        else:
            # X axis
            self._reset_x()

    def _axis_offs_pp(self):
        self._chg_axis_offs(+0.1)

    def _axis_offs_mm(self):
        self._chg_axis_offs(-0.1)

    def _axis_scale_pp(self):
        self._chg_axis_scale(1 / 1.25)

    def _axis_scale_mm(self):
        self._chg_axis_scale(1.25)

    def _chg_axis_offs(self, offsfact):
        axis, amin, amax = self._get_axis_range()
        c = (amin+amax)/2
        d = (amax-amin)/2
        c += d*2*offsfact
        if axis < 3:
            # Yn axis
            self.view_boxes[axis].setYRange(c-d, c+d, padding=0)
        else:
            # X axis
            self.view_boxes[0].setXRange(c-d, c+d, padding=0)

    def _chg_axis_scale(self, scalefact):
        axis, amin, amax = self._get_axis_range()
        c = (amin+amax)/2
        d = (amax-amin)/2*scalefact
        if axis < 3:
            # Yn axis
            self.view_boxes[axis].setYRange(c-d, c+d, padding=0)
        else:
            # X axis
            self.view_boxes[0].setXRange(c-d, c+d, padding=0)

    def _get_axis_range(self):
        axis = self.ui.cbAxisCtrlSelect.currentIndex()
        if axis < 3:
            # Yn axis
            [amin, amax] = self.view_boxes[axis].viewRange()[1]
        else:
            # X axis
            [amin, amax] = self.view_boxes[0].viewRange()[0]
        return axis, amin, amax