#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
#
# Custom radio button for color chooser palette
#
# latest rev by valerix
# feb 4 2021
#
# -----------------------------------------------------------------------------

from PyQt5 import QtCore, QtGui, QtWidgets


class Square_RadioBtn(QtWidgets.QRadioButton):
    """Custom radio button for color chooser palette."""

    def paintEvent(self, event):
        # draw the widget as paintEvent normally does
        # super(Square_RadioBtn, self).paintEvent(event)

        # create a new painter on the widget
        qp = QtGui.QPainter(self)
        # create a styleoption and init it with the button
        opt = QtGui.QStyleOptionButton()
        self.initStyleOption(opt)

        # if there is an icon, draw it, otherwise draw a filled rect
        if not self.icon().isNull():
            # we have an icon: draw it
            self.icon().paint(qp, self.rect())
        else:
            # no icon: just fill a rect with the right color
            # retrieve color from stylesheet "color" attribute
            thecolor = self.palette().color(QtGui.QPalette.WindowText)
            # print(thecolor.name())
            qp.fillRect(self.rect(), thecolor)

        # now we can know if the widget is hovered and/or checked
        blackpen = QtGui.QPen()
        blackpen.setWidth(4)
        blackpen.setColor(QtCore.Qt.black)
        qp.setPen(blackpen)

        # if selected, draw a frame around it
        if opt.state & (QtGui.QStyle.State_MouseOver | QtGui.QStyle.State_On):
            # ON state
            qp.drawRect(self.rect())
            # print("ON")
        else:
            # OFF state
            # print("OFF")
            pass
