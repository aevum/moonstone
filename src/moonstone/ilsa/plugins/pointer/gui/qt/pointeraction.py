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

import logging

import vtk
from PySide import QtCore, QtGui

import widget.resources_rc
from ......bloodstone.scenes.sliceimageplane import VtkSliceImagePlane
from ......bloodstone.scenes.imagevolume import VtkImageVolume

class PointerAction(QtCore.QObject):

    def __init__(self, ilsa):
        logging.debug("In PointerAction::__init__()")
        super(PointerAction, self).__init__(ilsa.parentWidget())
        self._ilsa = ilsa
        self.createWidgets()
        self.createActions()
        
        self._action1 = 0
        
#        self.actors = []
        
        self.leftButtonPressEvent = None
        self.leftButtonReleaseEvent = None
        self.rightButtonReleaseEvent = None 
        self.rightButtonPressEvent = None 
        self.mouseMoveEvent = None 
        
        
        
    def createWidgets(self):
        logging.debug("In PointerAction::createWidgets()") 
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(
            ":/static/default/icon/48x48/snap-orthogonal.png"), 
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPointer = QtGui.QAction(self.parent())
        self.actionPointer.setCheckable(True)
        self.actionPointer.setIcon(icon)
        self.actionPointer.setObjectName("actionPointer")
        self.actionPointer.setText(
            QtGui.QApplication.translate("MainWindow", "&Pointer", 
                                         None, QtGui.QApplication.UnicodeUTF8))
        
        self.parent().menuTools.addAction(self.actionPointer)
        self.parent().toolBarTools.addAction(self.actionPointer)
        

    def uncheck(self, actionType):
        if self.actionPointer.isChecked():
            self.actionPointer.setChecked(False)
            self.slotActionPointer()
            
    def createActions(self):
        logging.debug("In PointerAction::createActions()")
        self.connect(self.actionPointer, QtCore.SIGNAL("triggered()"),
                     self.slotActionPointer)
        
    def slotActionPointer(self):
        logging.debug("In PointerAction::slotActionPointer()")
        self._action = False
        scenes = self._ilsa.scenes()
        planes = self._ilsa.planes()
        if not self.actionPointer.isChecked():
            self.removeObservers()
                    
            return 
        self._ilsa.desactivateOthers("pointer", True)
                
        self.leftButtonPressEvent = {}
        self.leftButtonReleaseEvent = {}
        self.rightButtonReleaseEvent = {} 
        self.rightButtonPressEvent = {} 
        self.mouseMoveEvent = {} 
        for plane in planes:
            if isinstance( plane.scene, VtkImageVolume ):
                continue
                
            scene = plane.scene
                
            self.leftButtonPressEvent[scene] = scene.addObserver("LeftButtonPressEvent", 
                                                 lambda o, e, s=plane: self.ButtonCallback(o, e, s))
            self.leftButtonReleaseEvent[scene] = scene.addObserver("LeftButtonReleaseEvent", 
                                                 lambda o, e, s=plane: self.ButtonCallback(o, e, s))
            self.rightButtonReleaseEvent[scene] = scene.addObserver("RightButtonPressEvent", 
                                                 lambda o, e, s=plane: self.ButtonCallback(o, e, s))
            self.rightButtonPressEvent[scene] = scene.addObserver("RightButtonReleaseEvent", 
                                                lambda o, e, s=plane: self.ButtonCallback(o, e, s))
            self.mouseMoveEvent[scene] = scene.addObserver("MouseMoveEvent", 
                lambda o, e, s=plane: self.MouseMoveCallback(o, e, s))
                
    def removeObservers(self):
        if self.leftButtonPressEvent:
            for scene, observer in self.leftButtonPressEvent.items():
                scene.removeObserver(observer)
        if self.leftButtonReleaseEvent:
            for scene, observer in self.leftButtonReleaseEvent.items():
                scene.removeObserver(observer)
        if self.rightButtonReleaseEvent:
            for scene, observer in self.rightButtonReleaseEvent.items():
                scene.removeObserver(observer)
        if self.rightButtonPressEvent:
            for scene, observer in self.rightButtonPressEvent.items():
                scene.removeObserver(observer)
        if self.mouseMoveEvent:
            for scene, observer in self.mouseMoveEvent.items():
                scene.removeObserver(observer)
        self.leftButtonPressEvent = {}
        self.leftButtonReleaseEvent = {}
        self.rightButtonReleaseEvent = {} 
        self.rightButtonPressEvent = {} 
        self.mouseMoveEvent = {} 
            
    def ButtonCallback(self, obj, event, plane):
        logging.debug("In PointerAction::ButtonCallback()")
        if event == "LeftButtonPressEvent":
            self._action = 1
        elif event == "RightButtonPressEvent":
            self._action = 2
            scenes = self._ilsa.activeScenes()
            for scene in scenes:
                scene.render()
        elif event == "RightButtonReleaseEvent":
            scenes = self._ilsa.activeScenes()
            for scene in scenes:
                scene.render()
            self._action = 2
            self.MouseMoveCallback(obj, event, plane)
            self._action = 0
        else:
            self._action = 0
        self.MouseMoveCallback(obj, event, plane)

    def MouseMoveCallback(self, obj, event, vtkPlane):
        logging.debug("In PointerAction::MouseMoveCallback()")
        scene = vtkPlane.scene
        (lastX, lastY) = scene.interactor.GetLastEventPosition()
        (mouseX, mouseY) = scene.interactor.GetEventPosition()
        if self._action == 1:
            renderer = scene.renderer
            deltaY = mouseY - lastY
            z = vtkPlane.planeSlideValue + deltaY

            #vtkPlane.slotPlaneSlideChanged(z)
            vtkPlane.planeSlide.setValue(z)
            vtkPlane.planeSlide.update()
            scene.render()
        elif self._action == 2:
            renderer = scene.renderer
            scene.picker.Pick(mouseX, mouseY, 0, renderer)
            
            px, py, pz = scene.picker.GetPickPosition()

            Q = [px, py, pz]
            Q = scene.toOriginalView(Q)
           
            planes = self._ilsa.activePlanes()
            for plane in planes:
                if (not isinstance(plane.scene, VtkSliceImagePlane)) or plane.scene == scene:
                    continue
                    
                plane.setSliceToPosition(Q)

            scene.window.Render()
        else:
            scene.interactorStyle.OnMouseMove()
            
    def __computePoint(self, scene, xyz):
        imagedata = scene.imagedata
        ptId = imagedata.FindPoint(xyz)
        if ptId == -1:
            return

        a = [0, 0, 0]
        imagedata.GetPoint(ptId, a)
        
        o = imagedata.GetOrigin()
        s = imagedata.GetSpacing()
        e = imagedata.GetExtent()
        
        iq = [0, 0, 0]
        iqtemp = 0
        
        for i in range(3):
            iqtemp = vtk.vtkMath.Round((a[i] - o[i]) / s[i])
            if iqtemp < e[2*i]:
                iq[i] = e[2*i]
            elif iqtemp > e[2*i+1]:
                iq[i] = e[2*i+1]
            else:
                iq[i] = iqtemp
                
            xyz[i] = iq[i] * s[i] + o[i]

        return (xyz, ptId)
    
