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

import widget.resources_rc
from protractorproperties import ProtractorProperties
from ...protractor import Protractor
from ......bloodstone.scenes.imageplane import VtkImagePlane




class ProtractorAction(QtCore.QObject):

    def __init__(self, ilsa):
        logging.debug("In ProtractorAction::__init__()")
        super(ProtractorAction, self).__init__(ilsa.parentWidget())
        self._ilsa = ilsa
        self.protractor = None
        self._mouseEvent = 0
        self.createWidgets()
        self.createActions()
        self.propertiesAction.connect(self.propertiesAction.newProtractorButton,
                                QtCore.SIGNAL("clicked ( bool)"),
                                self.slotNewProtractor)
        self.propertiesAction.connect(self.propertiesAction.deleteProtractorButton,
                                QtCore.SIGNAL("clicked ( bool)"),
                                self.slotDeleteProtractor)

    def createWidgets(self):
        logging.debug("In ProtractorAction::createWidgets()")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(
            ":/static/default/icon/48x48/transferidor.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.actionProtractor = QtGui.QAction(self.parent())
        self.actionProtractor.setCheckable(True)
        self.actionProtractor.setIcon(icon)
        self.actionProtractor.setObjectName("actionProtractor")
        self.actionProtractor.setText(
            QtGui.QApplication.translate("ProtractorAction", "&Protractor",
                                         None, QtGui.QApplication.UnicodeUTF8))

        self.parent().menuTools.addAction(self.actionProtractor)
        self.parent().toolBarTools.addAction(self.actionProtractor)

        parentProperties = self.parent().scrollAreaWidgetContents

        self.propertiesAction = ProtractorProperties(parentProperties)
        self.propertiesAction.hide()
    
    def uncheck(self, actionType):
        if self.actionProtractor.isChecked():
            self.actionProtractor.setChecked(False)
            self.slotActionProtractor()

    def createActions(self):
        logging.debug("In ProtractorAction::createActions()")
        self.connect(self.actionProtractor, QtCore.SIGNAL("triggered()"),
                     self.slotActionProtractor)

    def slotActionProtractor(self):
        logging.debug("In ProtractorAction::slotActionProtractor()")
        if not self.actionProtractor.isChecked():
            self.propertiesAction.hide()
            self.parent().toolProperties.setVisible(False)
            if self.protractor:
                if self.protractor.status() != 3: 
                    self.desactivateProtactor()
            return
        self._ilsa.desactivateOthers("angle")
        self.parent().toolProperties.setVisible(True)
        self.propertiesAction.show()    
        self.parent().scrollAreaWidgetContents.resize(self.propertiesAction.size()) 
        if not self.protractor:   
            self.newProtactor()
            
    def slotNewProtractor(self, checked):
        if self.protractor:
            if self.protractor.status() != 3:
                return
        self.newProtactor()

    def newProtactor(self):
        self.protractor = Protractor()
        self.propertiesAction.addProtractor(self.protractor)
        self.scenesMap = {}
        self._mouseEvents = {}
        for scene in self._ilsa.scenes():
            if isinstance(scene, VtkImagePlane):
                self._mouseEvents[scene] = scene.addObserver("MouseMoveEvent", self.activateProtractor)
                self.scenesMap[scene.interactorStyle] = scene

    def slotDeleteProtractor(self, checked):
        self.protractor.desactivate()
        if self._mouseEvents:
            for scene in self._ilsa.scenes():
                if isinstance(scene, VtkImagePlane):
                    scene.removeObserver(self._mouseEvents[scene])
            self._mouseEvents = {}
        self.protractor = self.propertiesAction.removeSelectedProtractor()
        

    def desactivateProtactor(self):
        self.protractor.desactivate()
        if self._mouseEvents:
            for scene, observer in self._mouseEvents.items():
                scene.removeObserver(observer)
        self.slotDeleteProtractor(True)
        
    def activateProtractor(self, obj, evt):
        if not self.protractor.started():
            scene = self.scenesMap[obj]
            self.protractor.setScene(scene)
        else:
            for scene in self._ilsa.scenes():
                if isinstance(scene, VtkImagePlane):
                    scene.removeObserver(self._mouseEvents[scene])
            self._mouseEvents = {}
    
    def removeScene(self, scene):
        self.propertiesAction.removeScene(scene)        

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    win = ProtractorProperties()
    win.show()
    sys.exit(app.exec_())