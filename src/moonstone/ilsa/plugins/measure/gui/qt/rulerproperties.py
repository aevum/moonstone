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
from PySide import QtCore, QtGui

from widget.rulerproperties_ui import Ui_RulerProperties


class RulerProperties(QtGui.QWidget, Ui_RulerProperties):

    def __init__(self, parent=None, ruler=None):
        super(RulerProperties, self).__init__(parent)
        self.ruler = ruler
        self.rulerButton = None
        self.rulers = {}
        self.rulerButtons = {}
        self.setupUi(self)
        self.buttonGrigLayout =  QtGui.QGridLayout()
        self.buttonGrigLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.buttonGroup = QtGui.QButtonGroup()
        self.rulerGroup.setLayout(self.buttonGrigLayout)
        self.createActions()
        if ruler:
            self._getPropertiesFromRuler()

    def addRuler(self, ruler):
        self.ruler = ruler
        self.ruler.AddObserver("StartInteractionEvent", self.slotSelectButtonByRuler)
        self.ruler.AddObserver("EndInteractionEvent", self.slotMeasure)
        self.rulerButton = QtGui.QPushButton()
        self.rulerButton.setCheckable(True)
        self.rulerButton.setChecked(True)
        self.rulerButton.setMinimumSize(30, 30)
        self.rulerButton.setMaximumSize(30, 30)

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/static/default/icon/48x48/ruler-diagonal.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.rulerButton.setIcon(icon)
        self.rulerButtons[self.ruler] = self.rulerButton
        self.rulers[self.rulerButton] = self.ruler
        self.buttonGrigLayout.addWidget(self.rulerButton,(len(self.rulers)-1)/4,(len(self.rulers)-1)%4 )
        self.buttonGroup.addButton(self.rulerButton)
        self._getPropertiesFromRuler()

    def removeSelectedRuler(self):
        if not self.ruler:
            return False
        self.ruler.Off()
        self.buttonGroup.removeButton(self.rulerButton)
        self.buttonGrigLayout.removeWidget(self.rulerButton)
        self.rulers.pop(self.rulerButton)
        self.rulerButtons.pop(self.ruler)
        self.rulerButton.close()
        self.buttonGrigLayout.update()

        if self.rulers:
            self.ruler = self.rulers.values()[0]
            self.rulerButton = self.rulerButtons[self.ruler]
            self.rulerButton.setChecked(True)
            self._getPropertiesFromRuler()
        else:
            self.ruler = None
            self.rulerButton = None

        return True


    def getRuler(self):
        return self.ruler

    def createActions(self):
        self.pointColorFrame.mousePressEvent = self.slotPointColorClicked
        self.fontColorFrame.mousePressEvent = self.slotFontColorClicked
        self.lineColorFrame.mousePressEvent = self.slotLineColorClicked
        self.connect(self.buttonGroup, QtCore.SIGNAL(
                      "buttonClicked ( QAbstractButton*)"),
                      self.slotRulerChoosed)

    def slotPointColorClicked(self, event):
        self.colorDialog = QtGui.QColorDialog()
        self.connect(self.colorDialog, QtCore.SIGNAL("colorSelected ( QColor)"), self.changePointColor)
        self.colorDialog.show()

    def slotRulerChoosed(self, button):
        self.rulerButton = button
        self.ruler = self.rulers[button]
        self._getPropertiesFromRuler()

    def changePointColor(self, color):
        self.ruler.setPointColor(color.red()/255.0,color.green()/255.0, color.blue()/255.0)
        self.pointColorFrame.setStyleSheet(
              "background-color : rgb(" + str(color.red()) + ","
              + str(color.green()) + "," + str(color.blue())
              + ");" )

    def slotLineColorClicked(self, event):
        self.colorDialog = QtGui.QColorDialog()
        self.connect(self.colorDialog, QtCore.SIGNAL("colorSelected ( QColor)"), self.changeLineColor)
        self.colorDialog.show()

    def changeLineColor(self, color):
        self.ruler.setLineColor(color.red()/255.0, color.green()/255.0, color.blue()/255.0)
        self.lineColorFrame.setStyleSheet(
              "background-color : rgb(" + str(color.red()) + ","
              + str(color.green()) + "," + str(color.blue())
              + ");" )

    def slotFontColorClicked(self, event):
        self.colorDialog = QtGui.QColorDialog()
        self.connect(self.colorDialog, QtCore.SIGNAL("colorSelected ( QColor)"), self.changeFontColor)
        self.colorDialog.show()

    def changeFontColor(self, color):
        self.ruler.setFontColor(color.red()/255.0, color.green()/255.0, color.blue()/255.0)
        self.fontColorFrame.setStyleSheet(
              "background-color : rgb(" + str(color.red()) + ","
              + str(color.green()) + "," + str(color.blue())
              + ");" )

    def _getPropertiesFromRuler(self):
        lineColor = self.ruler.getLineColor()
        self.lineColorFrame.setStyleSheet(
              "background-color : rgb(" +  str(lineColor[0]*255)+ ","
              + str(lineColor[1]*255) + "," +  str(lineColor[2]*255)
              + ");" )

        pointColor = self.ruler.getPointColor()
        self.pointColorFrame.setStyleSheet(
              "background-color : rgb(" +  str(pointColor[0]*255)+ ","
              +  str(pointColor[1]*255) + "," +  str(pointColor[2]*255)
              + ");" )

        fontColor = self.ruler.getFontColor()
        self.fontColorFrame.setStyleSheet(
              "background-color : rgb(" +  str(fontColor[0]*255)+ ","
              +  str(fontColor[1]*255) + "," +  str(fontColor[2]*255)
              + ");" )

        self.measureLabel.setText(str(self.ruler.getMeasure())+" mm")

    def slotSelectButtonByRuler(self, obj, evt):
        self.ruler = obj
        self.rulerButton = self.rulerButtons[self.ruler]
        self.rulerButton.setChecked(True)
        self._getPropertiesFromRuler()

    def slotMeasure(self, obj, evt):
        self._getPropertiesFromRuler()
    
    def removeScene(self, scene):
        rulers = self.rulerButtons.keys()
        for ruler in rulers:
            if ruler.scene == scene:
                self.slotSelectButtonByRuler(ruler, None)
                self.removeSelectedRuler()

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    win = RulerProperties()
    win.show()
    sys.exit(app.exec_())

