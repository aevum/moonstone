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
from ....bloodstone.scenes.multisliceimageplane import VtkMultiSliceImagePlane
from ....bloodstone.scenes.sliceimageplane import VtkSliceImagePlane
from ....bloodstone.scenes.imagevolume import VtkImageVolume


class Contour(object):

    def __init__(self, scene):
        logging.debug("In Contour::__init__()")
        self._contourWidget = vtk.vtkContourWidget()
        self._contourWidget.parent = self
        self._scene = scene
        self._representation = vtk.vtkOrientedGlyphContourRepresentation()
        self._representation.GetLinesProperty().SetColor(1,0,0)
        self._visible = True
        self._started = False
        self._tubeActor = None
        self._tubeFilter = None
        self._radius = 0.6
        self._lineColor = (1, 0, 0)
        self._createCutter()
        self._replyList = []
        self._showLine = True
        self._contourWidget.SetInteractor(scene.interactor)
        self._contourWidget.SetRepresentation(self._representation)
        self._contourWidget.AddObserver("InteractionEvent", self._onInteractAction)
        self._contourWidget.AddObserver("EndInteractionEvent", self._endIteractAction)
        if isinstance(self._scene, VtkImagePlane):
            self._startEvent = self._scene.addObserver("MouseMoveEvent", self._start)
            if scene.planeOrientation == VtkImagePlane.PLANE_ORIENTATION_CORONAL or scene.planeOrientation == VtkImagePlane.PLANE_ORIENTATION_PANORAMIC_SLICE:
                self._showLine = False
                self._representation.GetProperty().SetOpacity(0.0)
                self._representation.GetLinesProperty().SetOpacity (0.0)
                self._representation.GetActiveProperty().SetOpacity (0.0)
        else:
            self._startEvent = -1
        
    
    @property    
    def representation(self):
        logging.debug("In Contour::contourWidget.getter()")
        return self._representation
    
    @property    
    def contourWidget(self):
        logging.debug("In Contour::contourWidget.getter()")
        return self._contourWidget
    
    @property    
    def scene(self):
        logging.debug("In Contour::scene.getter()")
        return self._scene
    
    @property    
    def replyList(self):
        logging.debug("In Contour::replyList.getter()")
        return self._replyList
    
    @replyList.setter    
    def replyList(self, replyList):
        logging.debug("In Contour::replyList.setter()")
        self._replyList = replyList
    
    @property
    def visible(self):
        logging.debug("In Contour::visible.getter()")
        return self._visible  
        
    @visible.setter   
    def visible(self, value):
        logging.debug("In Contour::visible.setter()")
        if self._tubeActor:
            self._tubeActor.SetVisibility(value)
            self._contourWidget.SetEnabled(value)
            self._scene.window.Render()
        self._visible  = value
    
    def delete(self):
        logging.debug("In Contour::delete()")
        self._contourWidget.Off()
        self.removeStartEvent()
        if self._tubeActor: 
            self._scene.renderer.RemoveActor(self._tubeActor)
        self._scene.window.Render()
        self._tubeActor = None
        self._tubeFilter = None
    
    def _createCutter(self):
        logging.debug("In Contour::_createCutter()")
        if isinstance(self._scene, VtkImagePlane) \
          or isinstance(self._scene, VtkMultiSliceImagePlane) \
          or isinstance(self._scene, VtkSliceImagePlane):
            self._cutter = vtk.vtkCutter()
            self._cutter.SetCutFunction(self._scene.planeCutter)
            self._cutter.GenerateCutScalarsOn()
        else:
            self._cutter = None

    def _createTube(self):
        logging.debug("In Contour::createTube()")
        path = self._representation.GetContourRepresentationAsPolyData()
        lines = path.GetLines()
        
        points = vtk.vtkPoints()
        for cellIdx in range(lines.GetNumberOfCells()):
            cell = path.GetCell(cellIdx)
            
            npts = 0
            pts = vtk.vtkIdList()
            path.GetCellPoints(npts, pts)
            
            for i in range(pts.GetNumberOfIds()):
                pt0 = path.GetPoints().GetPoint(pts.GetId(i))
                points.InsertNextPoint(pt0)
                   
        self._parametricSpline = vtk.vtkParametricSpline()
        self._parametricSpline.SetPoints(points)
        
        self._parametricFuntionSource = vtk.vtkParametricFunctionSource()
        self._parametricFuntionSource.SetParametricFunction(self._parametricSpline)
        self._parametricFuntionSource.SetUResolution(100)
        
        self._tubeFilter = vtk.vtkTubeFilter()
        self._tubeFilter.SetNumberOfSides(100)
        self._tubeFilter.SetRadius(self._radius)
        self._tubeFilter.SetInputConnection(self._parametricFuntionSource.GetOutputPort())
        
        if self._cutter:
            self._cutter.SetInputConnection(self._tubeFilter.GetOutputPort())
            self._cutter.Update()
                                                
            cube = vtk.vtkBox()
            cube.SetBounds(self._scene.imagedata.GetBounds())
            clip = vtk.vtkClipPolyData()
            clip.SetClipFunction(cube)
            clip.SetInputConnection(self._cutter.GetOutputPort())
            clip.InsideOutOn()
            clip.Update()          
            
            tubeMapper=vtk.vtkPolyDataMapper()
            tubeMapper.ScalarVisibilityOff()
            tubeMapper.SetInputConnection(clip.GetOutputPort())
            tubeMapper.GlobalImmediateModeRenderingOn()
            
            self._tubeActor = vtk.vtkActor()
            self._tubeActor.SetMapper(tubeMapper)
            self._tubeActor.GetProperty().LightingOff()
            self._tubeActor.GetProperty().SetColor(self._lineColor)
        else:
            cube = vtk.vtkBox()
            cube.SetBounds(self._scene.volume.GetBounds())
            clip = vtk.vtkClipPolyData()
            clip.SetClipFunction(cube)
            clip.SetInputConnection(self._tubeFilter.GetOutputPort())
            clip.InsideOutOn()
            clip.Update() 
            tubeMapper = vtk.vtkPolyDataMapper()
            tubeMapper.SetInputConnection(clip.GetOutputPort())
        
            self._tubeActor = vtk.vtkActor()
            self._tubeActor.SetMapper(tubeMapper)
            self._tubeActor.GetProperty().SetColor(self._lineColor)
        
        self._scene.renderer.AddActor(self._tubeActor)

    def removeStartEvent(self):
        logging.debug("In Contour::removeStartEvent()")
        self._scene.removeObserver(self._startEvent)
        self._started = True

    def _onInteractAction(self, obj, evt):
        logging.debug("In Contour::onInteractAction()")
        if self._representation.GetCurrentOperation() == 0:
            (X, Y) = self._scene.interactor.GetEventPosition()
            self._scene.picker.Pick(X, Y, 0, self._scene.renderer)
            q = list(self._scene.picker.GetPickPosition())
            (px, py, pz) = q 
            self._representation.SetNthNodeWorldPosition(self._representation.GetNumberOfNodes()-1, [px, py, pz])
            self._reply()
        if self._representation.GetNumberOfNodes() >= 2:
            if self._tubeActor:
                self._updateTube()
            else:
                self._createTube()
                if isinstance(self._scene, VtkImagePlane):
                    self.removeStartEvent()
                for contour in self._replyList:
                    if isinstance(contour.scene, VtkImagePlane):
                        contour.removeStartEvent()
                
    
    def _endIteractAction(self, obj, evt):
        logging.debug("In Contour::_endIteractAction()")
        self._reply()
    
    def _updateTube(self):
        logging.debug("In Contour::_updateTube()")
        path = self._representation.GetContourRepresentationAsPolyData()
        lines = path.GetLines()
        points = vtk.vtkPoints()
        for cellIdx in range(lines.GetNumberOfCells()):
            npts = 0
            pts = vtk.vtkIdList()
            path.GetCellPoints(npts, pts)
            
            for i in range(pts.GetNumberOfIds()):
                pt0 = path.GetPoints().GetPoint(pts.GetId(i))
                points.InsertNextPoint(pt0)
                   
        self._parametricSpline.SetPoints(points)
            
    def getPropertiesFromMark(self, mark):
        logging.debug("In Contour::getPropertiesFromMark()")
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
        while i < len(pts):
            addPosition = list(self._scene.fromOriginalView(pts[i]))
            self._representation.SetNthNodeWorldPosition(i, addPosition)
            i = i + 1

        if self._representation.GetNumberOfNodes() >= 2:
            if self._tubeActor:
                self._updateTube()
            else:
                self._createTube()
        
        self._scene.window.Render()

    def _start(self, obj, evt):
        logging.debug("In Contour::start()")
        if not self._contourWidget.GetEnabled() and self._visible:
            self._contourWidget.On()

    def _reply(self):
        logging.debug("In Contour::_reply()")
        for mark in self._replyList:
            mark.getPropertiesFromMark(self)
    
    @property
    def lineColor(self):
        logging.debug("In Contour::lineColor.getter()")
        return self._lineColor
    
    @lineColor.setter 
    def lineColor(self, lineColor):
        logging.debug("In Contour::lineColor.setter")
        self._lineColor = lineColor
        self._representation.GetLinesProperty().SetColor(self._lineColor)
        self._tubeActor.GetProperty().SetColor(self._lineColor)
        self.scene.window.Render()

    @property
    def radius(self):
        logging.debug("In Contour::radius.getter()")
        return self._radius
    
    @radius.setter
    def radius(self, radius):
        logging.debug("In Contour::radius.setter()")
        self._radius = radius
        if self._tubeFilter:
            self._tubeFilter.SetRadius(radius)
            self.scene.window.Render()
    
    def lock(self):
        logging.debug("In Contour::lock()")
        self._contourWidget.ProcessEventsOff()
        if self._showLine:
            self._representation.GetProperty().SetOpacity(0.0)
            self._representation.GetLinesProperty().SetOpacity (0.0)
        for contour in self._replyList:
            if contour._showLine:
                contour.representation.GetProperty().SetOpacity(0.0)
                contour.representation.GetLinesProperty().SetOpacity (0.0)
            contour.contourWidget.ProcessEventsOff()
            contour.scene.window.Render()
        self._scene.window.Render()
    
    def unlock(self):
        logging.debug("In Contour::unlock()")
        self._contourWidget.ProcessEventsOn()
        if self._showLine:
            self._representation.GetProperty().SetOpacity(1)
            self._representation.GetLinesProperty().SetOpacity (1)
        for contour in self._replyList:
            if contour._showLine:
                contour.representation.GetProperty().SetOpacity(1)
            contour.contourWidget.ProcessEventsOn()
            contour.scene.window.Render()
        self._scene.window.Render() 
    
    @property    
    def locked(self):
        logging.debug("In Contour::getLocked()")
        return not self._contourWidget.GetProcessEvents()            
    
    def save(self):
        logging.debug("In Contour::save()")
        yaml = {}
        yaml["lineColor"] = self._lineColor
        yaml["visible"] = self._visible
        yaml["locked"] = True
        yaml["radius"] = self.radius
        points = []
        i = 0
        while i < self._representation.GetNumberOfNodes():
            addPosition = [0,0,0]
            self._representation.GetNthNodeWorldPosition(i, addPosition)
            addPosition = list(self._scene.toOriginalView(addPosition)) 
            points.append(addPosition)
            i = i + 1
        yaml["points"] = points
        return yaml
    
    def loadPoints(self, points):
        logging.debug("In Contour::loadPoints()")
        for point in points: 
            self._addPoint(self._scene.fromOriginalView(point))
        
        self._reply()
        
        if self._representation.GetNumberOfNodes() >= 2:
            if self._tubeActor:
                self._updateTube()
            else:
                self._createTube()
                if isinstance(self._scene, VtkImagePlane):
                    self.removeStartEvent()
                for contour in self._replyList:
                    if isinstance(contour.scene, VtkImagePlane):
                        contour.removeStartEvent()
                
        self._scene.window.Render()
    
    def _addPoint(self, point):
        logging.debug("In Contour::addPoint()")
        i = self._representation.GetNumberOfNodes()
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
        i = self._representation.GetNumberOfNodes()
        self._representation.SetNthNodeWorldPosition(i-1, point)
        i = i + 1

    def addScene(self, scene):
        logging.debug("In Contour::addScene()")
        if isinstance(scene, VtkMultiSliceImagePlane):
            from multislicecontour import MultiSliceContour
            contour = MultiSliceContour(scene)
        else:
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
            addPosition = list(self._scene.toOriginalView(addPosition)) 
            points.append(addPosition)
            i = i + 1
        
        contour.loadPoints(points)
        
        contour.lineColor = self._lineColor
        contour.visible = self._visible
        if self.locked:
            contour.lock()
        else:
            contour.unlock()
        contour.radius = self.radius
        
    def removeScenePlugin(self, scenePlugin):
        logging.debug("In Contour::removeScenePlugin()")
        if self._replyList.count(scenePlugin) > 0:
            self._replyList.remove(scenePlugin)
             
    @property
    def started(self):
        return self._started
    
    @property 
    def originalPoints(self):
        i = 0    
        result = []
        while i < self._representation.GetNumberOfNodes():
            addPosition = [0,0,0]
            self._representation.GetNthNodeWorldPosition(i, addPosition)
            addPosition = list(self._scene.toOriginalView(addPosition))
            result.append(addPosition)
            i = i+1
        return result
            
             
