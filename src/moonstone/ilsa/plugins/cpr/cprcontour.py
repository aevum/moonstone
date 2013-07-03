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

import vtk
from ....bloodstone.scenes.imageplane import VtkImagePlane
from ....bloodstone.scenes.data.slice import Slice
from ....bloodstone.utils.msmath import intersect_line_with_plane, distance_from_plane

class CPRContour(object):

    def __init__(self, scenes, ilsa, onCloseAction):
        logging.debug("In CPRContour::__init__()")
        self._onCloseAction = onCloseAction
        self._panoramicPlane = None
        self._transversalPlane = None
        
        self._scene = None
        self.contourRep = vtk.vtkOrientedGlyphContourRepresentation()
        self.contourRep.GetLinesProperty().SetColor(1,1,1)
        self.contourRep.SetLineInterpolator(vtk.vtkLinearContourLineInterpolator())
        self.visible = True
        
        self.actualContourRep = vtk.vtkOrientedGlyphContourRepresentation()
        self.actualContourRep.GetLinesProperty().SetColor(0,1,0)
        self.actualContourRep.SetLineInterpolator(vtk.vtkLinearContourLineInterpolator())
        
        self.actualContourWidget = vtk.vtkContourWidget()
        self.actualContourWidget.SetRepresentation(self.actualContourRep)
        
        self.transversalContourRep = vtk.vtkOrientedGlyphContourRepresentation()
        self.transversalContourRep.GetLinesProperty().SetColor(0,1,0)
        self.transversalContourRep.SetLineInterpolator(vtk.vtkLinearContourLineInterpolator())
        
        self.transversalContourWidget = vtk.vtkContourWidget()
        self.transversalContourWidget.SetRepresentation(self.transversalContourRep)
        
        self.replyList = []
        self.numberOfNodes = 0
        self.contourWidget = vtk.vtkContourWidget()
        self._started = False
        self._closed = False
        self.sceneEvents = {}
        self._ilsa = ilsa
        axialScenes = []
        for scene in scenes:
            if isinstance(scene, VtkImagePlane):
                if scene.planeOrientation == scene.PLANE_ORIENTATION_AXIAL:
                    axialScenes.append(scene)
        self.scenes = axialScenes
        self.addEvents()
        self.pointColor = (0, 1, 0)
        self.lineColor = (1, 1, 1)
        self.actualLineColor = (0, 1, 0)
        self.transversalSize = 30.0
        self.lastNormal = None
    
          
    def delete(self):
        logging.debug("In CPRContour::delete()")
        self.contourWidget.Off()
        self.actualContourWidget.Off()
        self.transversalContourWidget.Off()
        if self._panoramicPlane:
            self._panoramicPlane.scene.removeSliceChangeListener(self.panoramicSliceChange)
            self._panoramicPlane.scene.decrementReferenceCount()
            if self._panoramicPlane.scene.referenceCount < 1:
                if self._panoramicPlane.mscreenParent.removeScene(self._scene):
                    self._panoramicPlane.notifyCloseListeners()
                    self._panoramicPlane.close()
            self._panoramicPlane = None
        if self._transversalPlane:
            self._transversalPlane.scene.removeSliceChangeListener(self.transversalSliceChange)
            self._transversalPlane.scene.decrementReferenceCount()
            if self._transversalPlane.scene.referenceCount < 1:
                if  self._transversalPlane.mscreenParent.removeScene(self.scene):
                    self._transversalPlane.notifyCloseListeners()
                    self._transversalPlane.close()
            self._transversalPlane = None
        self.removeEvents()
        if self._scene:
            self._scene.decrementReferenceCount()
            self._scene.removeSliceChangeListener(self.sceneChangeListener)
            self._scene.getPlane().mscreenParent.decrementReferenceCount()
            self._scene.window.Render()    

    def removeEvents(self):
        logging.debug("In CPRContour::removeEvents()")
        for sceneKey, events in self.sceneEvents.items():
            sceneKey.removeObserver(events[0])
            sceneKey.removeObserver(events[1])
        self.sceneEvents.clear()
            
    def addEvents(self):
        if not self._closed:
            if self._scene:
                self.sceneEvents[self._scene] = [
                                self._scene.addObserver("RightButtonReleaseEvent",  lambda o, e, i=self._scene: self.clickEvent(o, e, i)),
                                self._scene.addObserver("LeftButtonPressEvent",  lambda o, e, i=self._scene: self.clickEvent(o, e, i))
                            ]
            else:
                for scene in self.scenes:
                    if isinstance(scene, VtkImagePlane):
                        self.sceneEvents[scene] = [
                                scene.addObserver("RightButtonReleaseEvent",  lambda o, e, i=scene: self.clickEvent(o, e, i)),
                                scene.addObserver("LeftButtonPressEvent",  lambda o, e, i=scene: self.clickEvent(o, e, i))
                            ]
                    

    def setReplyList(self, list):
        logging.debug("In CPRContour::setReplyList()")
        self.replyList = list
        
    def onInteractAction(self, obj, evt):
        logging.debug("In CPRContour::onInteractAction()")        
    
    def endIteractAction(self, obj, evt):
        logging.debug("In CPRContour::endIteractAction()")
        self.createCPRImage()

    def setPanoramicPlane(self, panoramicPlane):
        self._panoramicPlane = panoramicPlane
        self._panoramicPlane.scene.incrementReferenceCount()
        self._panoramicPlane.scene.addSliceChangeListener(self.panoramicSliceChange)
        self.panoramicSliceChange(self._panoramicPlane)
        
        
    def setTransversalPlane(self, transversalPlane):
        self._transversalPlane = transversalPlane
        self._transversalPlane.scene.incrementReferenceCount()
        self._transversalPlane.scene.addSliceChangeListener(self.transversalSliceChange)
        self.transversalSliceChange(self._transversalPlane.scene)

    @property
    def scene(self):
        return self._scene

    @scene.setter
    def scene(self, scene):
        self._scene = scene
        self._scene.incrementReferenceCount()
        self._scene.getPlane().mscreenParent.incrementReferenceCount()
        for sceneKey, events in self.sceneEvents.items():
            if sceneKey != scene:
                sceneKey.removeObserver(events[0])
                sceneKey.removeObserver(events[1])
        self.sceneEvents = {scene:self.sceneEvents[scene]}
        self.contourWidget = vtk.vtkContourWidget()
        self.contourWidget.SetRepresentation(self.contourRep)
        self.contourWidget.AddObserver("InteractionEvent", self.onInteractAction)
        self.contourWidget.AddObserver("EndInteractionEvent", self.endIteractAction)
        
        self.contourWidget.SetInteractor(self._scene.interactor)
        self.actualContourWidget.SetInteractor(self._scene.interactor)
        self.transversalContourWidget.SetInteractor(self._scene.interactor)
        self.contourWidget.On()

    def clickEvent(self, obj, evt, scene):
        logging.debug("In CPRContour::start()")
        if not self._closed:
            if not self._started:
                self.scene = scene
                self._started = True
                (X, Y) = self._scene.interactor.GetEventPosition()
                self._scene.picker.Pick(X, Y, 0, self._scene.renderer)
                q = list(self._scene.picker.GetPickPosition())
                self.addPoint(q)
#            else:
            (X, Y) = self._scene.interactor.GetEventPosition()
            self._scene.picker.Pick(X, Y, 0, self._scene.renderer)
            q = list(self._scene.picker.GetPickPosition())
            self.addPoint(q)
            self._scene.window.Render()
            
#        self.contourRep.
        if evt == "RightButtonReleaseEvent":
            if self.contourRep.GetNumberOfNodes() < 3:
                evt
                return
            self ._closed = True
            self.removeEvents()
            self._scene.interactorStyle.OnRightButtonUp()
            self.createCPRImage()
            self._onCloseAction()
            # http://github.com/jeromevelut/Chiron/blob/Chiron-PoC/Algorithms/vtkFrenetSerretFrame.cxx

    def createCPRImage(self):        

        corners = self._scene.getPlane().getScreen().cubeCorners
        
        points = []
        i = 0
        while i < self.contourRep.GetNumberOfNodes():
            addPosition = [0,0,0]
            self.contourRep.GetNthNodeWorldPosition(i, addPosition)
            points.append(addPosition)
            i = i+1
            
        planeSource = self._scene.planeSource
        newPoints = []
        for p in points:
            newPoints.append(intersect_line_with_plane(p, [p + n for p, n in zip (p, planeSource.GetNormal())], planeSource.GetNormal(), planeSource.GetOrigin()))
            
        points = newPoints
        
        center = [(a + b) / 2.0 for a, b in zip(corners[0], corners[7])]
    
        pb = corners[0]
        pt = corners[7]
        
        if pb[2] > pt[2]:
            aux = pb 
            pb = pt 
            pt = aux 
        height = math.sqrt(vtk.vtkMath.Distance2BetweenPoints(intersect_line_with_plane(center, [pp + n for pp, n in zip (center, planeSource.GetNormal())], planeSource.GetNormal(), pb),
                                                              intersect_line_with_plane(center, [pp + n for pp, n in zip (center, planeSource.GetNormal())], planeSource.GetNormal(), pt)))
        slices = []
        pt0 = points[0]
        for i in range(1,len(points)):
            pt1 = points[i]
            if pt0 == pt1:
                continue
            width = math.sqrt(vtk.vtkMath.Distance2BetweenPoints(pt0, pt1))
            plane = vtk.vtkPlaneSource()
            orig = intersect_line_with_plane(pt0, [p1 + n for p1, n in zip (pt0, planeSource.GetNormal())], planeSource.GetNormal(), pb)
            plane.SetPoint1(intersect_line_with_plane(pt1, [p1 + n for p1, n in zip (pt1, planeSource.GetNormal())], planeSource.GetNormal(), pb))
            plane.SetPoint2(intersect_line_with_plane(pt0, [p1 + n for p1, n in zip (pt0, planeSource.GetNormal())], planeSource.GetNormal(), pt))
            plane.SetOrigin(orig)
            plane.Update()
            slices.append(Slice(plane.GetOrigin(), plane.GetPoint1(), plane.GetPoint2(), width, height))    
            pt0 = pt1
        
        pi = points[len(points) / 2 - 1]
        pf = points[len(points) / 2]
        tNormal = [(p2 - p1) / 2.0 for p1, p2 in zip(pi, pf)]
        tOrigin = [(p2 + p1) / 2.0 for p1, p2 in zip(pi, pf)]
        tOrigin = intersect_line_with_plane(tOrigin, [p1 + n for p1, n in zip (tOrigin, planeSource.GetNormal())], planeSource.GetNormal(), center)
        tp1 = [0,0,0]
        vtk.vtkMath.Cross(tNormal, planeSource.GetNormal(),tp1)
        tp1 = intersect_line_with_plane(tp1, [p1 + n for p1, n in zip (tp1, planeSource.GetNormal())], planeSource.GetNormal(), tOrigin)
        tp2 = [p1 -p2 for p1, p2 in zip(tOrigin, planeSource.GetNormal())]
        
        tPlane = vtk.vtkPlaneSource()
        tPlane.SetOrigin(tOrigin)
        tPlane.SetPoint1(tp1)
        tPlane.SetPoint2(tp2)
        self.normalizePlaneSize(tPlane, self.transversalSize, height) 
        tPlane.SetCenter(tOrigin)
                        
        tSlice = Slice(tPlane.GetOrigin(), tPlane.GetPoint1(), tPlane.GetPoint2(), self.transversalSize, height)
        
        tPathPoints = []
        for p in points:
            tPathPoints.append(intersect_line_with_plane(p, [p + n for p, n in zip (p, planeSource.GetNormal())], planeSource.GetNormal(), center))
        
        if self._panoramicPlane == None:
            self.setPanoramicPlane(self._scene.getPlane().getScreen().createScene(-2, slices = slices, resize=False))
            self.setTransversalPlane(self._scene.getPlane().getScreen().createScene(-3, slices = tSlice, data={"path": tPathPoints} ))
            self._scene.addSliceChangeListener(self.sceneChangeListener)
        else:
            self._transversalPlane.updateSliceAndPath(tSlice, tPathPoints)
            self._panoramicPlane.updateSlices(slices)
            self._panoramicPlane.scene.window.Render()
            self._transversalPlane.scene.window.Render()
            
        self.lastNormal = planeSource.GetNormal()
        self._scene.window.Render()
        

    def normalizePlaneSize(self, plane, width, height):
        distance = math.sqrt(vtk.vtkMath.Distance2BetweenPoints(plane.GetOrigin(), plane.GetPoint1()))
        scale = width/distance
        plane.SetPoint1([(p1 - o) * scale + o for p1, o in zip(plane.GetPoint1(), plane.GetOrigin())])
        
        distance = math.sqrt(vtk.vtkMath.Distance2BetweenPoints(plane.GetOrigin(), plane.GetPoint2()))
        scale = height/distance
        plane.SetPoint2([(p2 - o) * scale + o for p2, o in zip(plane.GetPoint2(), plane.GetOrigin())])
        
        plane.SetOrigin(plane.GetOrigin())
        
        plane.Update()
        
    def sceneChangeListener(self, scene=None):
        self.panoramicSliceChange(self._panoramicPlane.scene, render=False)
        self.transversalSliceChange(self._transversalPlane.scene, render=False)
        
        planeSource = self._scene.planeSource
        
        i = 0
        while i < self.contourRep.GetNumberOfNodes():
            addPosition = [0,0,0]
            self.contourRep.GetNthNodeWorldPosition(i, addPosition)
            self.contourRep.SetNthNodeWorldPosition(i, intersect_line_with_plane(addPosition, [p + n for p, n in zip (addPosition, planeSource.GetNormal())], planeSource.GetNormal(), planeSource.GetOrigin()))
            i = i+1
        if self.lastNormal:
            m = 0
            for l, a in zip(self.lastNormal, planeSource.GetNormal()):
                m = max(m, abs(l - a))
            if m > 0.0001:
                self.createCPRImage()   
        
            
    def panoramicSliceChange(self, scene= None, render = True):
        slices = scene.slice
        if not slices:
            return
        
        self.actualContourWidget.On()
        planeSource = self._scene.planeSource
        self.actualContourRep.ClearAllNodes()
        pd = vtk.vtkPolyData()
        points = vtk.vtkPoints()
        points.InsertPoint(0, 0, 0 ,0)
        pd.SetLines(vtk.vtkCellArray())
        pd.SetPoints(points)
        #self.clickEvent(None, None)
        self.actualContourWidget.Initialize(pd, 1)
        self.actualContourRep.SetNthNodeWorldPosition(0, 
                   intersect_line_with_plane(slices[0].plane.GetOrigin(), [p1 + n for p1, n in zip (slices[0].plane.GetOrigin(), planeSource.GetNormal())], planeSource.GetNormal(), planeSource.GetOrigin()))
        for slice in slices:
            self.actualContourRep.AddNodeAtWorldPosition([0 , 0, 0])
            i = self.actualContourRep.GetNumberOfNodes()
            self.actualContourRep.SetNthNodeWorldPosition(i-1, intersect_line_with_plane(slice.plane.GetPoint1(), [p1 + n for p1, n in zip (slice.plane.GetPoint1(), planeSource.GetNormal())], planeSource.GetNormal(), planeSource.GetOrigin()))
            
#        self.actualContourWidget.SetInteractor(self._scene.interactor)
        self.actualContourWidget.ProcessEventsOff()
        self.actualContourWidget.SetEnabled(self.visible)
        if render:
            self._scene.window.Render()
    
    def transversalSliceChange(self, scene= None, render = True):
        slice = scene.slice
        if not slice:
            return
        
        self.transversalContourWidget.On()
        planeSource = self._scene.planeSource
        self.transversalContourRep.ClearAllNodes()
        pd = vtk.vtkPolyData()
        points = vtk.vtkPoints()
        points.InsertPoint(0, 0, 0 ,0)
        pd.SetLines(vtk.vtkCellArray())
        pd.SetPoints(points)
        #self.clickEvent(None, None)
        self.transversalContourWidget.Initialize(pd, 1)
        self.transversalContourRep.SetNthNodeWorldPosition(0, 
                   intersect_line_with_plane(slice.plane.GetOrigin(), [p1 + n for p1, n in zip (slice.plane.GetOrigin(), planeSource.GetNormal())], planeSource.GetNormal(), planeSource.GetOrigin()))
        self.transversalContourRep.AddNodeAtWorldPosition([0 , 0, 0])
        i = self.transversalContourRep.GetNumberOfNodes()
        self.transversalContourRep.SetNthNodeWorldPosition(i-1, intersect_line_with_plane(slice.plane.GetPoint1(), [p1 + n for p1, n in zip (slice.plane.GetPoint1(), planeSource.GetNormal())], planeSource.GetNormal(), planeSource.GetOrigin()))
            
#        self.actualContourWidget.SetInteractor(self._scene.interactor)
        self.transversalContourWidget.ProcessEventsOff()
        self.transversalContourWidget.SetEnabled(self.visible)
        if render:
            self._scene.window.Render()
            
    def setRepresentationTo3D(self):
        logging.debug("In CPRContour::setRepresentationTo3D()")
        contourRep = vtk.vtkOrientedGlyphContourRepresentation()
        self.SetRepresentation(contourRep)

    def setRepresentationTo2D(self):
        logging.debug("In CPRContour::setRepresentationTo2D()")
        contourRep = vtk.vtkOrientedGlyphContourRepresentation()
        self.SetRepresentation(contourRep)

    def setPointColor(self, red, green, blue):
        logging.debug("In CPRContour::setPointColor()")
        self.pointColor = (red, green, blue)
        self.contourRep.GetProperty().SetColor(self.pointColor)

    def setLineColor(self, red, green, blue):
        logging.debug("In CPRContour::setLineColor()")
        self.lineColor = (red, green, blue)
        self.contourRep.GetLinesProperty().SetColor(self.lineColor)
        if self._scene:
            self._scene.window.Render()
    
    def setActualLineColor(self, red, green, blue):
        logging.debug("In CPRContour::setLineColor()")
        self.actualLineColor = (red, green, blue)
        self.actualContourRep.GetLinesProperty().SetColor(self.actualLineColor)
        self.transversalContourRep.GetLinesProperty().SetColor(self.actualLineColor)
        if self._scene:
            self._scene.window.Render()
            
    def setTransversalSize(self, size):
        logging.debug("In CPRContour::setLineColor()")
        self.transversalSize = size
        if self._transversalPlane:
            self._transversalPlane.scene.slice.setWidth(size)
            self._transversalPlane.scene.slicePosition = self._transversalPlane.scene.actualPosition 
        self._scene.window.Render()
        
    def getFontColor(self):
        logging.debug("In CPRContour::getFontColor()")
        return self.fontColor

    def getLineColor(self):
        logging.debug("In CPRContour::getLineColor()")
        return self.lineColor
    
    def getActualLineColor(self):
        logging.debug("In CPRContour::getActualLineColor()")
        return self.actualLineColor
    
    def getTransversalSize(self):
        logging.debug("In CPRContour::getTransversalLineColor()")
        return self.transversalSize

    def getPointColor(self):
        logging.debug("In CPRContour::getPointColor()")
        return self.pointColor

    def getReplyList(self):
        logging.debug("In CPRContour::getReplyList()")
        return self.replyList
    
    def lock(self):
        logging.debug("In CPRContour::lock()")
        self.contourWidget.ProcessEventsOff()
        self.contourWidget.SetEnabled(False)
        self.removeEvents()
        if self._scene:
            self._scene.window.Render() 
    
    def unlock(self):
        logging.debug("In CPRContour::unlock()")
        self.addEvents()
        self.contourWidget.ProcessEventsOn()
        self.contourWidget.SetEnabled(self.visible)
        self.contourRep.GetProperty().SetOpacity(1)
        self.contourRep.GetLinesProperty().SetOpacity (1)
        for contour in self.replyList:
            contour.contourRep.GetProperty().SetOpacity(1)
            contour.contourRep.GetLinesProperty().SetOpacity (1)
            contour.ProcessEventsOn()
            if contour._scene:
                contour._scene.window.Render()
        if self._scene:
            self._scene.window.Render() 
        
    def getLocked(self):
        logging.debug("In CPRContour::getLocked()")
        return not self.contourWidget.GetProcessEvents()
    
    def setVisible(self, value):
        logging.debug("In CPRContour::setVisible()")
        self.visible = value
        self.contourWidget.SetEnabled(value)
        self.actualContourWidget.SetEnabled(value)
        self.transversalContourWidget.SetEnabled(value)
        self._scene.window.Render()
        for contour in self.replyList:
            contour.visible = value
            contour.SetEnabled(value)
            contour._scene.window.Render()
            
    def getClosed(self):
        return self._closed

    def getVisible(self):
        logging.debug("In CPRContour::getVisible()")
        return self.visible
    
    def save(self):
        logging.debug("In CPRContour::save()")
        yaml = {}
        yaml["lineColor"] = self.getLineColor()
        yaml["actualLineColor"] = self.getActualLineColor()
        yaml["transversalSize"] = self.getTransversalSize()
        yaml["visible"] = self.getVisible()
        yaml["locked"] = self.getLocked()
        yaml["sceneId"] = self._scene.id
        yaml["panoramicSceneId"] = self._panoramicPlane.scene.id
        yaml["transversalSceneId"] = self._transversalPlane.scene.id
        points = []
        i = 0
        while i < self.contourRep.GetNumberOfNodes():
            addPosition = [0,0,0]
            self.contourRep.GetNthNodeWorldPosition(i, addPosition) 
            points.append(addPosition)
            i = i + 1
        yaml["points"] = points
        return yaml
    
    def loadPoints(self, points):
        logging.debug("In CPRContour::loadPoints()")
        for point in points: 
            self.addPoint(point)
        self._closed = True
        self.removeEvents()
        self._scene.window.Render()
    
    def addPoint(self, point):
        logging.debug("In CPRContour::addPoint()")
        i = self.contourRep.GetNumberOfNodes()
        if i == 0:
            pd = vtk.vtkPolyData()
            points = vtk.vtkPoints()
            points.InsertPoint(0, 0, 0 ,0)
            pd.SetLines(vtk.vtkCellArray())
            pd.SetPoints(points)
            #self.clickEvent(None, None)
            self.contourWidget.Initialize(pd, 1)
        else:
            if i == 2:
                #working around the workaround to fix sucide bug adding first point o.O :D 
                p0 = [0,0,0]
                self.contourRep.GetNthNodeWorldPosition(0, p0)
                p1 = [0,0,0]
                self.contourRep.GetNthNodeWorldPosition(1, p1)
                if p0 != p1:
                    self.contourRep.AddNodeAtWorldPosition([0 , 0, 0])
            else:
                self.contourRep.AddNodeAtWorldPosition([0 , 0, 0])
        i = self.contourRep.GetNumberOfNodes()
        self.contourRep.SetNthNodeWorldPosition(i-1, point)

    def addScene(self, scene):
        logging.debug("In CPRContour::addScene()")
        
    def removeScenePlugin(self, scenePlugin):
        logging.debug("In CPRContour::removeScenePlugin()")
        try:
            if self.scenes:
                self.scenes
        except:
            logging.warning("Scene does not exists")