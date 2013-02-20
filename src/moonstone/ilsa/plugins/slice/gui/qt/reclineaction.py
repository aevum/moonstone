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
import math
import logging
import vtk
from PySide import QtCore, QtGui

import widget.resources_rc
from ......bloodstone.scenes.sliceimageplane import VtkSliceImagePlane

class ReclineAction(QtCore.QObject):

    def __init__(self, ilsa):
        logging.debug("In ReclineAction::__init__()")
        super(ReclineAction, self).__init__(ilsa.parentWidget())
        self._ilsa = ilsa
        self.createWidgets()
        self.createActions()

        self.actions = {}
        self.actions["Slicing"] = 0
        self.actions["Rotate"] = 0
        self.actions["RotateZ"] = 0
        self.points = []
        self.centers = []
        
    def createWidgets(self):
        logging.debug("In ReclineAction::createWidgets()")
         
        icon41 = QtGui.QIcon()
        icon41.addPixmap(
            QtGui.QPixmap(":/static/default/icon/22x22/step_object_Gas.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionReclineWithThreePoints = QtGui.QAction(self.parent())
        self.actionReclineWithThreePoints.setCheckable(True)
        self.actionReclineWithThreePoints.setIcon(icon41)
        self.actionReclineWithThreePoints.setObjectName("actionReclineWithThreePoints")
        self.actionReclineWithThreePoints.setText(
            QtGui.QApplication.translate("ReclineAction",
                                         "Recline With Three &Points",
                                         None, QtGui.QApplication.UnicodeUTF8))
        
        self.parent().menuTools.addAction(self.actionReclineWithThreePoints)
        self.parent().toolBarTools.addAction(self.actionReclineWithThreePoints)
        
    
    def uncheck(self, actionType):
        if self.actionReclineWithThreePoints.isChecked():
            self.actionReclineWithThreePoints.setChecked(False)
            self.slotActionReclineWithThreePoints()

    def createActions(self):
        logging.debug("In ReclineAction::createActions()")
        self.connect(self.actionReclineWithThreePoints, 
                     QtCore.SIGNAL("triggered()"),
                     self.slotActionReclineWithThreePoints)

                
    def slotActionReclineWithThreePoints(self):
        logging.debug("In ReclineAction::slotActionReclineWithThreePoints()")
        self._action = False
        scenes = self._ilsa.scenes()
        if not self.actionReclineWithThreePoints.isChecked():
            self.removeObservers()
            for scene in scenes:
                if isinstance(scene, VtkSliceImagePlane) and scene.planeOrientation != VtkSliceImagePlane.PLANE_ORIENTATION_PANORAMIC_SLICE: 
                    for actor in self.disks:
                        try:
                            scene.renderer.RemoveActor(actor)   
                        except:
                            pass
                    scene.window.Render()
            scene.P = []
            self.disks = []
            return 
        self._ilsa.desactivateOthers("slice")
        planes = self._ilsa.planes()
        self.leftButtonPressEvent = {}
        self.rightButtonPressEvent = {}
        self.mouseWheelForwardEvent = {}
        self.mouseWheelBackwardEvent = {}
        for plane in planes:
            scene = plane.scene
            
            if isinstance(scene, VtkSliceImagePlane) and scene.planeOrientation != VtkSliceImagePlane.PLANE_ORIENTATION_PANORAMIC_SLICE:
                scene.P = []
                self.disks = []
                self.leftButtonPressEvent[scene] = scene.addObserver("LeftButtonPressEvent", 
                    lambda o, e, s=plane: \
                        self.slotLeftClick(o, e, s))
                self.rightButtonPressEvent[scene] = scene.addObserver("RightButtonPressEvent", 
                    lambda o, e, s=plane: \
                        self.slotRightClick(o, e, s))
                self.mouseWheelForwardEvent[scene] = scene.addObserver(
                    "MouseWheelForwardEvent", 
                    lambda o, e, p=plane: self.slotMouseWheelForward(o, e, p))
                self.mouseWheelBackwardEvent[scene] = scene.addObserver(
                    "MouseWheelBackwardEvent", 
                    lambda o, e, p=plane: self.slotMouseWheelBackward(o, e, p))
                
    def removeObservers(self):
        if self.leftButtonPressEvent:
            for scene, observer in self.leftButtonPressEvent.items():
                scene.removeObserver(observer)
        if self.rightButtonPressEvent:
            for scene, observer in self.rightButtonPressEvent.items():
                scene.removeObserver(observer)
        if self.mouseWheelForwardEvent:
            for scene, observer in self.mouseWheelForwardEvent.items():
                scene.removeObserver(observer)
        if self.mouseWheelBackwardEvent:
            for scene, observer in self.mouseWheelBackwardEvent.items():
                scene.removeObserver(observer)
        
        self.leftButtonPressEvent = {}
        self.rightButtonPressEvent = {}
        self.mouseWheelForwardEvent = {}
        self.mouseWheelBackwardEvent = {}
                
    def slotRightClick(self, obj, event, plane):
        logging.debug("In ReclineAction::slotRightClick()")
        try:
            if plane.scene.P:
                actor = self.disks.pop(len(self.disks)-1)
                plane.scene.renderer.RemoveActor(actor)
                plane.scene.P.pop(len(plane.scene.P)-1)
                plane.scene.window.Render()
        except:
            pass
      
    def slotLeftClick(self, obj, event, plane):
        logging.debug("In ReclineAction::slotLeftClick()")
        scene = plane.scene
        if scene.interactor.GetRepeatCount() >= 0:
            for scen in self._ilsa.scenes(): 
                if scen != scene:
                    try:
                        if len(scen.P) > 0:
                            return
                    except:
                        continue
            (X, Y) = scene.interactor.GetEventPosition()
            scene.picker.Pick(X, Y, 0, scene.renderer)
            x, y, z = scene.picker.GetPickPosition()
            xyz = [x, y, z]
            if xyz is None:
                return
            sphereSource = vtk.vtkSphereSource()
            sphereSource.SetCenter(xyz)
            sphereSource.SetRadius(1)

            sphereMapper = vtk.vtkPolyDataMapper()
            sphereMapper.SetInputConnection(sphereSource.GetOutputPort())
            sphereMapper.SetResolveCoincidentTopologyToPolygonOffset()

            sphereActor = vtk.vtkActor()
            sphereActor.SetMapper(sphereMapper)
            sphereActor.PickableOff()
            sphereActor.GetProperty().SetColor(1.0, 0.0, 0.0)
            
            scene.renderer.AddActor(sphereActor)
                
            self.disks.append(sphereActor)
            
            scene.P.append(xyz)
            if len(scene.P) >= 3:
                q1, q2, q3 = scene.P[0:3]
                scene.P = []   
                self.reclineWithThreePoints(scene, q1, q2, q3, self._ilsa.activeScenes())
                for scene in self._ilsa.activeScenes():
                    if isinstance(scene, VtkSliceImagePlane) and scene.planeOrientation != VtkSliceImagePlane.PLANE_ORIENTATION_PANORAMIC_SLICE: 
                        for actor in self.disks:
                            try:
                                scene.renderer.RemoveActor(actor)   
                            except:
                                pass
                        scene.window.Render()
                        
                self.disks = []
            obj.OnLeftButtonDown()

    
    def reclineWithThreePoints(self, scene, q1, q2, q3, replyScenes = []):
        origin = scene.planeSource.GetOrigin()
        spacing = scene.imagedata.GetSpacing()
        extent = scene.imagedata.GetExtent()
                
        Oi = (
            origin[0] + spacing[0] * extent[0],
            origin[1] + spacing[1] * extent[2],
            origin[2] + spacing[2] * extent[4], 
        )
        Of = (
            origin[0] + spacing[0] * extent[1],
            origin[1] + spacing[1] * extent[3],
            origin[2] + spacing[2] * extent[5], 
        )
        
        init_left_bottom = [Oi[0], Oi[1], Oi[2]]
        
        dx = abs(extent[1]-extent[0])
        dy = abs(extent[3]-extent[2])
        dz = abs(extent[5]-extent[4])
        
        if scene.planeOrientation == scene.PLANE_ORIENTATION_SAGITTAL: 
            k = dz if dz <= dy else dy
            o = init_left_bottom
            pt1 = [o[0], o[1]+k*0.25, o[2]]
            pt2 = [o[0], o[1], o[2]+k*0.25]
            
            iPlaneCanonical = vtk.vtkPlane()
            iPlaneCanonical.SetOrigin(Oi)
            iPlaneCanonical.SetNormal(1.0, 0.0, 0.0)
            fPlaneCanonical = vtk.vtkPlane()
            fPlaneCanonical.SetOrigin(Of)
            fPlaneCanonical.SetNormal(1.0, 0.0, 0.0)
        elif scene.planeOrientation == scene.PLANE_ORIENTATION_CORONAL:
            k = dz if dz <= dx else dx
            o = init_left_bottom
            pt1 = [o[0], o[1], o[2]+k*0.25]
            pt2 = [o[0]+k*0.25, o[1], o[2]]
            
            iPlaneCanonical = vtk.vtkPlane()
            iPlaneCanonical.SetOrigin(Oi)
            iPlaneCanonical.SetNormal(0.0, 1.0, 0.0)
            fPlaneCanonical = vtk.vtkPlane()
            fPlaneCanonical.SetOrigin(Of)
            fPlaneCanonical.SetNormal(0.0, 1.0, 0.0)
        else:
            k = dx if dx <= dy else dy
            o = init_left_bottom
            pt1 = [o[0]+k*0.25, o[1], o[2]]
            pt2 = [o[0], o[1]+k*0.25, o[2]]
            
            iPlaneCanonical = vtk.vtkPlane()
            iPlaneCanonical.SetOrigin(Oi)
            iPlaneCanonical.SetNormal(0.0, 0.0, 1.0)
            fPlaneCanonical = vtk.vtkPlane()
            fPlaneCanonical.SetOrigin(Of)
            fPlaneCanonical.SetNormal(0.0, 0.0, 1.0)
        
        iPlaneCanonicalSource = vtk.vtkPlaneSource()
        iPlaneCanonicalSource.SetOrigin(iPlaneCanonical.GetOrigin())
        iPlaneCanonicalSource.SetNormal(iPlaneCanonical.GetNormal())                    
                            
        planeCanonicalSource = vtk.vtkPlaneSource()
        planeCanonicalSource.SetOrigin(o)
        planeCanonicalSource.SetPoint1(pt1)
        planeCanonicalSource.SetPoint2(pt2)
        planeCanonicalSource.Update()
                                
        planeSource = vtk.vtkPlaneSource()        
        planeSource.SetPoint1(q1)
        planeSource.SetOrigin(q2)
        planeSource.SetPoint2(q3)
        planeSource.Update()
        
        planeCenter = [0.0, 0.0, 0.0]
        vtk.vtkTriangle.TriangleCenter(q1, q2, q3, planeCenter)
                                                                 
        planeCanonicalSource.SetCenter(planeSource.GetCenter())
        planeCanonicalSource.SetNormal(planeSource.GetNormal())
        planeCanonicalSource.Update()
                            
        n1 = planeCanonicalSource.GetNormal()
        c1 = planeCanonicalSource.GetCenter()
        
        p1 = [p+(n*10) for p,n in zip(c1, n1)]
        
        origin = scene.imagedata.GetOrigin()
        spacing = scene.imagedata.GetSpacing()
        extent = scene.imagedata.GetExtent()
        
        centerImageData = (
            origin[0] + spacing[0] * 0.5 * (extent[0] + extent[1]),
            origin[1] + spacing[1] * 0.5 * (extent[2] + extent[3]),
            origin[2] + spacing[2] * 0.5 * (extent[4] + extent[5])
        )
        
        
        Normal = planeCanonicalSource.GetNormal()
        Origin = planeCanonicalSource.GetOrigin()
        Point1 = planeCanonicalSource.GetPoint1()
        Point2 = planeCanonicalSource.GetPoint2()
        Center = planeCanonicalSource.GetCenter()
        
#                    if scene.planeOrientation == scene.PLANE_ORIENTATION_SAGITTAL: 
#                        n = [1.0, 0.0, 0.0]
#                    elif scene.planeOrientation == scene.PLANE_ORIENTATION_CORONAL:
#                        n = [0.0, 1.0, 0.0]
#                    else:
#                        n = [0.0, 0.0, 1.0]
        n = list(scene.planeSource.GetNormal())
        rotVector = [0, 0, 0]
        theta = 0.0
        
        dp = vtk.vtkMath.Dot(Normal, n)
        if dp >= 1:
            for actor in self.disks:
                scene.renderer.RemoveActor(actor)
                
            self.disks = []
            scenes = self._ilsa.scenes()
            for scene in scenes:
                scene.window.Render()
                
            return
        elif dp <= -1:
            theta = 180.0
            rotVector = [p1-o for p1, o in zip(Point1, Origin)]
            vtk.vtkMath.Normalize(rotVector)
        else:
            vtk.vtkMath.Cross(n, Normal, rotVector)
            theta = vtk.vtkMath.DegreesFromRadians(math.acos(dp))
            
        # Solved flip!
        if theta > 90.0:
            theta += 180.0
        
        # create rotation matrix
        transform = vtk.vtkTransform()
        transform.PostMultiply()
        
        transform.Translate(-Center[0], -Center[1], -Center[2])
        transform.RotateWXYZ(theta, rotVector[0], rotVector[1], rotVector[2])
        transform.Translate(Center[0], Center[1], Center[2])
#        
#        print scene.parent
#        print scene.parent.mscreenParent
        scene.parent.mscreenParent.applyCubeTransform(transform)

#        Origin = transform.TransformPoint(Origin)
#        Point1 = transform.TransformPoint(Point1)
#        Point2 = transform.TransformPoint(Point2)
#        
#        centerImageDataProjXYi = [0.0, 0.0, 0.0] 
#        vtk.vtkPlane.ProjectPoint(centerImageData, 
#                                  iPlaneCanonical.GetOrigin(), 
#                                  iPlaneCanonical.GetNormal(),
#                                  centerImageDataProjXYi)
#        centerPlaneProjXYi = [0.0, 0.0, 0.0]
#        vtk.vtkPlane.ProjectPoint(Center, 
#                                  iPlaneCanonical.GetOrigin(), 
#                                  iPlaneCanonical.GetNormal(),
#                                  centerPlaneProjXYi)
#        
#        w1 = [cr-ci for ci,cr in zip(centerImageDataProjXYi, centerPlaneProjXYi)]
#        
#        #transform.Translate(w1)
#        #transform.Update()
#        
#        s1 = transform.TransformPoint(scene.imagedata.GetCenter())
#        w2 = [sf-si for si,sf in zip(s1, Center)]
#        
#        #transform.Translate(w2)
#        #transform.Update()
#        
#        origin = scene.imagedata.GetOrigin()
#        spacing = scene.imagedata.GetSpacing()
#        extent = scene.imagedata.GetExtent()
#                        
#        o1 = (
#            origin[0] + spacing[0] * extent[0],
#            origin[1] + spacing[1] * extent[2],
#            origin[2] + spacing[2] * extent[4],
#        )
#        o2 = (
#            origin[0] + spacing[0] * extent[1],
#            origin[1] + spacing[1] * extent[3],
#            origin[2] + spacing[2] * extent[5],
#        )
#
#        a1 = [o1[0], o1[1], o1[2]]
#        a3 = [o2[0], o2[1], o1[2]]
#        
#        b1 = transform.TransformPoint(a1)
#        b3 = transform.TransformPoint(a3)
#        u1 = [(_2-_1)*0.5 for _1,_2 in zip(a1, a3)]
#        u2 = [(_2-_1)*0.5 for _1,_2 in zip(b1, b3)]
#        c1 = [_1+_2 for _1,_2 in zip(b1, u2)]
#        w3 = [_2-_1 for _1,_2 in zip(c1, u1)]
#                    transform.Translate(w3)
#                    transform.Update()
        
#        for scen in replyScenes:
#            scen.transform = transform
#            scen.window.Render()
    
    def slotMouseWheelForward(self, obj, event, plane):
        plane.planeSlide.setValue(plane.planeSlideValue + 1)
        plane.planeSlide.update()
        plane.scene.window.Render()
        
    def slotMouseWheelBackward(self, obj, event, plane):        
        plane.planeSlide.setValue(plane.planeSlideValue - 1)
        plane.planeSlide.update()
        plane.scene.window.Render()

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    win = ReclineAction()
    win.show()
    sys.exit(app.exec_())