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
from pyqtgraph import AxisItem
import time
import datetime


class AxisTime(AxisItem):
    """
    Formats axis labels to human readable time.
    values  - List of time values (Format: Seconds since 1970).
    scale   - Not used.
    spacing - Not used.
    """
    def tickStrings(self, values, scale, spacing):
        """
        We override this function to have the X-axis labels display our way.
        """
        strings = []
        for x in values:
            try:
                if spacing >= 1:
                    strings.append(time.strftime("%H:%M:%S",
                                                 time.localtime(x)))
                else:
                    # Generate date from timesamp
                    date = datetime.datetime.fromtimestamp(x)
                    # Format with millisecond
                    date = date.strftime("%M:%S.%f")[:-3]
                    strings.append(date)
            except ValueError:  # Time out of range.
                strings.append('')
        return strings
