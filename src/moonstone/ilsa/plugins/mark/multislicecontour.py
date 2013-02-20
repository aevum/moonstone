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
from ....bloodstone.scenes.imageplane import VtkImagePlane
from ....bloodstone.scenes.sliceimageplane import VtkSliceImagePlane
from ....bloodstone.scenes.imagevolume import VtkImageVolume
from contour import Contour

class MultiSliceContour(Contour):

    def __init__(self, scene):
        logging.debug("In MultiSliceContour::__init__()")
        super(MultiSliceContour, self).__init__(scene)
        self._tubeActor = None
        self._originalPoints = []
        self._scene.addTransformListener(self)
        self._pointMap = {}
        
    @property
    def lineColor(self):
        logging.debug("In Contour::lineColor.getter()")
        return self._lineColor
    
    @lineColor.setter 
    def lineColor(self, lineColor):
        logging.debug("In Contour::lineColor.setter")
        self._lineColor = lineColor
        self._representation.GetLinesProperty().SetColor(self._lineColor)
        for tubeActor in self._tubeActor:
            tubeActor.GetProperty().SetColor(self._lineColor)
        self.scene.window.Render()
    
    @property
    def visible(self):
        logging.debug("In Contour::visible.getter()")
        return self._visible  
       
    @visible.setter   
    def visible(self, value):
        logging.debug("In Contour::visible.setter()")
        if self._tubeActor:
            for tubeActor in self._tubeActor:
                tubeActor.SetVisibility(value)
        self._contourWidget.SetEnabled(value)
        self._scene.window.Render()
        self._visible  = value
    
    def delete(self):
        logging.debug("In MultiSliceContour::delete()")
        self.scene.removeTransformListener(self)
        self._contourWidget.Off()
        self.removeStartEvent()
        if self._tubeActor:
            for tubeActor in self._tubeActor: 
                self._scene.renderer.RemoveActor(tubeActor)
        self._scene.window.Render()
        self._tubeActor = None
        self._tubeFilter = None
    
    def _createCutter(self):
        logging.debug("In MultiSliceContour::createCutter()")
        self._cutters = []
        self._planeCutters = []
        for slice in self._scene.slice:
            cutter = vtk.vtkCutter()
            plane = vtk.vtkPlane()
            plane.SetOrigin(slice.plane.GetOrigin())
            plane.SetNormal(slice.plane.GetNormal())
            cutter.SetCutFunction(plane)
            cutter.GenerateCutScalarsOn()
            self._planeCutters.append(plane)
            self._cutters.append(cutter)

    def _createTube(self):
        logging.debug("In MultiSliceContour::createTube()")
        
        points = vtk.vtkPoints()
        for point in self._originalPoints:
            points.InsertNextPoint(point)
                   
        self._parametricSpline = vtk.vtkParametricSpline()
        self._parametricSpline.SetPoints(points)
        
        self._parametricFuntionSource = vtk.vtkParametricFunctionSource()
        self._parametricFuntionSource.SetParametricFunction(self._parametricSpline)
        self._parametricFuntionSource.SetUResolution(100)
        
        self._tubeFilter = vtk.vtkTubeFilter()
        self._tubeFilter.SetNumberOfSides(10)
        self._tubeFilter.SetRadius(self._radius)
        self._tubeFilter.SetInputConnection(self._parametricFuntionSource.GetOutputPort())
        
        self._tubeActor = []
        self._cubes = []
        i = 0
        for cutter in self._cutters:
            cutter.SetInputConnection(self._tubeFilter.GetOutputPort())
            cutter.Update()
            
            cube = vtk.vtkBox()
            #TODO change imagebounds to planesourceRange
            cube.SetBounds(self._scene.slice[i].getBounds())
            clip = vtk.vtkClipPolyData()
            clip.SetClipFunction(cube)
            clip.SetInputConnection(cutter.GetOutputPort())
            clip.InsideOutOn()
            clip.Update()          
            self._cubes.append(cube)
            
            tubeMapper=vtk.vtkPolyDataMapper()
            tubeMapper.ScalarVisibilityOff()
            tubeMapper.SetInputConnection(clip.GetOutputPort())
            tubeMapper.GlobalImmediateModeRenderingOn()
            
            tubeActor = vtk.vtkActor()
            tubeActor.SetMapper(tubeMapper)
            tubeActor.GetProperty().LightingOff()
            tubeActor.GetProperty().SetColor(self.lineColor)
            tubeActor.SetUserTransform(self._scene.slice[i].resliceTransform.GetInverse())
            
            
            self._tubeActor.append(tubeActor)
            self._scene.renderer.AddActor(tubeActor)
            i = i+1                
    
    def _updateTube(self):
        logging.debug("In MultiSliceContour::updateTube()")
        points = vtk.vtkPoints()
        for point in self._originalPoints:
            points.InsertNextPoint(point)
        self._parametricSpline.SetPoints(points)
        for i in range(len(self._tubeActor)):
            t = self._scene.slice[i].resliceTransform.GetInverse()
            t.PostMultiply()
            position = self._scene.camera.GetPosition()
            focalPoint = self._scene.camera.GetFocalPoint()
            vec = [f - p for f, p in zip(focalPoint, position)]
            vtk.vtkMath.Normalize(vec)
            vector = [p / -10000.0 for p in vec]
            t.Translate(vector)
            t.Update()
            self._tubeActor[i].SetUserTransform(t)
            self._cubes[i].SetBounds(self._scene.slice[i].getBounds())
            self._planeCutters[i].SetOrigin(self._scene.slice[i].plane.GetOrigin())
            self._planeCutters[i].SetNormal(self._scene.slice[i].plane.GetNormal())
            
            
    def getPropertiesFromMark(self, mark):
        logging.debug("In MultiSliceContour::getPropertiesFromMark()")
        i = self._representation.GetNumberOfNodes()
        pts = mark.originalPoints
        while i < len(pts):
            if i == 0:
                pd = vtk.vtkPolyData()
                points = vtk.vtkPoints()
                points.InsertPoint(0, 0, 0 ,0)
                pd.SetLines(vtk.vtkCellArray())
                pd.SetPoints(points)
                self._start(None, None)
                self._contourWidget.Initialize(pd, 1)
            else:
                self._representation.AddNodeAtWorldPosition([0 , 0, 0])
            i = i+1
            
        i = 0  
        self._pointMap.clear() 
        while i < len(pts):
            p = self._scene.fromOriginalView(pts[i])
            self._representation.SetNthNodeWorldPosition(i, p)
            self._pointMap[(p[0], p[1], p[2])] = pts[i] 
            i = i + 1
            
        self._originalPoints = pts

        if self._representation.GetNumberOfNodes() >= 2:
            if self._tubeActor:
                self._updateTube()
            else:
                self._createTube()
        
        self._scene.window.Render()

    def _reply(self):
        logging.debug("In MultiSliceContour::reply()")
        self._reloadOriginalPoints()
        for mark in self._replyList:
            mark.getPropertiesFromMark(self)
    
    def save(self):
        logging.debug("In MultiSliceContour::save()")
        yaml = {}
        yaml["lineColor"] = self._lineColor
        yaml["visible"] = self.visible
        yaml["locked"] = self.locked
        yaml["radius"] = self.radius
        points = []
        i = 0
        while i < self._representation.GetNumberOfNodes():
            addPosition = [0,0,0]
            self._representation.GetNthNodeWorldPosition(i, addPosition)
            if self._pointMap.has_key((addPosition[0], addPosition[1], addPosition[2])):
                addPosition = self._pointMap[(addPosition[0], addPosition[1], addPosition[2])]
            else:
                addPosition = self._scene.toOriginalView(addPosition) 
            points.append(addPosition)
            i = i + 1
        yaml["points"] = points
        return yaml
    
    def loadPoints(self, points):
        logging.debug("In MultiSliceContour::loadPoints()")
        self._originalPoints = points
        self._pointMap.clear()
        for point in points:
            p = self._scene.fromOriginalView(point) 
            self._addPoint(p)
            self._pointMap[(p[0], p[1], p[2])] = point
        self._reply()
        if self._representation.GetNumberOfNodes() >= 2:
            if self._tubeActor:
                self._updateTube()
            else:
                self.createTube()
                if isinstance(self._scene, VtkImagePlane):
                    self.removeStartEvent()
                for contour in self._replyList:
                    if isinstance(contour.scene, VtkImagePlane):
                        contour.removeStartEvent()
                
        self._scene.window.Render()
    
    def resetCutters(self):
        #TODO reaproveitar objetos
        self._planeCutters = []
        if self._tubeActor:
            for tubeActor in self._tubeActor: 
                self._scene.renderer.RemoveActor(tubeActor)
        for cutter in self._cutters:
            cutter.SetInputConnection(None)
        self._createCutter()
        self._createTube()
    
    
    def updateTransform(self):
        if len(self._scene.slice) != len(self._planeCutters):
            self.resetCutters()
        self.getPropertiesFromMark(self)
    
    def addScene(self, scene):
        logging.debug("In MultiSliceContour::addScene()")
        contour = Contour(scene)
        
        self._replyList.append(contour)
        for rContour in  self._replyList:
            rContour.replyList.append(contour)

        replyList = self._replyList[:]
        replyList.append(self)
        contour.replyList = replyList
        
        
        points =  []
        i = 0
        while i < self._representation.GetNumberOfNodes():
            addPosition = [0,0,0]
            self._representation.GetNthNodeWorldPosition(i, addPosition)
            if self.pointMap.has_key((addPosition[0], addPosition[1], addPosition[2])):
                addPosition = self._pointMap[(addPosition[0], addPosition[1], addPosition[2])]
            else:
                addPosition = self._scene.toOriginalView(addPosition) 
            points.append(addPosition)
            i = i + 1
        
        contour.loadPoints(points)
        
        contour.lineColor = self.lineColor
        contour.visible = self.visible
        if self.locked:
            contour.lock()
        else:
            contour.unlock()
        contour.radius = self.getRadius()
        
    def _reloadOriginalPoints(self):
        i = 0    
        result = []
        while i < self._representation.GetNumberOfNodes():
            addPosition = [0,0,0]
            self._representation.GetNthNodeWorldPosition(i, addPosition)
            if self._pointMap.has_key((addPosition[0], addPosition[1], addPosition[2])):
                addPosition = self._pointMap[(addPosition[0], addPosition[1], addPosition[2])]
            else:
                addPosition = self._scene.toOriginalView(addPosition)
            result.append(addPosition)
            i = i+1
        self._originalPoints =  result
    
    @property        
    def originalPoints(self):
        return self._originalPoints
    
    def _endIteractAction(self, obj, evt):
        logging.debug("In Contour::_endIteractAction()")
        self._reply()
        self.updateTransform()
        