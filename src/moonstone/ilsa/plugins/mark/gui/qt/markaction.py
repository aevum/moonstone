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
from PySide.QtGui import QColor

import widget.resources_rc
from markproperties import MarkProperties
from ...contour import Contour
from ...multislicecontour import MultiSliceContour
from ......bloodstone.scenes.multisliceimageplane import VtkMultiSliceImagePlane

class MarkAction(QtCore.QObject):

    def __init__(self, ilsa):
        logging.debug("In MarkAction::__init__()")
        super(MarkAction, self).__init__(ilsa.parentWidget())
        self._ilsa = ilsa
        self.createWidgets()
        self.createActions()

    def createWidgets(self):
        logging.debug("In MarkAction::createWidgets()")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(
            ":/static/default/icon/48x48/curve.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionMark = QtGui.QAction(self.parent())
        self.actionMark.setCheckable(True)
        self.actionMark.setIcon(icon)
        self.actionMark.setObjectName("actionMark")
        self.actionMark.setText(
            QtGui.QApplication.translate("MarkAction", "&Mark",
                                         None, QtGui.QApplication.UnicodeUTF8))

        self.parent().menuTools.addAction(self.actionMark)
        self.parent().toolBarTools.addAction(self.actionMark)

        parentProperties = self.parent().scrollAreaWidgetContents
        self.propertiesAction = MarkProperties(parentProperties)
        self.propertiesAction.hide()
    
    def uncheck(self, actionType):
        if self.actionMark.isChecked():
            self.actionMark.setChecked(False)
            self.slotActionMark()

    def createActions(self):
        logging.debug("In MarkAction::createActions()")
        self.connect(self.actionMark, QtCore.SIGNAL("triggered()"),
                     self.slotActionMark)
        self.propertiesAction.connect(self.propertiesAction.newMarkButton,
                                QtCore.SIGNAL("clicked ( bool)"),
                                self.slotNewMark)
        self.propertiesAction.connect(self.propertiesAction.deleteMarkButton,
                                QtCore.SIGNAL("clicked ( bool)"),
                                self.slotDeleteMark)

    def slotActionMark(self):
        logging.debug("In MarkAction::slotActionMark()")
        scenes = self._ilsa.scenes()
        if not self.actionMark.isChecked():
            if self.propertiesAction.contour and not self.propertiesAction.contour.started:
                self.propertiesAction.removeSelectedContour()
                
            self.propertiesAction.hide()
            self.parent().toolProperties.setVisible(False)
            self.propertiesAction.lockAll()
            return
        self._ilsa.desactivateOthers("mark")
        self.parent().toolProperties.setVisible(True)
        self.propertiesAction.show()
        self.parent().scrollAreaWidgetContents.resize(self.propertiesAction.size())
            
        if self.propertiesAction.getContour():
            self.propertiesAction.unlockCurrent()
            return

        replyList = []

        for scene in scenes:
            if isinstance(scene, VtkMultiSliceImagePlane):
                contour = MultiSliceContour(scene)
            else:
                contour = Contour(scene) 
            
            replyList.append(contour)

        self.propertiesAction.addContour(replyList[0])

        for i,scene in enumerate(scenes):
            a = replyList[:]
            b = a.pop(i)
            b.replyList = a


    def slotDeleteMark(self, checked):
        logging.debug("In MarkAction::slotDeleteMark()")
        self.propertiesAction.removeSelectedContour()

    def slotNewMark(self, checked):
        logging.debug("In MarkAction::slotNewMark()")
        for contour in self.propertiesAction.contours.values():
            if contour.contourWidget.GetWidgetState() != 2:
                return
        scenes = self._ilsa.scenes()
        replyList = []

        for scene in scenes:
            if isinstance(scene, VtkMultiSliceImagePlane):
                contour = MultiSliceContour(scene)
            else:
                contour = Contour(scene) 
            replyList.append(contour)

        self.propertiesAction.addContour(replyList[0])

        for i,scene in enumerate(scenes):
            a = replyList[:]
            b = a.pop(i)
            b.replyList = a
            
    def save(self):
        logging.debug("In MarkAction::save()")
        contours = self.propertiesAction.contours.values()
        yamlContours = []
        for contour in contours:
            yamlContours.append(contour.save())
        yaml = {"contours" : yamlContours}
        return yaml
    
    def restore(self, value):
        logging.debug("In MarkAction::restore()")
        contours = value["contours"]
        if contours:
            for contour in contours:
                self.loadContour(contour)
                    
    def loadContour(self, contourData):
        logging.debug("In MarkAction::loadContour()")
        scenes = self._ilsa.scenes()
        replyList = []

        for scene in scenes:
            contour = Contour(scene)
            replyList.append(contour)

        self.propertiesAction.addContour(replyList[0])

        for i,scene in enumerate(scenes):
            a = replyList[:]
            b = a.pop(i)
            b.replyList = a

        contour.loadPoints(contourData["points"])
            
        lc = contourData["lineColor"]
        lineColor = QColor.fromRgbF(lc[0], lc[1], lc[2])
        self.propertiesAction.changeLineColor(lineColor)
        self.propertiesAction.slotActionVisible(contourData["visible"])
        self.propertiesAction.slotActionLock(contourData["locked"])
        self.propertiesAction.lock.setChecked(contourData["locked"])
        self.propertiesAction.slotThicknessChanged(contourData["radius"])
    
    def addScene(self, scene):
        logging.debug("In MarkAction::addScene()")
        contours = self.propertiesAction.contours.values()
        for contour in contours:
            contour.addScene(scene)
            
    def removeScene(self, scene):
        logging.debug("In MarkAction::removeScene()")
        contours = self.propertiesAction.contours.values()
        for contour in contours:
            if contour.scene == scene:
                toRemove = contour
                if contour.replyList:
                    contour = contour.replyList[0]
                    self.propertiesAction.switchContourReference(toRemove, contour)
                else:
                    self.propertiesAction.removeCountour(contour)
                    continue
                
            else:
                for reply in contour.replyList:
                    if reply.scene == scene:
                        toRemove = reply
                        break
            contour.removeScenePlugin(toRemove)
            #TODO free em ToRemove
            for reply in contour.replyList:
                reply.removeScenePlugin(toRemove)
            toRemove.delete()
                
        
if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    win = MarkProperties()
    win.show()
    sys.exit(app.exec_())