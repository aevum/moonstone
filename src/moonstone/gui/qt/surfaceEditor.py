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
import copy

class SurfaceEditor(QtGui.QFrame):    
    def __init__(self, parent, callbackFunction):        
        super(SurfaceEditor, self).__init__(parent, QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool | QtCore.Qt.Window)
        self.parentWindow = parent
        self.createWidgets()
        self.createActions()
        self.callbackFunction = callbackFunction  
   
    def createWidgets(self):    
        self.surface = {}    
        self.surface["r"] = 1.0
        self.surface["g"] = 1.0
        self.surface["b"] = 0.6        
        self.surface["value"] = 600
           
        self.nameLabel = QtGui.QLabel("Name:")        
        self.surfaceName = QtGui.QLineEdit()
        self.surfaceName.setMaximumWidth(70)
        
        self.valueLabel = QtGui.QLabel("Value:")   
        self.value = QtGui.QLineEdit(str(self.surface["value"]))
        self.value.setInputMask("#0000")
        self.value.setMinimumHeight(30)
        self.value.setMaximumHeight(30)
        self.value.setMinimumWidth(45)
        self.value.setMaximumWidth(45)
                       
        self.colorButton = QtGui.QToolButton()
        self.colorButton.setMinimumSize(30, 30)
        self.colorButton.setMaximumSize(30, 30)
        self.colorButton.setStyleSheet("background-repeat: no-repeat;\
                                   background-position: 50% 50%;\
                                   background-color : rgb({0},{1},{2})".format(int(self.surface["r"] * 255), int(self.surface["g"] *255), int(self.surface["b"] *255)))
        
        self.okButton = QtGui.QPushButton("&OK")
        self.okButton.setMinimumHeight(20)
        self.okButton.setMinimumWidth(40)
        
        self.cancelButton = QtGui.QPushButton("&Cancel")
        self.cancelButton.setMinimumHeight(20)
        self.cancelButton.setMinimumWidth(40)
        
        windowLayout = QtGui.QHBoxLayout(self)
        windowLayout.addWidget(self.nameLabel)
        windowLayout.addWidget(self.surfaceName)
        windowLayout.addWidget(self.valueLabel)
        windowLayout.addWidget(self.value)
        windowLayout.addWidget(self.colorButton)
        windowLayout.addWidget(self.okButton)
        windowLayout.addWidget(self.cancelButton)
        
        self.colorDialog = QtGui.QColorDialog()                
    
    def createActions(self):
        self.connect(self.okButton, QtCore.SIGNAL("clicked()"), self.slotAddSurface)
        self.connect(self.cancelButton, QtCore.SIGNAL("clicked()"), self.hide)
        self.connect(self.colorButton, QtCore.SIGNAL("clicked()"), self.colorDialog.show)
        self.connect(self.colorDialog, QtCore.SIGNAL("colorSelected ( QColor)"), self.callbackColor)
        
#    def slotColorButtonClicked(self):
#        self.colorDialog.show()
        
    def callbackColor(self, color):
        self.surface["r"] = color.red() / 255.0
        self.surface["g"] = color.green() / 255.0
        self.surface["b"] = color.blue() / 255.0
        self.colorButton.setStyleSheet("background-repeat: no-repeat;\
                               background-position: 50% 50%;\
                               background-color : rgb({0},{1},{2})".format(color.red(), color.green(), color.blue()))
        
    def slotAddSurface(self):
        self.surface["name"] =  self.surfaceName.text()
        self.surface["value"] =  int(self.value.text())
        if self.callbackFunction(copy.copy(self.surface)):
            self.hide()
        else:
            msgBox = QtGui.QMessageBox()
            msgBox.setText(QtGui.QApplication.translate(
                    "SurfaceEditor", "Name already exist!",
                    None, QtGui.QApplication.UnicodeUTF8))
            msgBox.exec_()
   
  