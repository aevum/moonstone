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
import math
import sys

from PySide import QtCore, QtGui
import vtk

from ......bloodstone.scenes.imageplane import VtkImagePlane
from ......gui.qt.widget.genericload import GenericProgressBar
from ......bloodstone.utils import msmath


class ResliceAction(QtCore.QObject):

    def __init__(self, ilsa):
        logging.debug("In ReslicerAction::__init__()")
        super(ResliceAction, self).__init__(ilsa.parentWidget())
        self._ilsa = ilsa
        self.createWidgets()
        self.createActions()
        self.biDimensionalWidget = None
        self._action = False
        self._rigthButtonPressEvent = None
        
    def createWidgets(self):
        logging.debug("In ReslicerAction::createWidgets()")
        icon41 = QtGui.QIcon()
        icon41.addPixmap(
            QtGui.QPixmap(":/static/default/icon/48x48/half-skull.png"), 
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionResliceOblique = QtGui.QAction(self.parent())
        self.actionResliceOblique.setCheckable(True)
        self.actionResliceOblique.setIcon(icon41)
        self.actionResliceOblique.setObjectName("actionReslicePerpendicular")
        self.actionResliceOblique.setText(
            QtGui.QApplication.translate("ResliceAction", "&Reslice",
                                         None, QtGui.QApplication.UnicodeUTF8))
        
        self.parent().menuTools.addAction(self.actionResliceOblique)
        self.parent().toolBarTools.addAction(self.actionResliceOblique)
        
        

    def uncheck(self, actionType):
        logging.debug("In ReslicerAction::uncheck()")
        if self.actionResliceOblique.isChecked():
            self.actionResliceOblique.setChecked(False)
            self.slotActionResliceOblique()

    def createActions(self):
        logging.debug("In ReslicerAction::createActions()")
        self.connect(self.actionResliceOblique, 
                     QtCore.SIGNAL("triggered()"),
                     self.slotActionResliceOblique)

    def slotMouseWheelForwardCallback(self, obj, event, vtkPlane):
        logging.debug("In ReslicerAction::slotMouseWheelForwardCallback()")
        vtkPlane.planeSlide.setValue(vtkPlane.planeSlide.value()+1)
        
    def slotMouseWheelBackwardCallback(self, obj, event, vtkPlane):
        logging.debug("In ReslicerAction::slotMouseWheelBackwardCallback()")
        vtkPlane.planeSlide.setValue(vtkPlane.planeSlide.value()-1)
        
    def slotActionResliceOblique(self):
        logging.debug("In ReslicerAction::slotActionResliceOblique()")
        self._action = False
        
        scenes = self._ilsa.scenes()
        if not self.actionResliceOblique.isChecked():
            if self.biDimensionalWidget:
                self.biDimensionalWidget.Off()
            for plane, widget in self.biDimensionalWidgets.items():
                widget.Off()
                plane.scene.renderer.Render()
                plane.scene.window.Render()
                widget = None
            self.biDimensionalWidgets = {}
            for scene in scenes:
                if isinstance(scene, VtkImagePlane):
                    scene.coords = []
                    if self.biDimensionalWidget:
                        self.biDimensionalWidget.Off()
                        self.biDimensionalWidget = None
                    scene.removeObserver(self._rigthButtonPressEvent)
                    scene.removeObserver(self._rightButtonReleaseEvent)
                    scene.removeObserver(self._mouseWheelForwardEvent)
                    scene.removeObserver(self._mouseWheelBackwardEvent)
                    self._rigthButtonPressEvent = None
                    scene.window.Render()
            return 
        self._ilsa.desactivateOthers("reslice")
        planes = self._ilsa.planes()
        self.biDimensionalWidgets = {}
        for plane in planes:
            scene = plane.scene
            if isinstance(scene, VtkImagePlane) and scene.planeOrientation == VtkImagePlane.PLANE_ORIENTATION_AXIAL:
                scene.coords = []
                scene.msgBoxExec = 0
                rep = vtk.vtkBiDimensionalRepresentation2D()
                rep.GetPoint1Representation().GetProperty().SetColor(1,1,0)
                rep.GetPoint2Representation().GetProperty().SetColor(1,1,1)
                rep.GetPoint3Representation().GetProperty().SetColor(1,1,1)
                rep.GetPoint4Representation().GetProperty().SetColor(1,1,0)
                rep.GetTextProperty().SetFontSize(8)
                rep.PickableOff()
                handler = vtk.vtkPointHandleRepresentation2D()
                rep.SetHandleRepresentation(handler)
                
                biDimensionalWidget = vtk.vtkBiDimensionalWidget()
                biDimensionalWidget.SetRepresentation(rep)
                biDimensionalWidget.SetInteractor(scene.interactor)
                biDimensionalWidget.AddObserver("PlacePointEvent",
                    lambda o, e, s=plane: self.biDimensionalAddPoint(o, e, s))
                biDimensionalWidget.On()
                self.biDimensionalWidgets[plane] = biDimensionalWidget
                    
    def resliceObliqueButtonCallback(self, obj, event, vtkPlane):
        logging.debug("In RescliceAction::resliceObliqueButtonCallback()")
        if event == "RightButtonReleaseEvent":
            obj.OnRightButtonUp()
            scene = vtkPlane.scene
            self.VTKP = vtkPlane
            
            icon41 = QtGui.QIcon()
            icon41.addPixmap(
                QtGui.QPixmap(":/static/default/icon/22x22/insert-table.png"),
                QtGui.QIcon.Normal, QtGui.QIcon.Off)
            actionMakeVolume = QtGui.QAction(vtkPlane)
            actionMakeVolume.setCheckable(True)
            actionMakeVolume.setIcon(icon41)
            actionMakeVolume.setObjectName("actionMakeVolume")
            actionMakeVolume.setText(
                QtGui.QApplication.translate("MainWindow", "&Make Volume",
                                             None, QtGui.QApplication.UnicodeUTF8))
            self.connect(actionMakeVolume, 
                     QtCore.SIGNAL("triggered()"),
                     self.slotActionMakeVolume)
            
            icon42 = QtGui.QIcon()
            icon42.addPixmap(
                QtGui.QPixmap(":/static/default/icon/22x22/insert-table.png"),
                QtGui.QIcon.Normal, QtGui.QIcon.Off)
            actionMakeVolumeWithout3D = QtGui.QAction(vtkPlane)
            actionMakeVolumeWithout3D.setCheckable(True)
            actionMakeVolumeWithout3D.setIcon(icon41)
            actionMakeVolumeWithout3D.setObjectName("actionMakeVolumeWithout3D")
            actionMakeVolumeWithout3D.setText(
                QtGui.QApplication.translate("MainWindow", "&Make Volume without 3D",
                                             None, QtGui.QApplication.UnicodeUTF8))
            self.connect(actionMakeVolumeWithout3D, 
                     QtCore.SIGNAL("triggered()"),
                     self.slotActionMakeVolumeWithout3D)
            
            actionMakeVolume.setEnabled(True)
                
            menu = QtGui.QMenu(vtkPlane)
            menu.addAction(actionMakeVolume)
            menu.addAction(actionMakeVolumeWithout3D)
            menu.exec_(QtGui.QCursor.pos())
            obj.OnRightButtonUp()
        else:
            obj.OnRightButtonDown()
    
    
    def slotActionMakeVolumeWithout3D(self):
        logging.debug("In ReslicerAction::slotActionMakeVolumeWithout3D()")
        self.slotActionMakeVolume(0)
        
    def slotActionMakeVolume(self, generate3D=1):
        logging.debug("In ReslicerAction::slotActionMakeVolume()")
        vtkPlane = self.VTKP
        scene = vtkPlane.scene
        self.load = GenericProgressBar(self._ilsa.parentWidget(), progressBar=True)
        self.load.updateProgress(0, QtGui.QApplication.translate("ResliceAction", "Calculating...",
                                             None, QtGui.QApplication.UnicodeUTF8))
        obj1 = self.biDimensionalWidget

        rep = obj1.GetRepresentation()
        p1 = [0, 0, 0]
        rep.GetPoint1WorldPosition(p1)
        rep.SetPoint1WorldPosition(p1)

        p2 = [0, 0, 0]
        rep.GetPoint2WorldPosition(p2)
        rep.SetPoint2WorldPosition(p2)

        p3 = [0, 0, 0]
        rep.GetPoint3WorldPosition(p3)
        rep.SetPoint3WorldPosition(p3)

        p4 = [0, 0, 0]
        rep.GetPoint4WorldPosition(p4)
        rep.SetPoint4WorldPosition(p4)

        scene.coords = [p1, p2, p3, p4]
        self.reslice(vtkPlane, generate3D)

        self.biDimensionalWidget.Off()
        self.biDimensionalWidget = None

        self.actionResliceOblique.setChecked(False)
        self.slotActionResliceOblique()

        self.load.stopProcess()
        del self.load
        
            
    def biDimensionalAddPoint(self, obj, event, plane):
        logging.debug("In ReslicerAction::biDimensionalAddPoint()")
        scene = plane.scene

        if  not self._rigthButtonPressEvent:
            self._rigthButtonPressEvent = scene.addObserver("RigthButtonPressEvent",
                                                            lambda o, e, p=plane: self.resliceObliqueButtonCallback(o, e, p))
            self._rightButtonReleaseEvent = scene.addObserver("RightButtonReleaseEvent",
                                                              lambda o, e, p=plane: self.resliceObliqueButtonCallback(o, e, p))
            self._mouseWheelForwardEvent = scene.addObserver(
                "MouseWheelForwardEvent",
                lambda o, e, p=plane: self.slotMouseWheelForwardCallback(o, e, p))
            self._mouseWheelBackwardEvent = scene.addObserver(
                "MouseWheelBackwardEvent",
                lambda o, e, p=plane: self.slotMouseWheelBackwardCallback(o, e, p))
        if self.biDimensionalWidgets:
            self.biDimensionalWidget = self.biDimensionalWidgets.pop(plane)
            for box in self.biDimensionalWidgets.values():
                box.SetInteractor(None)
            self.biDimensionalWidgets.clear()
        
        (X, Y) = scene.interactor.GetEventPosition()
        
        scene.picker.Pick(X, Y, 0, scene.renderer)
        
        (px, py, pz) = scene.picker.GetPickPosition()
        (xyz, ptId) = self.__computePoint(scene, [px, py, pz])
        if xyz is None:
            return
        p = list(xyz)
        
        ###teste
        imagedata = scene.imagedata
        ptId = imagedata.FindPoint(p)
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
                
            p[i] = iq[i] * s[i] + o[i]

        (px, py, pz) = p
        xyz = p
        scene.coords.append(xyz)

    def reslice(self, plane, generate3D):
        logging.debug("In ReslicerAction::reslice()")
        scene = plane.scene
        if len(scene.coords) >= 4:
            p1, p2, p3, p4 = scene.coords[0:4]
            
            if scene.planeOrientation == scene.PLANE_ORIENTATION_SAGITTAL: 
                type = 0
            elif scene.planeOrientation == scene.PLANE_ORIENTATION_CORONAL: 
                type = 1
            else:
                type = 2
                
            #getting the plane normal to use like direction of cutting
            n = list(scene.planeSource.GetNormal())
            origin = scene.imagedata.GetOrigin()
            #scene.vtkActorTransform.TransformPoint(origin, origin)
            
            planeProj = vtk.vtkPlane()
            planeProj.SetOrigin(origin)
            planeProj.SetNormal(n)
            
            vtk.vtkPlane.ProjectPoint(p1, planeProj.GetOrigin(), planeProj.GetNormal(), p1)
            vtk.vtkPlane.ProjectPoint(p2, planeProj.GetOrigin(), planeProj.GetNormal(), p2)
            vtk.vtkPlane.ProjectPoint(p3, planeProj.GetOrigin(), planeProj.GetNormal(), p3)
            vtk.vtkPlane.ProjectPoint(p4, planeProj.GetOrigin(), planeProj.GetNormal(), p4)

            u1 = [(_p2-_p1)*0.5 for _p1,_p2 in zip(p4, p3)]
            o1 = [_p1+_v1 for _p1,_v1 in zip(p2, u1)]
            
            u2 = [(_p2-_p1)*0.5 for _p1,_p2 in zip(p4, p3)]
            o2 = [_p1+_v1 for _p1,_v1 in zip(p1, u2)]
            
            u3 = [(_p2-_p1)*0.5 for _p1,_p2 in zip(p3, p4)]
            o3 = [_p1+_v1 for _p1,_v1 in zip(p1, u3)]
            
            u4 = [(_p2-_p1)*0.5 for _p1,_p2 in zip(p3, p4)]
            o4 = [_p1+_v1 for _p1,_v1 in zip(p2, u4)]
            
            origin = scene.imagedata.GetOrigin()
            dist1 = math.sqrt(vtk.vtkMath.Distance2BetweenPoints(o1, origin))
            dist2 = math.sqrt(vtk.vtkMath.Distance2BetweenPoints(o2, origin))
            dist3 = math.sqrt(vtk.vtkMath.Distance2BetweenPoints(o3, origin))
            dist4 = math.sqrt(vtk.vtkMath.Distance2BetweenPoints(o4, origin))
            if dist1 <= min([dist2, dist3, dist4]):
                q1, q2, q3, q4 = o1, o2, o3, o4
            elif dist2 <= min([dist1, dist3, dist4]):
                q1, q2, q3, q4 = o2, o3, o4, o1
            elif dist3 <= min([dist2, dist1, dist4]):
                q1, q2, q3, q4 = o3, o4, o1, o2
            else:
                q1, q2, q3, q4 = o4, o1, o2, o3
            origin = q1
            
            d1 = math.sqrt(vtk.vtkMath.Distance2BetweenPoints(q1, q2))
            d2 = math.sqrt(vtk.vtkMath.Distance2BetweenPoints(q1, q4))
            
            # ----------------------------------------------------------------
            t1, t2, t3 = q1, q2, [q2[0], q1[1], q2[2]]
            hi = math.sqrt(vtk.vtkMath.Distance2BetweenPoints(t1, t2))
            ca = math.sqrt(vtk.vtkMath.Distance2BetweenPoints(t1, t3))
            
            u1 = [_2-_1 for _1,_2 in zip(t1, t2)]

            cos = math.acos(ca / hi)
            angle = math.degrees(cos)
            self.TETHA = -angle if u1[1] < 0 else angle
            self.FATOR_CAMERA = 1.0 if u1[1] < 0 else -1.0
            
            transform = vtk.vtkTransform()
            transform.Concatenate(scene.transform)
            transform.RotateZ(self.TETHA)
            transform.Update()
            
            # Canonica!
            xAxis = [1.0, 0.0, 0.0, 0.0]
            transform.MultiplyPoint(xAxis, xAxis)
            xAxis = xAxis[0:3]
            vtk.vtkMath.Normalize(xAxis)
            
            yAxis = [0.0, 1.0, 0.0, 0.0]
            transform.MultiplyPoint(yAxis, yAxis)
            yAxis = yAxis[0:3]
            vtk.vtkMath.Normalize(yAxis)
            
            zAxis = [0.0, 0.0, 0.0]
            vtk.vtkMath.Cross(xAxis, yAxis, zAxis)
            vtk.vtkMath.Normalize(zAxis)
            
            origin2 = scene.imagedata.GetOrigin()
            extent = scene.imagedata.GetWholeExtent()
            spacing = scene.imagedata.GetSpacing()
            
            bounds = [origin2[0] + spacing[0]*extent[0], # xmin
                      origin2[0] + spacing[0]*extent[1], # xmax
                      origin2[1] + spacing[1]*extent[2], # ymin
                      origin2[1] + spacing[1]*extent[3], # ymax
                      origin2[2] + spacing[2]*extent[4], # zmin
                      origin2[2] + spacing[2]*extent[5]] # zmax
            
            thePlaneNormal = [0,0,0]
            thePlaneNormal[type] = 1
            thePlaneOriginBase = [bounds[0],bounds[2], bounds[4]]
            thePlaneOriginTop = [bounds[1],bounds[3], bounds[5]]
            
            corners = []
            corners.append((q1, [y+z for y, z in zip(n, q1)]))
            corners.append((q2, [y+z for y, z in zip(n, q2)]))
            corners.append((q3, [y+z for y, z in zip(n, q3)]))
            corners.append((q4, [y+z for y, z in zip(n, q4)]))
            
            distB = 0
            distBN = sys.maxint
            distT = 0
            distTN = 0
            originBaseOffset = [0,0,0]
            originBaseOffsetN = [0,0,0]
            for q, c in corners:
                qb = msmath.intersect_line_with_plane(q, c, thePlaneNormal, thePlaneOriginBase)
                qt = msmath.intersect_line_with_plane(q, c, thePlaneNormal, thePlaneOriginTop)
                dist = math.sqrt(vtk.vtkMath.Distance2BetweenPoints(q, qb))
                if dist > distB:
                    originBaseOffset = [y - z for y, z in zip(qb, q)]
                    distB = dist
                if dist < distBN:
                    originBaseOffsetN = [y - z for y, z in zip(qb, q)]
                    distBN = dist
                dist = math.sqrt(vtk.vtkMath.Distance2BetweenPoints(q, qt))
                if dist > distT:
                    distT = dist
                    distTN = math.sqrt(vtk.vtkMath.Distance2BetweenPoints([p1 + p2 for p1, p2 in zip(q, n)], qt))
                    
            if distTN > distT:
                n = [-p for p in n] 
            
            if originBaseOffset[type] > 0:
                origin = [y + z for y, z in zip(origin, originBaseOffsetN)]
                distH = distT - distBN
            else:
                origin = [y + z for y, z in zip(origin, originBaseOffset)]
                distH = distT + distB
                
            
            q5 = [x * distT + y for x, y in zip(n, q1)]
            q6 = [x * distT + y for x, y in zip(n, q2)]
            q7 = [x * distT + y for x, y in zip(n, q3)]
            q8 = [x * distT + y for x, y in zip(n, q4)]
                
            q1 = [y - x * distH for x, y in zip(n, q5)]
            q2 = [y - x * distH for x, y in zip(n, q6)]
            q3 = [y - x * distH for x, y in zip(n, q7)]
            q4 = [y - x * distH for x, y in zip(n, q8)]
               
            
            cubeCorners = [q1, q5, q4, q8, q2, q6, q3, q7] 
            self.load.updateProgress(10, self.load.updateProgress(0, 
                                                    QtGui.QApplication.translate("ResliceAction", 
                                                        "Slicing...",
                                                        None, 
                                                        QtGui.QApplication.UnicodeUTF8)))

            activeSubWindow = self._ilsa.activeSubWindow()
            if activeSubWindow:
                subWindow =  self._ilsa.windowArea()
                
            self.load.updateProgress(100, QtGui.QApplication.translate("ResliceAction", 
                                                        "Completed",
                                                        None, 
                                                        QtGui.QApplication.UnicodeUTF8))

            subWindow.createMScreensFromImagedata(scene.imagedata, cubeCorners=cubeCorners, generate3D = generate3D)
            scene.window.Render()
    
    def __computePoint(self, scene, xyz):
        logging.debug("In ReslicerAction::__computePoint()")
        imagedata = scene.imagedata
        ptId = imagedata.FindPoint(xyz)
        if ptId == -1:
            return (None, None)

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

        return xyz, ptId
    