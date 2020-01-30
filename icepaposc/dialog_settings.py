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

from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDialogButtonBox
from ui.ui_dialog_settings import Ui_DialogSettings


class DialogSettings(QDialog):

    def __init__(self, parent, settings):
        QDialog.__init__(self, parent)
        self.parent = parent
        self.ui = Ui_DialogSettings()
        self.ui.setupUi(self)
        self.settings = settings
        self.apply_button = self.ui.bbApplyClose.button(QDialogButtonBox.Apply)
        self.close_button = self.ui.bbApplyClose.button(QDialogButtonBox.Close)
        self._connect_signals()
        self._update_gui_rate()
        self.ui.sbSampleRate.setMinimum(self.settings.sample_rate_min)
        self.ui.sbSampleRate.setMaximum(self.settings.sample_rate_max)
        self.ui.sbSampleRate.setValue(self.settings.sample_rate)
        self.ui.sbDumpRate.setMinimum(self.settings.dump_rate_min)
        self.ui.sbDumpRate.setMaximum(self.settings.dump_rate_max)
        self.ui.sbDumpRate.setValue(self.settings.dump_rate)
        self.ui.sbLenAxisX.setMinimum(self.settings.default_x_axis_length_min)
        self.ui.sbLenAxisX.setMaximum(self.settings.default_x_axis_length_max)
        self.ui.sbLenAxisX.setValue(self.settings.default_x_axis_length)
        self.apply_button.setDisabled(True)

    def _connect_signals(self):
        self.ui.sbSampleRate.valueChanged.connect(self._sample_rate_changed)
        self.ui.sbDumpRate.valueChanged.connect(self._dump_rate_changed)
        self.ui.sbLenAxisX.valueChanged.connect(self._x_axis_length_changed)
        self.apply_button.clicked.connect(self._apply)
        self.close_button.clicked.connect(self.close)

    def _sample_rate_changed(self):
        self._update_gui_rate()
        self._check_button_state()

    def _dump_rate_changed(self):
        self._update_gui_rate()
        self._check_button_state()

    def _x_axis_length_changed(self):
        self._check_button_state()

    def _check_button_state(self):
        eq = self.ui.sbSampleRate.value() == self.settings.sample_rate and \
           self.ui.sbDumpRate.value() == self.settings.dump_rate and \
           self.ui.sbLenAxisX.value() == self.settings.default_x_axis_length
        self.apply_button.setDisabled(eq)

    def _update_gui_rate(self):
        update_rate = self.ui.sbSampleRate.value() * self.ui.sbDumpRate.value()
        self.ui.leGuiUpdateRate.setText(str(update_rate))

    def _apply(self):
        self.settings.sample_rate = self.ui.sbSampleRate.value()
        self.settings.dump_rate = self.ui.sbDumpRate.value()
        self.settings.default_x_axis_length = self.ui.sbLenAxisX.value()
        self.settings.announce_update()
        self.apply_button.setDisabled(True)

    def done(self, r):
        """Overload of QDialog.done()."""
        self.parent.enable_action()
        QDialog.done(self, r)
