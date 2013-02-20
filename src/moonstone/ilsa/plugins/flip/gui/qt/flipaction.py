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

from ......bloodstone.scenes.imageplane import VtkImagePlane

import widget.resources_rc

class FlipAction(QtCore.QObject):

    def __init__(self, ilsa):
        logging.debug("In FlipAction::__init__()")
        super(FlipAction, self).__init__(ilsa.parentWidget())
        self._ilsa = ilsa
        self._iconResolution = "48x48"
        self.createWidgets()
        self.createActions()
        self._action = False
        
        
    def createWidgets(self):
        logging.debug("In FlipAction::createWidgets()") 
        self.actionFlipHorizontal = QtGui.QAction(self.parent())
        self.actionFlipHorizontal.setCheckable(True)
        icon37 = QtGui.QIcon()
        icon37.addPixmap(
            QtGui.QPixmap(":/static/default/icon/{0}/object-flip-horizontal.png".format(self._iconResolution)), 
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionFlipHorizontal.setIcon(icon37)
        self.actionFlipHorizontal.setObjectName("actionFlipHorizontal")
        self.actionFlipHorizontal.setText(
            QtGui.QApplication.translate("MainWindow", "&Flip Horizontal", None, 
                                         QtGui.QApplication.UnicodeUTF8))
        
        self.parent().menuTools.addAction(self.actionFlipHorizontal)
        self.parent().toolBarTools.addAction(self.actionFlipHorizontal)
        
        self.actionFlipVertical = QtGui.QAction(self.parent())
        self.actionFlipVertical.setCheckable(True)
        icon37 = QtGui.QIcon()
        icon37.addPixmap(
            QtGui.QPixmap(":/static/default/icon/{0}/object-flip-vertical.png".format(self._iconResolution)), 
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionFlipVertical.setIcon(icon37)
        self.actionFlipVertical.setObjectName("actionFlipVertical")
        self.actionFlipVertical.setText(
            QtGui.QApplication.translate("MainWindow", "&Flip Vertical", None, 
                                         QtGui.QApplication.UnicodeUTF8))
        
        self.parent().menuTools.addAction(self.actionFlipVertical)
        self.parent().toolBarTools.addAction(self.actionFlipVertical)
        

    def createActions(self):
        logging.debug("In FlipAction::createActions()")
        self.connect(self.actionFlipHorizontal, QtCore.SIGNAL("triggered()"),
                     self.slotActionFlipHorizontal)
        self.connect(self.actionFlipVertical, QtCore.SIGNAL("triggered()"),
                     self.slotActionFlipVertical)
        
    def slotActionFlipHorizontal(self):
        logging.debug("In FlipAction::slotActionFlipHorizontal()")
        self._action = False
        self._observers = {
            "LeftButtonPressEvent": self.ButtonCallbackFlipHorizontal,
            "LeftButtonReleaseEvent": self.ButtonCallbackFlipHorizontal,
            "MouseMove": self.MouseMoveCallbackFlipHorizontal
        }
        scenes = self._ilsa.scenes()
        if not self.actionFlipHorizontal.isChecked():
            for scene, observer in self.leftButtonPressEvents.items():
                scene.removeObserver(observer)
            for scene, observer in self.leftButtonReleaseEvents.items():
                scene.removeObserver(observer)
            return 
        self._ilsa.desactivateOthers("flip")
        if self.actionFlipVertical.isChecked():
            self.actionFlipVertical.setChecked(False)
            self.slotActionFlipVertical()
            
        self.leftButtonPressEvents = {}
        self.leftButtonReleaseEvents = {}
        for scene in scenes:
            if isinstance(scene, VtkImagePlane):
                self.leftButtonPressEvents[scene] = scene.addObserver("LeftButtonPressEvent", 
                    lambda o, e, s=scene: self.ButtonCallbackFlipHorizontal(o, e, s))
                self.leftButtonReleaseEvents[scene] = scene.addObserver("LeftButtonReleaseEvent", 
                    lambda o, e, s=scene: self.ButtonCallbackFlipHorizontal(o, e, s))
            
    def ButtonCallbackFlipHorizontal(self, obj, event, scene):
        logging.debug("In FlipAction::ButtonCallbackFlipHorizontal()")
        if event == "LeftButtonPressEvent":
            self._action = True
            scene.flipHorizontal()
            obj.OnLeftButtonUp()
        else:
            self._action = False
            obj.OnRightButtonUp()

    def MouseMoveCallbackFlipHorizontal(self, obj, event, scene):
        logging.debug("In FlipAction::MouseMoveCallbackFlipHorizontal()")
        (lastX, lastY) = scene.interactor.GetLastEventPosition()
        (mouseX, mouseY) = scene.interactor.GetEventPosition()

        if self._action:
            deltaY = mouseY - lastY
            obj.OnRightButtonDown()
            scene.render()
        else:
            obj.OnRightButtonUp()
            
    def slotActionFlipVertical(self):
        logging.debug("In FlipAction::slotActionFlipVertical()")
        self._action = False
        self._observers = {
            "LeftButtonPressEvent": self.ButtonCallbackFlipVertical,
            "LeftButtonReleaseEvent": self.ButtonCallbackFlipVertical,
            "MouseMove": self.MouseMoveCallbackFlipVertical
        }
        scenes = self._ilsa.scenes()
        if not self.actionFlipVertical.isChecked():
            for scene, observer in self.leftButtonPressEvents.items():
                scene.removeObserver(observer)
            for scene, observer in self.leftButtonReleaseEvents.items():
                scene.removeObserver(observer)
            return 
        self._ilsa.desactivateOthers("flip")
        if self.actionFlipHorizontal.isChecked():
            self.actionFlipHorizontal.setChecked(False)
            self.slotActionFlipHorizontal()
        self.leftButtonPressEvents = {}
        self.leftButtonReleaseEvents = {}
        for scene in scenes:
            if isinstance(scene, VtkImagePlane):
                self.leftButtonPressEvents[scene] = scene.addObserver("LeftButtonPressEvent", 
                    lambda o, e, s=scene: self.ButtonCallbackFlipVertical(o, e, s))
                self.leftButtonReleaseEvents[scene] = scene.addObserver("LeftButtonReleaseEvent", 
                    lambda o, e, s=scene: self.ButtonCallbackFlipVertical(o, e, s))
            
    def ButtonCallbackFlipVertical(self, obj, event, scene):
        logging.debug("In FlipAction::ButtonCallbackFlipVertical()")
        if event == "LeftButtonPressEvent":
            self._action = True
            scene.flipVertical()
            obj.OnLeftButtonUp()
        else:
            self._action = False
            obj.OnRightButtonUp()

    def MouseMoveCallbackFlipVertical(self, obj, event, scene):
        logging.debug("In FlipAction::MouseMoveCallbackFlipVertical()")
        (lastX, lastY) = scene.interactor.GetLastEventPosition()
        (mouseX, mouseY) = scene.interactor.GetEventPosition()

        if self._action:
            deltaY = mouseY - lastY
            obj.OnRightButtonDown()
            scene.render()
        else:
            obj.OnRightButtonUp()
    
    
    def uncheck(self, actionType):
        if self.actionFlipHorizontal.isChecked():
            self.actionFlipHorizontal.setChecked(False)
            self.slotActionFlipHorizontal()
        elif self.actionFlipVertical.isChecked():
            self.actionFlipVertical.setChecked(False)
            self.slotActionFlipVertical()


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    win = FlipAction()
    win.show()
    sys.exit(app.exec_())