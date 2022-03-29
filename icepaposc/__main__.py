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

import sys
from PyQt5.QtWidgets import QApplication
from .window_main import WindowMain
import argparse
from . import version


def get_parser():
    desc = 'IcePAP Oscilloscope Application, base on ethernet communication\n'
    desc += 'Version: {}.\n'.format(version)
    epi = 'Documentation: https://alba-synchrotron.github.io/pyIcePAP-doc/\n'
    epi += 'Copyright 2017:\n' \
           '   MAX IV Laboratory, Lund, Sweden\n' \
           '   CELLS / ALBA Synchrotron, Bellaterra, Spain.'
    fmt = argparse.RawTextHelpFormatter
    parse = argparse.ArgumentParser(description=desc,
                                    formatter_class=fmt,
                                    epilog=epi)
    ver = '%(prog)s {0}'.format(version)

    parse.add_argument('--version', action='version', version=ver)

    parse.add_argument('host', help='IcePAP Host')
    parse.add_argument('--axis', help='Selected axis', default=1, type=int)
    parse.add_argument('-p', '--port', type=int, default=5000,
                       help='IcePAP port')
    parse.add_argument('-t', '--timeout', type=int, default=3,
                       help='Socket timeout')
    parse.add_argument('--sigset', default='',
                       help='.lst filename to import signals from')
    parse.add_argument('-s', '--sig', nargs='*', default=[],
                       help='Preselected signals '
                            '<driver>:<signal name>:<Y-axis>')

    # TODO: Allow to pass the axes preselected and type of graph
    # parse.add_argument('-a', nargs='*', help='Axes to save, default all',
    #                    type=int, default=[])
    # save_cmd.add_argument('-d', '--debug', action='store_true',
    #                       help='Activate log level DEBUG')

    return parse


def main():
    args = get_parser().parse_args()
    print(args)

    app = QApplication(sys.argv)
    win = WindowMain(args.host, args.port, args.timeout, args.sig, args.axis, args.sigset)
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
