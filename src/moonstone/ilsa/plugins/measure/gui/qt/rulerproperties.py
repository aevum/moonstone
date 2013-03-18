# -*- coding: utf-8 -*-
#
# Moonstone is platform for processing of medical images (DICOM).
# Copyright (C) 2009-2011 by Neppo Tecnologia da Informação LTDA
# and Aevum Softwares LTDA
#
# This file is part of Moonstone.
#
# Moonstone is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import logging

from PySide import QtCore, QtGui

from widget.rulerproperties_ui import Ui_RulerProperties


class RulerProperties(QtGui.QWidget, Ui_RulerProperties):

    def __init__(self, parent=None, ruler=None):
        logging.debug("In RulerProperties::__init__()")
        super(RulerProperties, self).__init__(parent)
        self._ruler = ruler
        self._rulerButton = None
        self._rulers = {}
        self._rulerButtons = {}
        self.setupUi(self)
        self._buttonGrigLayout =  QtGui.QGridLayout()
        self._buttonGrigLayout.setAlignment(QtCore.Qt.AlignLeft)
        self._buttonGroup = QtGui.QButtonGroup()
        self.rulerGroup.setLayout(self._buttonGrigLayout)
        self.createActions()
        if ruler:
            self._getPropertiesFromRuler()

    def addRuler(self, ruler):
        logging.debug("In RulerProperties::addRuler()")
        self._ruler = ruler
        self._ruler.distanceWidget.AddObserver("StartInteractionEvent", self.slotSelectButtonByRuler)
        self._ruler.distanceWidget.AddObserver("EndInteractionEvent", self.slotMeasure)
        self._rulerButton = QtGui.QPushButton()
        self._rulerButton.setCheckable(True)
        self._rulerButton.setChecked(True)
        self._rulerButton.setMinimumSize(30, 30)
        self._rulerButton.setMaximumSize(30, 30)

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/static/default/icon/48x48/ruler-diagonal.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self._rulerButton.setIcon(icon)
        self._rulerButtons[self._ruler] = self._rulerButton
        self._rulers[self._rulerButton] = self._ruler
        self._buttonGrigLayout.addWidget(self._rulerButton,(len(self._rulers)-1)/4,(len(self._rulers)-1)%4 )
        self._buttonGroup.addButton(self._rulerButton)
        self._getPropertiesFromRuler()

    def removeSelectedRuler(self):
        logging.debug("In RulerProperties::removeSelectedRuler()")
        if not self._ruler:
            return False
        self._ruler.distanceWidget.Off()
        self._buttonGroup.removeButton(self._rulerButton)
        self._buttonGrigLayout.removeWidget(self._rulerButton)
        self._rulers.pop(self._rulerButton)
        self._rulerButtons.pop(self._ruler)
        self._rulerButton.close()
        self._buttonGrigLayout.update()

        if self._rulers:
            self._ruler = self._rulers.values()[len(self._rulers) - 1]
            self._rulerButton = self._rulerButtons[self._ruler]
            self._rulerButton.setChecked(True)
            self._getPropertiesFromRuler()
        else:
            self._ruler = None
            self._rulerButton = None

        return True

    @property
    def ruler(self):
        logging.debug("In RulerProperties::ruler.getter()")
        return self._ruler

    def createActions(self):
        logging.debug("In RulerProperties::createActions")
        self.pointColorFrame.mousePressEvent = self.slotPointColorClicked
        self.fontColorFrame.mousePressEvent = self.slotFontColorClicked
        self.lineColorFrame.mousePressEvent = self.slotLineColorClicked
        self.connect(self._buttonGroup, QtCore.SIGNAL(
                      "buttonClicked ( QAbstractButton*)"),
                      self.slotRulerChoosed)

    def slotPointColorClicked(self, event):
        logging.debug("In RulerProperties::slotPointColorClicked")
        self.colorDialog = QtGui.QColorDialog()
        self.connect(self.colorDialog, QtCore.SIGNAL("colorSelected ( QColor)"), self.changePointColor)
        self.colorDialog.show()

    def slotRulerChoosed(self, button):
        logging.debug("In RulerProperties::slotRulerChoosed")
        self._rulerButton = button
        self._ruler = self._rulers[button]
        self._getPropertiesFromRuler()

    def changePointColor(self, color):
        self._ruler.pointColor = color.red()/255.0,color.green()/255.0, color.blue()/255.0
        self.pointColorFrame.setStyleSheet(
              "background-color : rgb(" + str(color.red()) + ","
              + str(color.green()) + "," + str(color.blue())
              + ");" )

    def slotLineColorClicked(self, event):
        logging.debug("In RulerProperties::slotLineColorClicked")
        self.colorDialog = QtGui.QColorDialog()
        self.connect(self.colorDialog, QtCore.SIGNAL("colorSelected ( QColor)"), self.changeLineColor)
        self.colorDialog.show()

    def changeLineColor(self, color):
        logging.debug("In RulerProperties::changeLineColor")
        self._ruler.lineColor = color.red() / 255.0, color.green() / 255.0, color.blue() / 255.0
        self.lineColorFrame.setStyleSheet(
            "background-color : rgb(" + str(color.red()) + ","
            + str(color.green()) + "," + str(color.blue())
            + ");")

    def slotFontColorClicked(self, event):
        logging.debug("In RulerProperties::slotFontColorClicked")
        self.colorDialog = QtGui.QColorDialog()
        self.connect(self.colorDialog, QtCore.SIGNAL("colorSelected ( QColor)"), self.changeFontColor)
        self.colorDialog.show()

    def changeFontColor(self, color):
        logging.debug("In RulerProperties::changeFontColor")
        self._ruler.fontColor = color.red() / 255.0, color.green() / 255.0, color.blue() / 255.0
        self.fontColorFrame.setStyleSheet(
            "background-color : rgb(" + str(color.red()) + ","
            + str(color.green()) + "," + str(color.blue())
            + ");")

    def _getPropertiesFromRuler(self):
        logging.debug("In RulerProperties::_getPropertiesFromRuler")
        lineColor = self._ruler.lineColor
        self.lineColorFrame.setStyleSheet(
              "background-color : rgb(" +  str(lineColor[0]*255)+ ","
              + str(lineColor[1]*255) + "," +  str(lineColor[2]*255)
              + ");")

        pointColor = self._ruler.pointColor
        self.pointColorFrame.setStyleSheet(
              "background-color : rgb(" +  str(pointColor[0]*255)+ ","
              +  str(pointColor[1]*255) + "," +  str(pointColor[2]*255)
              + ");")

        fontColor = self._ruler.fontColor
        self.fontColorFrame.setStyleSheet(
              "background-color : rgb(" +  str(fontColor[0]*255)+ ","
              +  str(fontColor[1]*255) + "," +  str(fontColor[2]*255)
              + ");")

        self.measureLabel.setText(str(self._ruler.measure)+" mm")

    def slotSelectButtonByRuler(self, obj, evt):
        logging.debug("In RulerProperties::slotSelectButtonByRuler")
        self._ruler = obj.parent
        self._rulerButton = self._rulerButtons[self._ruler]
        self._rulerButton.setChecked(True)
        self._getPropertiesFromRuler()

    def slotMeasure(self, obj, evt):
        logging.debug("In RulerProperties::slotMeasure")
        self._getPropertiesFromRuler()
    
    def removeScene(self, scene):
        logging.debug("In RulerProperties::removeScene")
        rulers = self._rulerButtons.keys()
        for ruler in rulers:
            if ruler.scene == scene:
                self.slotSelectButtonByRuler(ruler, None)
                self.removeSelectedRuler()