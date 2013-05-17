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

from cprproperties import CPRProperties
from ...cprcontour import CPRContour


class CPRAction(QtCore.QObject):

    def __init__(self, ilsa):
        logging.debug("In CPRAction::__init__()")
        super(CPRAction, self).__init__(ilsa.parentWidget())
        self._ilsa = ilsa
        self.createWidgets()
        self.createActions()

    def createWidgets(self):
        logging.debug("In CPRAction::createWidgets()")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(
            ":/static/default/icon/48x48/panoramic-grey.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCPR = QtGui.QAction(self.parent())
        self.actionCPR.setCheckable(True)
        self.actionCPR.setIcon(icon)
        self.actionCPR.setObjectName("actionCPR")
        self.actionCPR.setText(
            QtGui.QApplication.translate("MainWindow", "&CPR",
                                         None, QtGui.QApplication.UnicodeUTF8))

        self.parent().menuTools.addAction(self.actionCPR)
        self.parent().toolBarTools.addAction(self.actionCPR)

        parentProperties = self.parent().scrollAreaWidgetContents
        self.propertiesAction = CPRProperties(parentProperties)
        self.propertiesAction.hide()
    
    def uncheck(self, actionType):
        if self.actionCPR.isChecked():
            self.actionCPR.setChecked(False)
            self.slotActionCPR()

    def createActions(self):
        logging.debug("In CPRAction::createActions()")
        self.connect(self.actionCPR, QtCore.SIGNAL("triggered()"),
                     self.slotActionCPR)
        self.propertiesAction.connect(self.propertiesAction.newCPRButton,
                                QtCore.SIGNAL("clicked ( bool)"),
                                self.slotNewCPR)
        self.propertiesAction.connect(self.propertiesAction.deleteCPRButton,
                                QtCore.SIGNAL("clicked ( bool)"),
                                self.slotDeleteCPR)

    def slotActionCPR(self):
        logging.debug("In CPRAction::slotActionCPR()")
        if not self.actionCPR.isChecked():
            self.propertiesAction.hide()
            self.parent().toolProperties.setVisible(False)
            self.propertiesAction.lockAll()
            self.cprClosed()
            return
        self._ilsa.desactivateOthers("cpr")
        self.parent().toolProperties.setVisible(True)
        self.propertiesAction.show()
        self.parent().scrollAreaWidgetContents.resize(self.propertiesAction.size())
            
        if self.propertiesAction.getContour():
            self.propertiesAction.unlockCurrent()
            return

        self.slotNewCPR(True)

    def slotDeleteCPR(self, checked):
        logging.debug("In CPRAction::slotDeleteCPR()")
        self.propertiesAction.removeSelectedContour()

    def slotNewCPR(self, checked):
        logging.debug("In CPRAction::slotNewCPR()")
        for contour in self.propertiesAction.contours.values():
            if not contour.getClosed():
                return
        scenes = self._ilsa.scenes()
        controller = self._ilsa.windowArea().cameraController
        self._oldActions = [controller.getActiveAction(controller.BUTTON_LEFT),
                            controller.getActiveAction(controller.BUTTON_RIGHT),
                            controller.getActiveAction(controller.BUTTON_MIDDLE),
                            controller.getActiveAction(controller.BUTTON_SCROLL)]
        controller.selectAction(controller.ACTION_NONE, controller.BUTTON_LEFT)
        controller.selectAction(controller.ACTION_NONE, controller.BUTTON_RIGHT)
        controller.selectAction(controller.ACTION_TRANSLATE, controller.BUTTON_MIDDLE)
        controller.selectAction(controller.ACTION_ZOOM, controller.BUTTON_SCROLL)
        controller.lockButtons(True)
        contour = CPRContour(scenes, self._ilsa, self.cprClosed)
        self.propertiesAction.addContour(contour)

    def cprClosed(self):
        if self._oldActions:
            controller = self._ilsa.windowArea().cameraController
            controller.selectAction(self._oldActions[0], controller.BUTTON_LEFT)
            controller.selectAction(self._oldActions[1], controller.BUTTON_RIGHT)
            controller.selectAction(self._oldActions[2], controller.BUTTON_MIDDLE)
            controller.selectAction(self._oldActions[3], controller.BUTTON_SCROLL)
            controller.lockButtons(False)
            self._oldActions = []

    def save(self):
        logging.debug("In CPRAction::save()")
        contours = self.propertiesAction.contours.values()
        yamlContours = []
        for contour in contours:
            if contour.getClosed():
                yamlContours.append(contour.save())
        yaml = {"contours": yamlContours}
        return yaml
    
    def restore(self, value):
        logging.debug("In CPRAction::restore()")
        contours = value["contours"]
        if contours:
            for contour in contours:
                self.loadContour(contour)
        self._oldActions=[]
        self.slotActionCPR()
                    
    def loadContour(self, contourData):
        logging.debug("In CPRAction::loadContour()")
        scenes = self._ilsa.scenes()
        contour = CPRContour(scenes, self._ilsa, self.cprClosed)
        for scene in scenes:
            if contourData["sceneId"] == scene.id:
                contour.scene = scene
            elif contourData["panoramicSceneId"] == scene.id:
                contour.setPanoramicPlane(scene.parent)
            elif contourData["transversalSceneId"] == scene.id:
                contour.setTransversalPlane(scene.parent)
        self.propertiesAction.addContour(contour)
        
        contour.loadPoints(contourData["points"])
            
        lc = contourData["lineColor"]
        alc = contourData["actualLineColor"]
        ts = contourData["transversalSize"]
        lineColor = QColor.fromRgbF(lc[0], lc[1], lc[2])
        actualLineColor = QColor.fromRgbF(alc[0], alc[1], alc[2])
        self.propertiesAction.changeLineColor(lineColor)
        self.propertiesAction.changeActualLineColor(actualLineColor)
        contour.setTransversalSize(ts)
        self.propertiesAction.slotActionVisible(contourData["visible"])
        self.propertiesAction.slotActionLock(contourData["locked"])
        self.propertiesAction.lock.setChecked(contourData["locked"])

    def addScene(self, scene):
        logging.debug("In CPRAction::addScene()")
        contours = self.propertiesAction.contours.values()
        for contour in contours:
            contour.addScene(scene)
            
    def removeScene(self, contour):
        logging.debug("In CPRAction::removeScene()")
        return