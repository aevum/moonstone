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
import logging
import vtk
from widget.textproperties_ui import Ui_TextProperties
import unicodedata


class TextProperties(QtGui.QWidget, Ui_TextProperties):

    def __init__(self, parent=None, text=None):
        super(TextProperties, self).__init__(parent)
        self.text = text
        self.textButton = None
        self.texts = {}
        self.textButtons = {}
        self.setupUi(self)
        self.buttonGrigLayout =  QtGui.QGridLayout()
        self.buttonGrigLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.buttonGroup = QtGui.QButtonGroup()
        self.textGroup.setLayout(self.buttonGrigLayout)
        self.createActions()
        if text:
            self._getPropertiesFromText()

    def addText(self, text):
        self.text = text
        self.text.AddObserver("StartInteractionEvent", self.slotSelectButtonByText)
        self.text.AddObserver("EndInteractionEvent", self.slotMeasure)
        self.textButton = QtGui.QPushButton()
        self.textButton.setCheckable(True)
        self.textButton.setChecked(True)
        self.textButton.setMinimumSize(30, 30)
        self.textButton.setMaximumSize(30, 30)

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/text.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.textButton.setIcon(icon)
        self.textButtons[self.text] = self.textButton
        self.texts[self.textButton] = self.text
        self.buttonGrigLayout.addWidget(self.textButton,(len(self.texts)-1)/4,(len(self.texts)-1)%4 )
        self.buttonGroup.addButton(self.textButton)
        self._getPropertiesFromText()

    def removeSelectedText(self):
        if not self.text:
            return False
        self.text.Off()
        if self.text.scene:
            self.text.scene.renderer.RemoveActor(self.text.textActor)
            self.text.scene.window.Render()
        self.buttonGroup.removeButton(self.textButton)
        self.buttonGrigLayout.removeWidget(self.textButton)
        self.texts.pop(self.textButton)
        self.textButtons.pop(self.text)
        self.textButton.close()
        self.buttonGrigLayout.update()
        self.text.removeObservers()
        if self.texts:
            self.text = self.texts.values()[0]
            self.textButton = self.textButtons[self.text]
            self.textButton.setChecked(True)
            self._getPropertiesFromText()
        else:
            self.text = None
            self.textButton = None

        return True


    def getText(self):
        return self.text

    def createActions(self):
        self.fontColor.mousePressEvent = self.slotFontColorClicked
        self.connect(self.buttonGroup, QtCore.SIGNAL(
                      "buttonClicked ( QAbstractButton*)"),
                      self.slotTextChoosed)
        self.connect(self.textField, QtCore.SIGNAL(
                      "textChanged ( QString)"),
                      self.slotTextChanged)
        self.connect(self.fontSize, QtCore.SIGNAL("valueChanged ( int)"),
                      self.slotFontSizeChanged)
        self.connect(self.fontCombo, QtCore.SIGNAL("currentIndexChanged ( QString )"), self.slotFontChanged)
        self.connect(self.bold, QtCore.SIGNAL("clicked ( bool)"), self.slotActionBold)
        self.connect(self.italic, QtCore.SIGNAL("clicked ( bool)"), self.slotActionItalic)
        self.connect(self.visible, QtCore.SIGNAL("clicked ( bool)"), self.slotActionVisible)
    
    def slotActionBold(self, bold):
        if self.text:
            self.text.setBold(bold)
    
    def slotFontChanged(self, font):
        if self.text:
            self.text.setFont(font)
    
    def slotActionItalic(self, italic):
        if self.text:
            self.text.setItalic(italic)
    
    def slotActionVisible(self, visible):
        if self.text:
            self.text.setVisible(visible)

    def slotFontSizeChanged(self, size):
        if self.text:
            self.text.setFontSize(size)

    
    def slotTextChanged(self, newText):
        if self.text:
            if isinstance(newText, unicode):
                newText = unicodedata.normalize('NFKD', newText).encode('ascii','ignore')
            self.text.setText(newText)
    
    def slotTextChoosed(self, button):
        self.textButton = button
        self.text = self.texts[button]
        self._getPropertiesFromText()


    def slotFontColorClicked(self, event):
        self.colorDialog = QtGui.QColorDialog()
        self.connect(self.colorDialog, QtCore.SIGNAL("colorSelected ( QColor)"), self.changeFontColor)
        self.colorDialog.show()

    def changeFontColor(self, color):
        self.text.setFontColor(color.red()/255.0, color.green()/255.0, color.blue()/255.0)
        self.fontColor.setStyleSheet(
              "background-color : rgb(" + str(color.red()) + ","
              + str(color.green()) + "," + str(color.blue())
              + ");" )

    def _getPropertiesFromText(self):
        fontColor = self.text.getFontColor()
        self.fontColor.setStyleSheet(
              "background-color : rgb(" +  str(fontColor[0]*255)+ ","
              +  str(fontColor[1]*255) + "," +  str(fontColor[2]*255)
              + ");" )

        self.textField.setText(self.text.getText())
        self.bold.setChecked(self.text.getBold())
        self.italic.setChecked(self.text.getItalic())
        self.visible.setChecked(self.text.getVisible())
        self.fontSize.setValue(self.text.getFontSize())
        font = self.text.getFont()
        for i in range(self.fontCombo.count()):
            if self.fontCombo.itemText(i) == font:
                self.fontCombo.setCurrentIndex(i)
                break

    def slotSelectButtonByText(self, obj, evt):
        self.text = obj
        self.textButton = self.textButtons[self.text]
        self.textButton.setChecked(True)
        self._getPropertiesFromText()

    def slotMeasure(self, obj, evt):
        self._getPropertiesFromText()
   
    def removeScene(self, scene):
        texts = self.textButtons.keys()
        for text in texts:
            if text.scene == scene:
                self.slotSelectButtonByText(text, None)
                self.removeSelectedText()
            
if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    win = TextProperties()
    win.show()
    sys.exit(app.exec_())

