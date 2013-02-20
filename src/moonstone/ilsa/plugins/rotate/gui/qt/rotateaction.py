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


class RotateAction(QtCore.QObject):

    def __init__(self, ilsa):
        logging.debug("In RotateAction::__init__()")
        super(RotateAction, self).__init__(ilsa.parentWidget())
        self._ilsa = ilsa
        self.createWidgets()
        self.createActions()
        self._action = False
        
        
    def createWidgets(self):
        logging.debug("In RotateAction::createWidgets()") 
        self.actionRotate = QtGui.QAction(self.parent())
        self.actionRotate.setCheckable(True)
        icon41 = QtGui.QIcon()
        icon41.addPixmap(
            QtGui.QPixmap(":/static/default/icon/48x48/transform-rotate.png"), 
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRotate.setIcon(icon41)
        self.actionRotate.setObjectName("actionRotate")
        self.actionRotate.setText(
            QtGui.QApplication.translate("MainWindow", "&Rotate", 
                                         None, QtGui.QApplication.UnicodeUTF8))
        
        self.parent().menuTools.addAction(self.actionRotate)
        self.parent().toolBarTools.addAction(self.actionRotate)
        
        
    def uncheck(self, actionType):
        if self.actionRotate.isChecked():
            self.actionRotate.setChecked(False)
            self.slotActionRotate()

    def createActions(self):
        logging.debug("In TranslateAction::createActions()")
        self.connect(self.actionRotate, QtCore.SIGNAL("triggered()"),
                     self.slotActionRotate)
        
    def slotActionRotate(self):
        logging.debug("In TranslateAction::slotActionTranslate()")
        self._action = False
        self._observers = {
            "LeftButtonPressEvent": self.ButtonCallback,
            "LeftButtonReleaseEvent": self.ButtonCallback,
            "MouseMove": self.MouseMoveCallback
        }
        scenes = self._ilsa.scenes()
        if not self.actionRotate.isChecked():
            for scene, observer in self._mouseMoveEvents.items():
                scene.removeObserver(observer)
            for scene, observer in self._leftButtonPressEvents.items():
                scene.removeObserver(observer)
            for scene, observer in self._leftButtonReleaseEvents.items():
                scene.removeObserver(observer)
            return 
        self._ilsa.desactivateOthers("rotate")
        self._leftButtonPressEvents = {}
        self._leftButtonReleaseEvents = {}
        self._mouseMoveEvents = {}
        for scene in scenes:
            if isinstance(scene, VtkImagePlane):
                self._leftButtonPressEvents[scene] = scene.addObserver("LeftButtonPressEvent", 
                                                     self.ButtonCallback)
                self._leftButtonReleaseEvents[scene] = scene.addObserver("LeftButtonReleaseEvent", 
                                                     self.ButtonCallback)
                self._mouseMoveEvents[scene] = scene.addObserver("MouseMoveEvent", 
                    lambda o, e, s=scene: self.MouseMoveCallback(o, e, s))
            
    def ButtonCallback(self, obj, event):
        logging.debug("In TranslateAction::ButtonCallback()")
        if event == "LeftButtonPressEvent":
            self._action = True
#            obj.StartSpin() Funciona sem :D
        else:
            self._action = False
            obj.OnRightButtonUp()

    def MouseMoveCallback(self, obj, event, vtkScene):
        logging.debug("In TranslateAction::MouseMoveCallback()")
        (lastX, lastY) = vtkScene.interactor.GetLastEventPosition()
        (mouseX, mouseY) = vtkScene.interactor.GetEventPosition()
        if self._action:
            deltaY = mouseY - lastY
            obj.Spin()
            obj.OnRightButtonDown()
            vtkScene.window.Render()
        else:
            obj.OnRightButtonUp()
    

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    win = RotateAction()
    win.show()
    sys.exit(app.exec_())