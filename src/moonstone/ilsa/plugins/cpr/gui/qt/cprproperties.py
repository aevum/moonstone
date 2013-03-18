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

from widget.cprproperties_ui import Ui_CPRProperties


class CPRProperties(QtGui.QWidget, Ui_CPRProperties):

    def __init__(self, parent=None, contour=None):
        super(CPRProperties, self).__init__(parent)
        self.contour = contour
        self.contourButton = None
        self.contours = {}
        self.contourButtons = {}
        self.setupUi(self)
        self.buttonGrigLayout =  QtGui.QGridLayout()
        self.buttonGrigLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.buttonGroup = QtGui.QButtonGroup()
        self.cprGroup.setLayout(self.buttonGrigLayout)
        self.createActions()
        if contour:
            self._getPropertiesFromContour()

    def addContour(self, contour):
        for c in self.contourButtons.keys():
            c.lock()
        self.contour = contour
#        contour.contourWidget.AddObserver("StartInteractionEvent", self.slotSelectButtonByContour)
        self.contourButton = QtGui.QPushButton()
        self.contourButton.setCheckable(True)
        self.contourButton.setChecked(True)
        self.contourButton.setMinimumSize(30, 30)
        self.contourButton.setMaximumSize(30, 30)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/static/default/icon/48x48/panoramic-grey.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.contourButton.setIcon(icon)
        self.contourButtons[self.contour] = self.contourButton
        self.contours[self.contourButton] = self.contour
        self.buttonGrigLayout.addWidget(self.contourButton,(len(self.contours)-1)/4,(len(self.contours)-1)%4 )
        self.buttonGroup.addButton(self.contourButton)
        self._getPropertiesFromContour()

    def removeSelectedContour(self):
        if not self.contour:
            return False
        self.contour.delete()
        #for contour in self.contour.getReplyList():
        #    contour.delete()
        self.buttonGroup.removeButton(self.contourButton)
        self.buttonGrigLayout.removeWidget(self.contourButton)
        self.contours.pop(self.contourButton)
        self.contourButtons.pop(self.contour)
        self.contourButton.close()
        self.buttonGrigLayout.update()


        if self.contours:
            self.contour = self.contours.values()[0]
            self.contourButton = self.contourButtons[self.contour]
            self.contourButton.setChecked(True)
            self._getPropertiesFromContour()
        else:
            self.contour = None
            self.rulerButton = None

        return True
    
    def lockAll(self):
        for contour in self.contours.values():
            contour.lock()

    def unlockCurrent(self):
        self._getPropertiesFromContour()
        self.contour.unlock()
        self.lock.setChecked(0)

    def getContour(self):
        return self.contour

    def createActions(self):
        self.lineColorFrame.mousePressEvent = self.slotLineColorClicked
        self.actualLineColorFrame.mousePressEvent = self.slotActualLineColorClicked
        self.connect(self.transversalSize, QtCore.SIGNAL(
                      "valueChanged ( int )"),
                      self.slotTransversalSizeChanged)
        self.connect(self.buttonGroup, QtCore.SIGNAL(
                      "buttonClicked ( QAbstractButton*)"),
                      self.slotContourChoosed)
        self.connect(self.lock,
                                QtCore.SIGNAL("clicked ( bool)"),
                                self.slotActionLock)
        self.connect(self.visible,
                                QtCore.SIGNAL("clicked ( bool)"),
                                self.slotActionVisible)


    def slotActionLock(self, checked):
        if checked:
            self.contour.lock()
        else:
            self.contour.unlock() 
            

    def slotActionVisible(self, checked):
        self.contour.setVisible(checked)



    def slotContourChoosed(self, obj):
        try :
            self.contour = self.contours[obj]
            self.contourButton = self.contourButtons[self.contour]
            for c in self.contourButtons.keys():
                if c != self.contour:
                    c.lock()
            self.contour.unlock()
        except:
            lst = self.contours[obj]
            for contour in lst:
                try :
                    self.contour = contour
                    self.contourButton = self.contourButtons[self.contour]
                    break
                except:
                    pass
        self._getPropertiesFromContour()



    def slotLineColorClicked(self, event):
        self.colorDialog = QtGui.QColorDialog()
        self.connect(self.colorDialog, QtCore.SIGNAL("colorSelected ( QColor)"), self.changeLineColor)
        self.colorDialog.show()

    def changeLineColor(self, color):
        self.contour.setLineColor(color.red()/255.0, color.green()/255.0, color.blue()/255.0)
        lst = self.contour.getReplyList()
        for contour in lst:
            contour.setLineColor(color.red()/255.0, color.green()/255.0, color.blue()/255.0)
        self.lineColorFrame.setStyleSheet(
              "background-color : rgb(" + str(color.red()) + ","
              + str(color.green()) + "," + str(color.blue())
              + ");" )
        
    def slotActualLineColorClicked(self, event):
        self.colorDialog = QtGui.QColorDialog()
        self.connect(self.colorDialog, QtCore.SIGNAL("colorSelected ( QColor)"), self.changeActualLineColor)
        self.colorDialog.show()

    def changeActualLineColor(self, color):
        self.contour.setActualLineColor(color.red()/255.0, color.green()/255.0, color.blue()/255.0)
        lst = self.contour.getReplyList()
        for contour in lst:
            contour.setActualLineColor(color.red()/255.0, color.green()/255.0, color.blue()/255.0)
        self.actualLineColorFrame.setStyleSheet(
              "background-color : rgb(" + str(color.red()) + ","
              + str(color.green()) + "," + str(color.blue())
              + ");" )

    
    def slotTransversalSizeChanged(self, size):
        self.contour.setTransversalSize(size)
        lst = self.contour.getReplyList()
        for contour in lst:
            contour.setTransversalSize(size)
            
    def _getPropertiesFromContour(self):
        lineColor = self.contour.getLineColor()
        self.lineColorFrame.setStyleSheet(
              "background-color : rgb(" +  str(lineColor[0]*255)+ ","
              + str(lineColor[1]*255) + "," +  str(lineColor[2]*255)
              + ");" )

        actualLineColor = self.contour.getActualLineColor()
        self.actualLineColorFrame.setStyleSheet(
              "background-color : rgb(" +  str(actualLineColor[0]*255)+ ","
              + str(actualLineColor[1]*255) + "," +  str(actualLineColor[2]*255)
              + ");" )
        
        transversalSize = self.contour.getTransversalSize()
        self.transversalSize.setValue(transversalSize)
        
        self.lock.setChecked(self.contour.getLocked())
        self.visible.setChecked(self.contour.getVisible())

#    def slotSelectButtonByContour(self, obj, evt):
#        try :
#            self.contour = obj
#            self.contourButton = self.contourButtons[self.contour]
#        except:
#            lst = obj.getReplyList()
#            for contour in lst:
#                try :
#                    self.contour = contour
#                    self.contourButton = self.contourButtons[self.contour]
#                    break
#                except:
#                    pass
#
#        self.contourButton.setChecked(True)
#        self._getPropertiesFromContour()
        
    def switchContourReference(self, oldContour, newContour):
        button = self.contourButtons.pop(oldContour)
        self.contourButtons[newContour] = button
        self.contours[button] = newContour
        if self.contour == newContour :
            self.contour = newContour
            
    def removeCountour(self, contour):
        self.contour = contour
        self.contourButton = self.contourButtons[self.contour]
        self.removeSelectedContour()

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    win = CPRProperties()
    win.show()
    sys.exit(app.exec_())

