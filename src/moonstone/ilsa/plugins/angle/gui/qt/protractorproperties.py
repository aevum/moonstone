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

from widget.protractorproperties_ui import Ui_ProtractorProperties


class ProtractorProperties(QtGui.QWidget, Ui_ProtractorProperties):

    def __init__(self, parent=None, protractor=None):
        logging.debug("In ProtractorProperties::__init__()")
        super(ProtractorProperties, self).__init__(parent)
        self.protractor = protractor
        self.protractorButton = None
        self.protractors = {}
        self.protractorButtons = {}
        self.setupUi(self)
        self.buttonGrigLayout =  QtGui.QGridLayout()
        self.buttonGrigLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.buttonGroup = QtGui.QButtonGroup()
        self.protractorGroup.setLayout(self.buttonGrigLayout)
        self.createActions()
        if self.protractor:
            self._getPropertiesFromProtractor()


    def addProtractor(self, protractor):
        logging.debug("In ProtractorProperties::addProtractor()")
        self.protractor = protractor
        self.protractor.angleWidget.AddObserver("StartInteractionEvent", self.slotSelectButtonByProtractor)
        self.protractor.angleWidget.AddObserver("EndInteractionEvent", self.slotMeasure)
        self.protractorButton = QtGui.QPushButton()
        self.protractorButton.setCheckable(True)
        self.protractorButton.setChecked(True)
        self.protractorButton.setMinimumSize(30, 30)
        self.protractorButton.setMaximumSize(30, 30)

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/static/default/icon/48x48/transferidor.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.protractorButton.setIcon(icon)
        self.protractorButtons[self.protractor] = self.protractorButton
        self.protractors[self.protractorButton] = self.protractor
        self.buttonGrigLayout.addWidget(self.protractorButton,(len(self.protractors)-1)/4,(len(self.protractors)-1)%4 )
        self.buttonGroup.addButton(self.protractorButton)
        self._getPropertiesFromProtractor()

    def removeSelectedProtractor(self):
        logging.debug("In ProtractorProperties::removeSelectedProtractor()")
        if not self.protractor:
            return None
        self.protractor.angleWidget.Off()
        self.buttonGroup.removeButton(self.protractorButton)
        self.buttonGrigLayout.removeWidget(self.protractorButton)
        self.protractors.pop(self.protractorButton)
        try:
            self.protractorButtons.pop(self.protractor)
        except:
            pass
        self.protractorButton.close()
        self.buttonGrigLayout.update()
        if self.protractors:
            self.protractor = self.protractors.values()[0]
            self.protractorButton = self.protractorButtons[self.protractor]
            self.protractorButton.setChecked(True)
            self._getPropertiesFromProtractor()
        else:
            return None
        return self.protractor


    def createActions(self):
        logging.debug("In ProtractorProperties::createActions()")
        self.fontColorFrame.mousePressEvent = self.slotFontColorClicked
        self.lineColorFrame.mousePressEvent = self.slotLineColorClicked
        self.connect(self.buttonGroup, QtCore.SIGNAL(
                      "buttonClicked ( QAbstractButton*)"),
                      self.slotProtractorChoosed)

    def slotFontSizeChanged(self, size):
        logging.debug("In ProtractorProperties::slotFontSizeChanged()")
        self.protractor.setFontSize(size)

    def slotProtractorChoosed(self, button):
        logging.debug("In ProtractorProperties::slotProtractorChoosed()")
        self.protractorButton = button
        self.protractor = self.protractors[button]
        self._getPropertiesFromProtractor()

    def slotLineColorClicked(self, event):
        logging.debug("In ProtractorProperties::slotLineColorClicked()")
        self.colorDialog = QtGui.QColorDialog()
        self.connect(self.colorDialog, QtCore.SIGNAL("colorSelected ( QColor)"), self.changeLineColor)
        self.colorDialog.show()

    def changeLineColor(self, color):
        logging.debug("In ProtractorProperties::changeLineColor()")
        self.protractor.lineColor = [color.red()/255.0, color.green()/255.0, color.blue()/255.0]
        self.lineColorFrame.setStyleSheet(
              "background-color : rgb(" + str(color.red()) + ","
              + str(color.green()) + "," + str(color.blue())
              + ");" )

    def slotFontColorClicked(self, event):
        logging.debug("In ProtractorProperties::slotFontColorClicked()")
        self.colorDialog = QtGui.QColorDialog()
        self.connect(self.colorDialog, QtCore.SIGNAL("colorSelected ( QColor)"), self.changeFontColor)
        self.colorDialog.show()

    def changeFontColor(self, color):
        logging.debug("In ProtractorProperties::changeFontColor()")
        self.protractor.fontColor = (color.red()/255.0, color.green()/255.0, color.blue()/255.0)
        self.fontColorFrame.setStyleSheet(
              "background-color : rgb(" + str(color.red()) + ","
              + str(color.green()) + "," + str(color.blue())
              + ");" )

    def _getPropertiesFromProtractor(self):
        logging.debug("In ProtractorProperties::_getPropertiesFromProtractor()")
        lineColor = self.protractor.lineColor
        self.lineColorFrame.setStyleSheet(
              "background-color : rgb(" +  str(lineColor[0]*255)+ ","
              + str(lineColor[1]*255) + "," +  str(lineColor[2]*255)
              + ");" )

        self.angleLabel.setText("{0:.2f}".format(self.protractor.angle))


    def slotSelectButtonByProtractor(self, obj, evt):
        logging.debug("In ProtractorProperties::slotSelectButtonByProtractor()")
        self.protractor = obj.parent
        self.protractorButton = self.protractorButtons[self.protractor]
        self.protractorButton.setChecked(True)
        self._getPropertiesFromProtractor()

    def slotMeasure(self, obj, evt):
        logging.debug("In ProtractorProperties::slotMeasure()")
        self._getPropertiesFromProtractor()
    
    def removeScene(self, scene):
        logging.debug("In ProtractorProperties::removeScene()")
        protractors = self.protractorButtons.keys()
        for protractor in protractors:
            if protractor.scene() == scene:
                self.slotSelectButtonByProtractor(protractor, None)
                self.removeSelectedProtractor()