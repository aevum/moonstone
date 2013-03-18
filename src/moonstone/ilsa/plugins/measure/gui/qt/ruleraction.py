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

from rulerproperties import RulerProperties
from ...ruler import Ruler
from ......bloodstone.scenes.imageplane import VtkImagePlane



class RulerAction(QtCore.QObject):

    def __init__(self, ilsa):
        logging.debug("In RulerAction::__init__()")
        super(RulerAction, self).__init__(ilsa.parentWidget())
        self._ilsa = ilsa
        self.createWidgets()
        self.createActions()

    def createWidgets(self):
        logging.debug("In RulerAction::createWidgets()")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(
            ":/static/default/icon/48x48/ruler-diagonal.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.actionRuler = QtGui.QAction(self.parent())
        self.actionRuler.setCheckable(True)
        self.actionRuler.setIcon(icon)
        self.actionRuler.setObjectName("actionRuler")
        self.actionRuler.setText(
            QtGui.QApplication.translate("MainWindow", "&Ruler",
                                         None, QtGui.QApplication.UnicodeUTF8))

        self.parent().menuTools.addAction(self.actionRuler)
        self.parent().toolBarTools.addAction(self.actionRuler)

        parentProperties = self.parent().scrollAreaWidgetContents

        self.propertiesAction = RulerProperties(parentProperties)
        self.propertiesAction.hide()

    def uncheck(self, actionType):
        if self.actionRuler.isChecked() and actionType!=self._ilsa.ACTION_TYPE_MOUSE:
            self.actionRuler.setChecked(False)
            self.slotActionRuler()
            
    def createActions(self):
        logging.debug("In RulerAction::createActions()")
        self.connect(self.actionRuler, QtCore.SIGNAL("triggered()"),
                     self.slotActionRuler)

    def slotActionRuler(self):
        logging.debug("In RulerAction::slotActionRuler()")
        if not self.actionRuler.isChecked():
            self.propertiesAction.hide()
            self.parent().toolProperties.setVisible(False)
            if  self.propertiesAction.ruler:
                if  self.propertiesAction.ruler.rep.GetDistance() == 0:
                    self.slotDeleteRuler(True)
            return
        self._ilsa.desactivateOthers("measure")
        if self.propertiesAction.ruler:
            self.parent().toolProperties.setVisible(True)
            self.propertiesAction.show()
            self.parent().scrollAreaWidgetContents.resize(self.propertiesAction.size())
            return
    
        self.propertiesAction.connect(self.propertiesAction.newRulerButton,
                                QtCore.SIGNAL("clicked ( bool)"),
                                self.slotNewRuler)
        self.propertiesAction.connect(self.propertiesAction.deleteRulerButton,
                                QtCore.SIGNAL("clicked ( bool)"),
                                self.slotDeleteRuler)

        self.parent().toolProperties.setVisible(True)
        self.propertiesAction.show()
        self.parent().scrollAreaWidgetContents.resize(self.propertiesAction.size())
        self.newRuler()

    def newRuler(self):
        logging.debug("In RulerAction::newRuler()")
        self.ruler = Ruler()
        self.propertiesAction.addRuler(self.ruler)
        self.started = False
        self.scenesMap = {}
        self.observers = {}
        for scene in self._ilsa.scenes():
            if isinstance(scene, VtkImagePlane):
                self.observers[scene] = scene.addObserver("MouseMoveEvent", self.activateRuler)
                self.scenesMap[scene.interactor.GetInteractorStyle()] = scene
    
    def slotNewRuler(self, checked):
        logging.debug("In RulerAction::slotNewRuler()")
        if not self.propertiesAction.ruler or self.propertiesAction.ruler.representation.GetDistance() != 0:
            self.newRuler()

    def slotDeleteRuler(self, checked):
        logging.debug("In RulerAction::slotDeleteRuler()")
        self.propertiesAction.removeSelectedRuler()
        for scene, observer in self.observers.items():
            scene.removeObserver(observer)
        self.ruler = None

    def activateRuler(self, obj, evt):
        logging.debug("In RulerAction::activateRuler()")
        if not self.ruler.started:
            scene = self.scenesMap[obj]
            self.ruler.scene = scene
            self.ruler.activate()
        else:
            for scene, observer in self.observers.items():
                scene.removeObserver(observer)
    
    def removeScene(self, scene):
        logging.debug("In RulerAction::removeScene()")
        self.propertiesAction.removeScene(scene)