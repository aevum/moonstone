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
from .widget.hounsfieldColorSegmentEditor_ui import Ui_HounsfieldColorSegmentEditor 

class HounsfieldColorSegmentEditor(QtGui.QFrame, Ui_HounsfieldColorSegmentEditor):    
    def __init__(self, parent, callbackFunction, segmentBase=[]):        
        super(HounsfieldColorSegmentEditor, self).__init__(parent, QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)
        self.parentWindow = parent
        self.setupUi(self)
        self.createWidgets()
        self.createActions()
        self.callbackFunction = callbackFunction
        self.setSegment(segmentBase)     
   
    def createWidgets(self):
        self.pointsLayout = QtGui.QVBoxLayout()
        self.scrollAreaWidgetContents.setLayout(self.pointsLayout)
            
    
    def createActions(self):
        self.connect(self.newPointButton, QtCore.SIGNAL("clicked()"),
                     self.slotNewPointClicked)
        self.connect(self.cancelButton, QtCore.SIGNAL("clicked()"),
                     self.cancelButtonClicked)
        self.connect(self.okButton, QtCore.SIGNAL("clicked()"),
                     self.slotOkClicked)
        
    def slotNewPointClicked(self):
        self.addPoint({"x": 0.5, "r": 0.0, "g": 0.0, "b": 0.0, "midpoint": 0.5, "sharpness": 0.0})
        self.callbackFunction(self.getSegment()) 
        self.parentWindow.preview()
    
    def slotOkClicked(self):
        self.callbackFunction(self.getSegment()) 
        self.close()   
        
    def getSegment(self):
        result = []
        for point in self.visualPoints:
            result.append({"x": float(point["x"].text()), "r": point["r"], "g": point["g"], "b": point["b"], 
                           "midpoint": float(point["midpoint"].text()), "sharpness": float(point["sharpness"].text())})
        return result

    def cancelButtonClicked(self):
        self.close()
    
    def setSegment(self, points):
        self.points = []
        for point in points:
            self.points.append(point)
        self.points.sort(lambda x, y : int((x["x"] - y["x"]) * 1000))
        self.resetPointsWidget()
            
    def resetPointsWidget(self):
        self.visualPoints = []
#        self.pointsLayout = QtGui.QVBoxLayout()
#        self.scrollAreaWidgetContents.setLayout(self.pointsLayout)
        for point in self.points:
            self.addPoint(point)
            
    def addPoint(self, point):
        doubleXVal = QtGui.QDoubleValidator( -10.0, 10.0, 3, self )
        doubleVal = QtGui.QDoubleValidator( 0.0, 1.0, 3, self )
        vPoint = {}
        line = QtGui.QWidget()
        line.setMinimumHeight(30)
        self.pointsLayout.addWidget(line)
        hLayout = QtGui.QHBoxLayout()
        line.setLayout(hLayout)
        x = QtGui.QLineEdit(str(point["x"]))
        x.setValidator(doubleXVal)
        x.setInputMask("#0.00")
        x.setMaxLength(4)
        x.setMinimumHeight(20)
        x.setMaximumWidth(35)
        x.setMinimumWidth(35)
        
#        colorButton = QtGui.QPushButton()
#        colorButton.setPalette(QtGui.QPalette(QtGui.QColor(int(point["r"] * 255), int(point["g"] *255), int(point["b"] *255))))
#        colorButton.setMinimumHeight(20)
#        colorButton.setMaximumWidth(35)
#        colorButton.setMinimumWidth(35)
        
        colorButton = QtGui.QToolButton()
#        colorButton.setCheckable(True)
#        colorButton.setChecked(True)
        colorButton.setMinimumSize(30, 30)
        colorButton.setMaximumSize(30, 30)

        #icon = QtGui.QIcon()
        #icon.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/implant.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        colorButton.setStyleSheet("background-repeat: no-repeat;\
                                   background-position: 50% 50%;\
                                   background-color : rgb({0},{1},{2})".format(int(point["r"] * 255), int(point["g"] *255), int(point["b"] *255)))
        self.connect(colorButton, QtCore.SIGNAL("clicked()"), lambda : self.changePointColor(vPoint))
        
        if point.has_key("midpoint"):
            midpoint = QtGui.QLineEdit(str(point["midpoint"]))
        else:
            midpoint = QtGui.QLineEdit("0.50")
        midpoint.setValidator(doubleVal)
        midpoint.setInputMask("0.00")
        midpoint.setMaxLength(3)
        midpoint.setMinimumHeight(20)
        midpoint.setMinimumWidth(35)
        midpoint.setMaximumWidth(35)
        if point.has_key("sharpness"):
            sharpness = QtGui.QLineEdit(str(point["sharpness"]))
        else:
            sharpness = QtGui.QLineEdit("0.00")
        sharpness.setValidator(doubleVal)
        sharpness.setInputMask("0.00")
        sharpness.setMaxLength(3)
        sharpness.setMinimumHeight(20)
        sharpness.setMinimumWidth(35)
        sharpness.setMaximumWidth(35)
        
        l = QtGui.QLabel("x:")
        l.setMinimumHeight(20)
        hLayout.addWidget(l)
        hLayout.addWidget(x)
          
        hLayout.addWidget(colorButton)                
                                  
        l = QtGui.QLabel("midpoint:")
        l.setMinimumHeight(20)
        hLayout.addWidget(l)
        hLayout.addWidget(midpoint)
        
        l = QtGui.QLabel("sharpness:")
        l.setMinimumHeight(20)
        hLayout.addWidget(l)
        hLayout.addWidget(sharpness)
    
        button = QtGui.QPushButton()
        button.setMinimumHeight(20)
        button.setMinimumWidth(40)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/edit-delete.png"), 
                       QtGui.QIcon.Normal, 
                       QtGui.QIcon.Off)
        button.setIcon(icon)
        self.connect(button, QtCore.SIGNAL("clicked()"),
                     lambda : self.slotRemovePointClicked(vPoint))        
        hLayout.addWidget(button)
        
        vPoint["x"] = x
        vPoint["midpoint"] = midpoint
        vPoint["sharpness"] = sharpness 
        vPoint["line"] = line
        vPoint["button"] = button
        vPoint["r"] = point["r"] 
        vPoint["g"] = point["g"] 
        vPoint["b"] = point["b"]
        vPoint["colorButton"] = colorButton
        hLayout.addItem(QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        
        self.connect(x, QtCore.SIGNAL("textChanged(QString)"), self.pointXChanged)
        self.connect(midpoint, QtCore.SIGNAL("textChanged(QString)"), self.pointValueChanged)
        self.connect(sharpness, QtCore.SIGNAL("textChanged(QString)"), self.pointValueChanged)
        self.visualPoints.append(vPoint)
    
    def changePointColor(self, vPoint):
        self.colorDialog = QtGui.QColorDialog()                
        def callback(color):
            vPoint["r"] = color.red() / 255.0
            vPoint["g"] = color.green() / 255.0
            vPoint["b"] = color.blue() / 255.0
            vPoint["colorButton"].setStyleSheet("background-repeat: no-repeat;\
                                   background-position: 50% 50%;\
                                   background-color : rgb({0},{1},{2})".format(color.red(), color.green(), color.blue()))
            self.callbackFunction(self.getSegment()) 
            self.parentWindow.preview()
        self.connect(self.colorDialog, QtCore.SIGNAL("colorSelected ( QColor)"), callback)
        self.colorDialog.show()
    
    def slotRemovePointClicked(self, point):
        self.visualPoints.remove(point)
        self.pointsLayout.removeWidget(point["line"])
        self.callbackFunction(self.getSegment()) 
        self.parentWindow.preview()
    
    def pointValueChanged(self):
        self.callbackFunction(self.getSegment()) 
        self.parentWindow.preview()
        
        
    def pointXChanged(self):
        lastX = None
        reorder =  False
        for point in self.visualPoints:
            if lastX != None:
                if float(point["x"].text()) < lastX:
                    reorder = True
                    break
            lastX = float(point["x"].text())
        if reorder:
            self.sortLines()
        self.callbackFunction(self.getSegment()) 
        self.parentWindow.preview()
    
    def sortLines(self):
        for point in self.visualPoints:
            self.pointsLayout.removeWidget(point["line"])
        self.visualPoints.sort(lambda x, y : int((float(x["x"].text()) - float(y["x"].text())) * 1000))       
        for point in self.visualPoints:
            self.pointsLayout.addWidget(point["line"])
    
  