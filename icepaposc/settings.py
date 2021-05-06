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

import os
from configparser import ConfigParser


class Settings:
    """Application settings."""

    # Settings for collector
    SAMPLE_RATE_MIN = 10  # [milliseconds]
    SAMPLE_RATE_MAX = 1000  # [milliseconds]
    DUMP_RATE_MIN = 1
    DUMP_RATE_MAX = 100

    # Settings for GUI
    X_AXIS_LEN_MIN = 5  # [Seconds]
    X_AXIS_LEN_MAX = 3600  # [Seconds]

    # Settings for auto save.
    SAVING_INTERVAL_MIN = 1  # [Minutes]
    SAVING_INTERVAL_MAX = 24 * 60  # [Minutes]

    def __init__(self):
        """Initializes an instance of class Settings."""

        user_path = os.path.expanduser("~")

        # Check folders
        base_folder = os.path.join(user_path, '.icepaposc')
        if not os.path.exists(base_folder):
            os.mkdir(base_folder)
        self.signals_set_folder = os.path.join(base_folder, 'signalset')
        if not os.path.exists(self.signals_set_folder):
            os.mkdir(self.signals_set_folder)

        # First configuration
        self.sample_rate = 50   # [milliseconds]
        self.dump_rate = 2  # [Seconds]
        self.default_x_axis_len = 30
        self.use_auto_save = False
        self.use_append = False
        self.saving_interval = 5  # [Minutes]
        self.saving_folder = user_path

        self.conf_file = os.path.join(base_folder, "settings.ini")
        self._read_file()

    def _read_file(self):
        conf = ConfigParser()
        conf.read(self.conf_file)

        self.sample_rate = conf.getint('collector', 'tick_interval',
                                       fallback=self.sample_rate)
        self.dump_rate = conf.getint('collector', 'sample_buf_len',
                                     fallback=self.dump_rate)
        self.default_x_axis_len = conf.getint('gui', 'default_x_axis_len',
                                              fallback=self.default_x_axis_len)
        self.use_auto_save = conf.getboolean('auto_save', 'use',
                                             fallback=self.use_auto_save)
        self.use_append = conf.getboolean('auto_save', 'append',
                                          fallback=self.use_append)
        self.saving_interval = conf.getint('auto_save', 'interval',
                                           fallback=self.saving_interval)
        self.saving_folder = conf.get('auto_save', 'folder',
                                      fallback=self.saving_folder)
        self.signals_set_folder = conf.get('signals_set', 'folder',
                                           fallback=self.signals_set_folder)

    def update(self):
        """Called when a setting has been changed."""
        conf = ConfigParser()
        conf.read(self.conf_file)

        if 'collector' not in conf:
            conf.add_section('collector')
        conf.set('collector', 'tick_interval', str(self.sample_rate))
        conf.set('collector', 'sample_buf_len', str(self.dump_rate))

        if 'gui' not in conf:
            conf.add_section('gui')
        conf.set('gui', 'default_x_axis_len', str(self.default_x_axis_len))

        if 'auto_save' not in conf:
            conf.add_section('auto_save')
        conf.set('auto_save', 'use', str(self.use_auto_save))
        conf.set('auto_save', 'append', str(self.use_append))
        conf.set('auto_save', 'interval', str(self.saving_interval))
        conf.set('auto_save', 'folder', str(self.saving_folder))

        if 'signals_set' not in conf:
            conf.add_section('signals_set')
        conf.set('signals_set', 'folder', self.signals_set_folder)

        with open(self.conf_file, 'w') as f:
            conf.write(f)
