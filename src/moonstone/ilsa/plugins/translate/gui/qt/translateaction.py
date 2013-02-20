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
from ......bloodstone.scenes.imageplane import VtkImagePlane


class TranslateAction(QtCore.QObject):

    def __init__(self, ilsa):
        logging.debug("In TranslateAction::__init__()")
        super(TranslateAction, self).__init__(ilsa.parentWidget())
        self._ilsa = ilsa
        self.createWidgets()
        self.createActions()
        
        self._action = False
        
        
        self.leftButtonPressEvent = None
        self.leftButtonReleaseEvent = None
        self.mouseMoveEvent = None
        
        
    def createWidgets(self):
        logging.debug("In TranslateAction::createWidgets()") 
        self.actionTranslate = QtGui.QAction(self.parent())
        self.actionTranslate.setCheckable(True)
        icon37 = QtGui.QIcon()
        icon37.addPixmap(QtGui.QPixmap(":/static/default/icon/48x48/transform.png"), 
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionTranslate.setIcon(icon37)
        self.actionTranslate.setObjectName("actionTranslate")
        self.actionTranslate.setText(
            QtGui.QApplication.translate("MainWindow", "&Translate", None, 
                                         QtGui.QApplication.UnicodeUTF8))
        
        self.parent().menuTools.addAction(self.actionTranslate)
        self.parent().toolBarTools.addAction(self.actionTranslate)
        

    def uncheck(self, actionType):
        if self.actionTranslate.isChecked():
            self.actionTranslate.setChecked(False)
            self.slotActionTranslate()
            
    def createActions(self):
        logging.debug("In TranslateAction::createActions()")
        self.connect(self.actionTranslate, QtCore.SIGNAL("triggered()"),
                     self.slotActionTranslate)
        
    def slotActionTranslate(self):
        logging.debug("In TranslateAction::slotActionTranslate()")
        self._action = False
       
        scenes = self._ilsa.scenes()
        if not self.actionTranslate.isChecked():
            self.removeObservers()
            return 
        self._ilsa.desactivateOthers("translate")
        self.leftButtonPressEvent = {}
        self.leftButtonReleaseEvent = {}
        self.mouseMoveEvent = {} 
        for scene in scenes:
            if isinstance(scene, VtkImagePlane):
                self.leftButtonPressEvent[scene] = scene.addObserver("LeftButtonPressEvent", 
                                                     self.ButtonCallback)
                self.leftButtonReleaseEvent[scene] = scene.addObserver("LeftButtonReleaseEvent", 
                                                     self.ButtonCallback)
                self.mouseMoveEvent[scene] = scene.addObserver("MouseMoveEvent", 
                    lambda o, e, s=scene: self.MouseMoveCallback(o, e, s))
                
    def removeObservers(self):
        if self.leftButtonPressEvent:
            for scene, observer in self.leftButtonPressEvent.items():
                scene.removeObserver(observer)
        if self.leftButtonReleaseEvent:
            for scene, observer in self.leftButtonReleaseEvent.items():
                scene.removeObserver(observer)
        if self.mouseMoveEvent:
            for scene, observer in self.mouseMoveEvent.items():
                scene.removeObserver(observer)
        self.leftButtonPressEvent = {}
        self.leftButtonReleaseEvent = {}
        self.mouseMoveEvent = {} 
            
    def ButtonCallback(self, obj, event):
        logging.debug("In TranslateAction::ButtonCallback()")
        if event == "LeftButtonPressEvent":
            self._action = True
#            obj.StartPan()
        else:
            self._action = False
            obj.OnRightButtonUp()

    def MouseMoveCallback(self, obj, event, scene):
        logging.debug("In TranslateAction::MouseMoveCallback()")
        (lastX, lastY) = scene.interactor.GetLastEventPosition()
        (mouseX, mouseY) = scene.interactor.GetEventPosition()

        if self._action:
            obj.Pan()
            obj.OnRightButtonDown()
            scene.window.Render()
        else:
            obj.OnRightButtonUp()