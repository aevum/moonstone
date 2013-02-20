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
import vtk
from PySide import QtCore, QtGui

import widget.resources_rc
from ......bloodstone.scenes.imageplane import VtkImagePlane


class ZoomAction(QtCore.QObject):

    def __init__(self, ilsa):
        logging.debug("In ZoomAction::__init__()")
        super(ZoomAction, self).__init__(ilsa.parentWidget())
        self._ilsa = ilsa
        self.createWidgets()
        self.createActions()
        
        self._action = False
        
    def createWidgets(self):
        logging.debug("In ZoomAction::createWidgets()")
        
        icon23 = QtGui.QIcon()
        icon23.addPixmap(
            QtGui.QPixmap(":/static/default/icon/48x48/zoom-in.png"), 
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionZoomIn = QtGui.QAction(self.parent())
        self.actionZoomIn.setCheckable(True)
        self.actionZoomIn.setIcon(icon23)
        self.actionZoomIn.setObjectName("actionZoomIn")
        self.actionZoomIn.setText(
            QtGui.QApplication.translate("MainWindow", "Zoom &In", None, 
                                         QtGui.QApplication.UnicodeUTF8))
        self.actionZoomIn.setShortcut(
            QtGui.QApplication.translate("MainWindow", "Ctrl++", None, 
                                         QtGui.QApplication.UnicodeUTF8))
        
        self.parent().menuTools.addAction(self.actionZoomIn)
        self.parent().toolBarTools.addAction(self.actionZoomIn)        
    
    def uncheck(self, actionType):
        if self.actionZoomIn.isChecked():
            self.actionZoomIn.setChecked(False)
            self.slotActionZoomIn()

    def createActions(self):
        logging.debug("In ZoomAction::createActions()")
        self.connect(self.actionZoomIn, QtCore.SIGNAL("triggered()"),
                     self.slotActionZoomIn)
        
    def slotActionZoomIn(self):
        logging.debug("In ZoomAction::slotActionZoomIn()")
        self._action = False
        scenes = self._ilsa.scenes()
        if not self.actionZoomIn.isChecked():
            self.removeObservers()                    
            return 
        self._ilsa.desactivateOthers("zoom", self._ilsa.ACTION_TYPE_MOUSE)
        
        
        self._leftButtonPressEvent = {}
        self._leftButtonReleaseEvent = {}
        self._mouseMoveEvent = {}
        
        for scene in scenes:
            if isinstance(scene, VtkImagePlane):
                self._leftButtonPressEvent[scene] = scene.addObserver("LeftButtonPressEvent", 
                                                     self.ButtonZoomInCallback)
                self._leftButtonReleaseEvent[scene] = scene.addObserver("LeftButtonReleaseEvent", 
                                                     self.ButtonZoomInCallback)
                self._mouseMoveEvent[scene] =  scene.addObserver("MouseMoveEvent", 
                    lambda o, e, s=scene: self.MouseMoveZoomInCallback(o, e, s))
                
    def removeObservers(self):
        if self._leftButtonPressEvent:
            for scene, observer in self._leftButtonPressEvent.items():
                scene.removeObserver(observer)
        if self._leftButtonReleaseEvent:
            for scene, observer in self._leftButtonReleaseEvent.items():
                scene.removeObserver(observer)
        if self._mouseMoveEvent:
            for scene, observer in self._mouseMoveEvent.items():
                scene.removeObserver(observer)
        self._leftButtonPressEvent = {}
        self._leftButtonReleaseEvent = {}
        self._mouseMoveEvent = {}
            
            
    def slotActionZoomReset(self):
        logging.debug("In ZoomAction::slotActionZoomReset()")
        self._action = False
        scenes = self._ilsa.scenes()
        if not self.actionZoomReset.isChecked():
            self.zoomResetProperties.hide()
            self.parent().toolProperties.setVisible(False)
            for scene in scenes:
                if scene.VTK_SCENE == "VOLUME":
                    #scene.vtkInteractorStyle = vtk.vtkInteractorStyleTrackballCamera()
                    pass
                elif scene.VTK_SCENE == "SLICE":
                    scene.vtkInteractorStyle = vtk.vtkInteractorStyleImage()
            return 
        #self.parent().toolProperties.setVisible(True)
        #self.zoomResetProperties.show()
        for scene in scenes:
            if scene.VTK_SCENE == "VOLUME":
                #scene.vtkInteractorStyle = vtk.vtkInteractorStyleTrackballCamera()
                pass
            elif scene.VTK_SCENE == "SLICE":
                scene.vtkInteractorStyle = vtk.vtkInteractorStyleImage()
                scene.vtkInteractorStyle.AddObserver("LeftButtonPressEvent", 
                    lambda o, e, s=scene: self.ButtonZoomResetCallback(o, e, s))
                scene.vtkInteractorStyle.AddObserver("LeftButtonReleaseEvent", 
                    lambda o, e, s=scene: self.ButtonZoomResetCallback(o, e, s))
            
    def ButtonZoomInCallback(self, obj, event):
        logging.debug("In ZoomAction::ButtonCallback()")
        if event == "LeftButtonPressEvent":
            self._action = True
            obj.StartDolly()
        else:
            self._action = False
            obj.OnRightButtonUp()

    def MouseMoveZoomInCallback(self, obj, event, scene):
        logging.debug("In ZoomAction::MouseMoveCallback()")
        (lastX, lastY) = scene.interactor.GetLastEventPosition()
        (mouseX, mouseY) = scene.interactor.GetEventPosition()

        if self._action:
            scene.interactorStyle.Dolly()
            scene.interactorStyle.OnRightButtonDown()
            scene.window.Render()
        else:
            scene.interactorStyle.OnRightButtonUp()  
                        
    def MouseMoveZoomRegionCallback(self, obj, event, scene):
        logging.debug("In ZoomAction::MouseMoveCallback()")
        if self._bbox:
            xy = scene.interactor.GetEventPosition()
            x, y = xy
            self.pts.SetPoint(1, x, self._y, 0)
            self.pts.SetPoint(2, x, y, 0)
            self.pts.SetPoint(3, self._x, y, 0)
            scene.window.Render()