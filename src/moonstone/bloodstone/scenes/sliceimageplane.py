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
import sys
import math
from PySide import QtGui

from data.imagedata import VtkImageData
from ..utils.msmath import intersect_line_with_plane
from imageplane import VtkImagePlane

class VtkSliceImagePlane(VtkImageData, VtkImagePlane):
    def __init__(self, vtkInteractor, parent, planeOrientarion = VtkImagePlane.PLANE_ORIENTATION_AXIAL):
        logging.debug("In VtkSliceImagePlane::__init__()")
        super(VtkSliceImagePlane, self).__init__(vtkInteractor)        
        self._firstUpdate = True
        self._parent = parent
        self._planeOrientation = planeOrientarion
        self._referenceCount = 0
        self._planeFactor = 1.0
        self._restrictPlaneToVolume = True
        self._originalWindow = 1.0
        self._originalLevel = 0.5
        self._currentWindow = 1.0
        self._currentLevel = 0.5
        self._textureInterpolate = True
        self._resliceInterpolate = vtk.VTK_LINEAR_INTERPOLATION
        self._userControlledLookupTable = False
        self._displayText = False
        self._currentCursorPosition = [0, 0, 0]
        self._currentImageValue = vtk.VTK_DOUBLE_MAX
        self._marginSelectMode = 8
        self._userContinuousCursor = False
        self._marginSizeX = 0.05
        self._marginSizeY = 0.05
        self._slabThickness = 0.0
        self._slabSpacing = [.4, .4, .4]
        self.actualPosition = 0
        
        # Represent the plane's outline
        self._planeSource = vtk.vtkPlaneSource()
        self._planeSource.SetXResolution(1)
        self._planeSource.SetYResolution(1)
        self._planeOutlinePolyData = vtk.vtkPolyData()
        self._planeOutlineActor = vtk.vtkActor()
        
        # Represent the resliced image plane
        self._colorMap = vtk.vtkImageMapToColors()
        self._reslice = vtk.vtkImageReslice()
        self._reslice.TransformInputSamplingOff()
        self._resliceAxes = vtk.vtkMatrix4x4()
        self._texture = vtk.vtkTexture()
        self._texturePlaneActor = vtk.vtkActor()
        self._texturePlaneActorColor = self.getBorderColor()
        self._texturePlaneWidgetActor = vtk.vtkActor()
        self._textureLineWidgetActor = vtk.vtkActor()
        self._transform = vtk.vtkTransform()
        self._resliceTransform = None
        self._imageData = None
        self._lookupTable = None
        self._planeCutter = vtk.vtkPlane()
        
        # Represent the cross hair cursor
        self._cursorPolyData = vtk.vtkPolyData()
        self._cursorActor = vtk.vtkActor()

        # Represent the oblique positioning margins
        self._marginPolyData = vtk.vtkPolyData()
        self._marginActor = vtk.vtkActor()
        
        # Represent the text: annotation for cursor position and W/L
        self._topLeftTextProperty = vtk.vtkTextProperty()
        self._topLeftTextProperty.SetFontSize(12)
        self._topLeftTextProperty.SetFontFamilyToArial()
        self._topLeftTextProperty.BoldOff()
        self._topLeftTextProperty.ItalicOff()
        self._topLeftTextProperty.SetJustificationToLeft()
        self._topLeftTextProperty.SetVerticalJustificationToBottom()
        self._topLeftTextProperty.SetColor(1.0, 1.0, 1.0)
        
        self._topLeftTextMapper = vtk.vtkTextMapper()
        self._topLeftTextMapper.SetTextProperty(self._topLeftTextProperty)
        
        self._topLeftTextActor = vtk.vtkActor2D()
        self._topLeftTextActor.SetMapper(self._topLeftTextMapper)
        self._topLeftTextActor.GetPositionCoordinate(). \
                                    SetCoordinateSystemToNormalizedDisplay()
        self._topLeftTextActor.GetPositionCoordinate().SetValue(0.04, 0.95)
        
        self._bottomLeftTextProperty = vtk.vtkTextProperty()
        self._bottomLeftTextProperty.SetFontSize(12)
        self._bottomLeftTextProperty.SetFontFamilyToArial()
        self._bottomLeftTextProperty.BoldOff()
        self._bottomLeftTextProperty.ItalicOff()
        self._bottomLeftTextProperty.SetJustificationToLeft()
        self._bottomLeftTextProperty.SetVerticalJustificationToTop()
        self._bottomLeftTextProperty.SetColor(1.0, 1.0, 1.0)
        
        self._bottomLeftTextMapper = vtk.vtkTextMapper()
        self._bottomLeftTextMapper.SetTextProperty(self._bottomLeftTextProperty)
        
        self._bottomLeftTextActor = vtk.vtkActor2D()
        self._bottomLeftTextActor.SetMapper(self._bottomLeftTextMapper)
        self._bottomLeftTextActor.GetPositionCoordinate(). \
                                    SetCoordinateSystemToNormalizedDisplay()
        self._bottomLeftTextActor.GetPositionCoordinate().SetValue(0.04, 0.05)
        
        #creating directions
        self._directionTextProperty = vtk.vtkTextProperty()
        self._directionTextProperty.SetFontSize(12)
        self._directionTextProperty.SetFontFamilyToArial()
        self._directionTextProperty.ShadowOn()
        self._directionTextProperty.SetShadowOffset(1, 1)
        self._directionTextProperty.ItalicOff()
        self._directionTextProperty.SetJustificationToLeft()
        self._directionTextProperty.SetVerticalJustificationToBottom()
        self._directionTextProperty.SetColor(1.0, 1.0, 1.0)
        
        self._topDirectionTextMapper = vtk.vtkTextMapper()
        self._topDirectionTextMapper.SetTextProperty(self._directionTextProperty)
        
        self._topDirectionActor = vtk.vtkActor2D()
        self._topDirectionActor.SetMapper(self._topDirectionTextMapper)
        self._topDirectionActor.GetPositionCoordinate(). \
                                    SetCoordinateSystemToNormalizedViewport()
        self._topDirectionActor.GetPositionCoordinate().SetValue(0.5, 0.95)
        self._topDirectionActor.GetMapper().SetInput("")
        
        self._bottomDirectionTextMapper = vtk.vtkTextMapper()
        self._bottomDirectionTextMapper.SetTextProperty(self._directionTextProperty)
        
        self._bottomDirectionActor = vtk.vtkActor2D()
        self._bottomDirectionActor.SetMapper(self._bottomDirectionTextMapper)
        self._bottomDirectionActor.GetPositionCoordinate(). \
                                    SetCoordinateSystemToNormalizedViewport()
        self._bottomDirectionActor.GetPositionCoordinate().SetValue(0.5, 0.05)
        self._bottomDirectionActor.GetMapper().SetInput("")
        
        self._leftDirectionTextMapper = vtk.vtkTextMapper()
        self._leftDirectionTextMapper.SetTextProperty(self._directionTextProperty)
        
        self._leftDirectionActor = vtk.vtkActor2D()
        self._leftDirectionActor.SetMapper(self._leftDirectionTextMapper)
        self._leftDirectionActor.GetPositionCoordinate(). \
                                    SetCoordinateSystemToNormalizedViewport()
        self._leftDirectionActor.GetPositionCoordinate().SetValue(0.04, 0.5)
        
        self._leftDirectionActor.GetMapper().SetInput("")

        self._rightDirectionTextMapper = vtk.vtkTextMapper()
        self._rightDirectionTextMapper.SetTextProperty(self._directionTextProperty)        

        self._rightDirectionActor = vtk.vtkActor2D()
        self._rightDirectionActor.SetMapper(self._rightDirectionTextMapper)
        self._rightDirectionActor.GetPositionCoordinate(). \
                                    SetCoordinateSystemToNormalizedViewport()
        self._rightDirectionActor.GetPositionCoordinate().SetValue(0.93, 0.5)
        self._rightDirectionActor.GetMapper().SetInput("")
        
        self.createPlaneOutline()
        
        # Define some default point coordinates
        bounds = [-0.5, 0.5, -0.5, 0.5, -0.5, 0.5]
        
        # Initial creation of the widget, serves to initialize it
#        self.updatePlace(bounds)
        
        self.createTexturePlane()
        self.createCursor()
        self.createMargins()
        self.createText()
        
        # Manage the picking stuff
        self._planePicker = None
        picker = vtk.vtkCellPicker()
        picker.SetTolerance(0.005) # need some fluff
        self.picker = picker
        del picker
        
        # Set up the initial properties
        self._planeProperty = None
        self._selectedPlaneProperty = None
        self._cursorProperty = None
        self._marginProperty = None
        self._texturePlaneProperty = None
        self.createDefaultProperties()
        
        # Set up actions
        self._leftButtonAction = "cursor"
        self._middleButtonAction = "slice-motion"
        self._rightButtonAction = "window-level"
        
        # Set up actions
        self._leftButtonAutoModifier = None
        self._middleButtonAutoModifier = None
        self._rightButtonAutoModifier = None
        
        self._state = "start"
        self._lastButtonPressed = None
        
        self._textureVisibility = True
        
        self._input = None
        self._imageData = None
        self._slice = 0
        self._sliceThickness = 0
        
        self._rotateAxis = [0, 0, 0]
        self._radiusVector = [0, 0, 0]
        self._lastPickPosition = [0, 0, 0]
        
        self._enabled = False
        
        self.interactorStyle = vtk.vtkInteractorStyleImage()
        self._id = "{0}".format(self.parent.id)
        
        self._sliceChangeListeners = []
        self.actualCameraPosition = None
        self.lastNomal = None
        self.__imageWidgetList = []

    def getBorderColor(self):
        if self.planeOrientation == VtkImagePlane.PLANE_ORIENTATION_AXIAL:
            return (1.0, 0.0, 0.0)
        if self.planeOrientation == VtkImagePlane.PLANE_ORIENTATION_CORONAL:
            return (0.0, 1.0, 0.0)
        if self.planeOrientation == VtkImagePlane.PLANE_ORIENTATION_SAGITTAL:
            return (0.0, 0.0, 1.0)
        if self.planeOrientation == VtkImagePlane.PLANE_ORIENTATION_PANORAMIC:
            return (0.5, 0.5, 0.5)
        if self.planeOrientation == VtkImagePlane.PLANE_ORIENTATION_PANORAMIC_SLICE:
            return (0.0, 1.0, 1.0)
      
    def close(self):
        #self._parent = None
        #self._slab.SetInputConnection(None)
        self._slab.GetOutput().ReleaseData()
        #self._colorMap.SetInputConnection(None)
        self._colorMap.GetOutput().ReleaseData()
        #self._texture.SetInputConnection(None)
        self._texture.ReleaseGraphicsResources(self.window)
        #self.renderer.RemoveViewProp(self._texturePlaneActor)
        #self._texturePlaneActor.SetMapper( None )
        #self._texturePlaneActor.SetTexture(None)
        self._texturePlaneActor.ReleaseGraphicsResources(self.window)

        for event in self.events:
            self._interactor.RemoveObserver(event)
        #self.camera.RemoveObserver(self.cameraEvent)

        #super(VtkSliceImagePlane, self).destroy()
        #self._interactor.parent = None
        #self._interactor.close()
        #self._interactor.destroy()
        #self._input = None
        #self._interactor._RenderWindow = None
        #self._imageData = None
        #self.processEvents = None
        self._reslice.GetOutput().ReleaseData()
       
          
    def processEvents(self, obj, event):        
        self._lastButtonPressed = "no-button"
        # okay, let's do the right thing
        if event == "LeftButtonPressEvent":
            self._lastButtonPressed = "LeftButtonPressEvent"
            self.onLeftButtonDown()
        elif event == "LeftButtonReleaseEvent":
            self._lastButtonPressed = "LeftButtonReleaseEvent"
            self.onLeftButtonUp()
        elif event == "MiddleButtonPressEvent":
            self._lastButtonPressed = "MiddleButtonPressEvent"
            self.onMiddleButtonDown()
        elif event == "MiddleButtonReleaseEvent":
            self._lastButtonPressed = "MiddleButtonReleaseEvent"
            self.onMiddleButtonUp()
        elif event == "RightButtonPressEvent":
            self._lastButtonPressed = "RightButtonPressEvent"
            self.onRightButtonDown()
        elif event == "RightButtonReleaseEvent":
            self._lastButtonPressed = "RightButtonReleaseEvent"
            self.onRightButtonUp()
        elif event == "MouseMoveEvent":
            self._lastButtonPressed = "MouseMoveEvent"
            self.onMouseMove()
        elif event == "CharEvent":
            self._lastButtonPressed = "CharEvent"
            self.onChar()
            
    def onLeftButtonDown(self):
        logging.debug("In VtkSliceImagePlane::onLeftButtonDown()")
        if self._leftButtonAction == "cursor":
            self.startCursor()
        elif self._leftButtonAction == "slice-motion":
            self.startSliceMotion()
        elif self._leftButtonAction == "window-levels":
            self.startWindowLevel()
    
    def onLeftButtonUp(self):
        logging.debug("In VtkSliceImagePlane::onLeftButtonUp()")
        
        print "opa"
#        if self._leftButtonAction == "cursor":
#            self.stopCursor()
#        elif self._leftButtonAction == "slice-motion":
#            self.stopSliceMotion()
#        elif self._leftButtonAction == "window-levels":
#            self.stopWindowLevel()
            
    def onMiddleButtonDown(self):
        logging.debug("In VtkSliceImagePlane::onMiddleButtonDown()")
        if self._middleButtonAction == "cursor":
            self.startCursor()
#        elif self._middleButtonAction == "slice-motion":
#            self.startSliceMotion()
        elif self._middleButtonAction == "window-levels":
            self.startWindowLevel()
    
    def onMiddleButtonUp(self):
        logging.debug("In VtkSliceImagePlane::onMiddleButtonUp()")
        if self._middleButtonAction == "cursor":
            self.stopCursor()
        elif self._middleButtonAction == "slice-motion":
            self.stopSliceMotion()
        elif self._middleButtonAction == "window-levels":
            self.stopWindowLevel()
            
    def onRightButtonDown(self):
        logging.debug("In VtkSliceImagePlane::onRightButtonDown()")
        if self._rightButtonAction == "cursor":
            self.startCursor()
        elif self._rightButtonAction == "slice-motion":
            self.startSliceMotion()
        elif self._rightButtonAction == "window-levels":
            self.startWindowLevel()
    
    def onRightButtonUp(self):
        logging.debug("In VtkSliceImagePlane::onRightButtonUp()")
        if self._rightButtonAction == "cursor":
            self.stopCursor()
        elif self._rightButtonAction == "slice-motion":
            self.stopSliceMotion()
        elif self._rightButtonAction == "window-levels":
            self.stopWindowLevel()
            
    def onMouseMove(self):
        logging.debug("In VtkSliceImagePlane::onMouseMove()")
        # See whether we're active
        if self._state == "outside" or self._state == "start":
            return
        
        (X, Y) = self.interactor.GetEventPosition()
        
        # Do different things depending on state
        # Calculations everybody does
        camera = self.renderer.GetActiveCamera()
        if not camera:
            return
        
        focalPoint = [0, 0, 0]
        pickPoint = [0, 0, 0]
        prevPickPoint = [0, 0, 0, 0]
        
        # Compute the two points defining the motion vector
        self.interactorStyle.ComputeWorldToDisplay(self.renderer,
                                                   self._lastPickPosition[0],
                                                   self._lastPickPosition[1],
                                                   self._lastPickPosition[2],
                                                   focalPoint)
        
        z = focalPoint[2]
        
        self.interactorStyle.ComputeDisplayToWorld(
                self.renderer,
                self.interactor.GetLastEventPosition()[0],
                self.interactor.GetLastEventPosition()[1],
                z, prevPickPoint)
        
        self.interactorStyle.ComputeWorldToDisplay(self.renderer, 
                                                   X, Y, z, pickPoint)
        
        if self._state == "window-levelling":
            self.windowLevel(X, Y)
            self.manageTextDisplay()
        elif self._state == "pushing":
            self.push(prevPickPoint, pickPoint)
            self.updatePlane()
            self.updateMargins()
            self.buildRepresentation()
        elif self._state == "spinning":
            self.spin(prevPickPoint, pickPoint)
            self.updatePlane()
            self.updateMargins()
            self.buildRepresentation()
        elif self._state == "rotating":
            self.rotate(prevPickPoint, pickPoint)
            self.updatePlane()
            self.updateMargins()
            self.buildRepresentation()
            ##TODO update Directions
        elif self._state == "scaling":
            self.scale(prevPickPoint, pickPoint)
            self.updatePlane()
            self.updateMargins()
            self.buildRepresentation()
        elif self._state == "moving":
            self.updatePlane()
            self.updateMargins()
            self.buildRepresentation()
        elif self._state == "cursoring":
            self.updateCursor(X, Y)
            self.manageTextDisplay()
        
        # Interact, if desired
        if self._state == "window-levelling":
            pass
        else:
            pass
        
        self.window.Render()
        
    def onChar(self):
        logging.debug("In VtkSliceImagePlane::onChar()")
        if self.interactor.GetKeyCode() == "r" \
           or self.interactor.GetKeyCode() == "R":
            if self.interactor.GetShiftKey() or self.interactor.GetControlKey():
                self.windowLevel(self._originalWindow, self._originalLevel)
            else:
                self.interactorStyle.OnChar()
        else:
            self.interactorStyle.OnChar()

                                
    def startCursor(self):
        logging.debug("In VtkSliceImagePlane::startCursor()")
        if self._state == "outside" or self._state == "start":
            return
        self._state = "start"
        self.highlightPlane(False)
        self.activateCursor(False)
        self.activateText(False)
        
        #self.endInteraction()
        self.window.Render()
        
    def startSliceMotion(self):
        logging.debug("In VtkSliceImagePlane::startSliceMotion()")
        (X, Y) = self.interactor.GetEventPosition()
        
        # Okay, make sure that the pick is in the current renderer
        if not self.renderer or not self.renderer.IsInViewport(X, Y):
            self._state = "outside"
            return
        
        # Okay, we can process this. If anything is picked, then we
        # can start pushing the plane.
        self._planePicker.Pick(X, Y, 0, self.renderer)
        path = self._planePicker.GetPath()
         
        found = False
        if path:
            # Deal with the possibility that we may be using a shared picker
            path.InitTraversal()
            for i in range(path.GetNumberOfItems()):
                node = path.GetNextNode()
                if node.GetViewProp() == vtk.vtkProp.SafeDownCast(
                                                    self._texturePlaneActor):
                    found = True
                    break
                 
        if not found or not path:
            self._state = "outside"
            self.highlightPlane(False)
            self.activateMargins(False)
            return
        else:
            self._state = "pushing"
            self.highlightPlane(True)
            self.activateMargins(True)
            self.updateState()
            self.updateMargins()
        
        #self.interactor.StartInteraction()
        self.window.Render()
        
    def stopSliceMotion(self):
        logging.debug("In VtkSliceImagePlane::stopSliceMotion()")
        if self._state == "outside" or self._state == "start":
            return
        self._state = "start"
        self.highlightPlane(False)
        self.activateMargins(False)
        
        #self.interactor.EndInteraction()
        self.window.Render()
        
    def startWindowLevel(self):
        logging.debug("In VtkSliceImagePlane::startWindowLevel()")
        (X, Y) = self.interactor.GetEventPosition()
        
        # Okay, make sure that the pick is in the current renderer
        '''if not self.renderer or not self.renderer.IsInViewport(X, Y):
            self._state = "outside"
            return
        '''
        
        # Okay, we can process this. If anything is picked, then we
        # can start pushing the plane.
        self._planePicker.Pick(X, Y, 0, self.renderer)
        path = self._planePicker.GetPath()
         
        found = False
        if path:
            # Deal with the possibility that we may be using a shared picker
            path.InitTraversal()
            for i in range(path.GetNumberOfItems()):
                node = path.GetNextNode()
                if node.GetViewProp() == vtk.vtkProp.SafeDownCast( self._texturePlaneActor ):
                    found = True
                    break
                
        self._initialWindow = self._currentWindow
        self._initialLevel = self._currentLevel
                 
        '''if not found or not path:
            self._state = "outside"
            self.highlightPlane(False)
            self.activateText(False)
            return
        else:
            self._state = "window-levelling"
            self.highlightPlane(True)
            self.activateMargins(True)
            self._startWindowLevelPositionX = X
            self._startWindowLevelPositionY = Y
            self.manageTextDisplay()
        '''
        self.highlightPlane(True)
        self.activateMargins(True)
        self._startWindowLevelPositionX = X
        self._startWindowLevelPositionY = Y
        self.manageTextDisplay()
        
        #self.startInteraction()
        self.window.Render()
        
    def stopWindowLevel(self):
        logging.debug("In VtkSliceImagePlane::stopWindowLevel()")
        if self._state == "outside" or self._state == "start":
            return
        self._state = "start"
        self.highlightPlane(False)
        self.activateText(False)
        self._interactorStyle.add
        
        self.endInteraction()
        self.window.Render()
        self.interactorStyle = None
    
    def cameraModifiedObserver(self, a ,b):
        self.updateDirections()
        
    def addObservers(self):
        logging.debug("In VtkSliceImagePlane::addObservers()")
        self.events = []
        if self.interactor:
            self.events = [self.interactor.AddObserver("MouseMoveEvent", self.processEvents),
            self.interactor.AddObserver("LeftButtonPressEvent", 
                                        self.processEvents),
            self.interactor.AddObserver("MiddleButtonPressEvent", 
                                        self.processEvents),
            self.interactor.AddObserver("MiddleButtonReleaseEvent", 
                                        self.processEvents),
            self.interactor.AddObserver("RightButtonPressEvent", 
                                        self.processEvents),
            self.interactor.AddObserver("RightButtonReleaseEvent", 
                                        self.processEvents),
            
            self.interactor.AddObserver("CharEvent", self.processEvents)]
        
        self.cameraEvent = self.camera.AddObserver("ModifiedEvent", 
                                    self.cameraModifiedObserver)
            
    def windowLevel2(self, X, Y, minRange = None, maxRange = None):
        logging.debug("In VtkSliceImagePlane::windowLevel2()")
        if X == 0 and Y == 0:
            return
        
         
        window = self._currentWindow
        level = self._currentLevel
        
        
        if not minRange:
            minRange = 0
        if not maxRange:
            maxRange = 2000
        # Compute normalized delta
        dx = ((maxRange - minRange) / 500) * X 
        dy = ((maxRange - minRange) / 500) * Y
        
        # Compute new window level
        newWindow = dx + window
        newLevel = level - dy
        if minRange:
            if newWindow < 0.1:
                newWindow = 0.1
            if newLevel < minRange:
                newLevel = minRange
        if maxRange:
            if newWindow > maxRange - minRange:
                newWindow = maxRange - minRange
            if newLevel > maxRange:
                newLevel = maxRange
        
        if not self._userControlledLookupTable:
            rmin = newLevel - 0.5*abs(newWindow)
            rmax = rmin + abs(newWindow)
            self._lookupTable.SetTableRange(rmin, rmax)
        self._currentWindow = newWindow
        self._currentLevel = newLevel
        self.window.Render()
        
    def manageTextDisplay(self):
        logging.debug("In VtkSliceImagePlane::manageTextDisplay()")
        if not self._displayText:
            return
        
    @property
    def textureVisibility(self):
        logging.debug("In VtkSliceImagePlane::textureVisibility()")
        return self._textureVisibility
        
    @textureVisibility.setter
    def textureVisibility(self, flag):
        logging.debug("In VtkSliceImagePlane::textureVisibility()")
        if self._textureVisibility == flag:
            return
        self._textureVisibility = flag
        if self._enabled and self._textureVisibility:
            self.renderer.AddViewProp(self._texturePlaneActor)
        else:
            self.renderer.RemoveViewProp(self._texturePlaneActor)
        self.modified()
        
    def modified(self):
        logging.debug("In VtkSliceImagePlane::modified()")
        self._texturePlaneActor.Modified()
        
    def resliceInterpolate(self, i):
        logging.debug("In VtkSliceImagePlane::resliceInterpolate()")
        
    def createPlaneOutline(self):
        logging.debug("In VtkSliceImagePlane::createPlaneOutline()")
        points = vtk.vtkPoints()
        points.SetNumberOfPoints(4)
        for i in range(4):
            points.SetPoint(i, (0, 0, 0))
            
        cells = vtk.vtkCellArray()
        cells.Allocate(0, cells.EstimateSize(4, 2))
        pts = vtk.vtkIdList()
        pts.InsertNextId(3)
        pts.InsertNextId(2)
        cells.InsertNextCell(pts) # top edge
        
        pts = vtk.vtkIdList()
        pts.InsertNextId(0)
        pts.InsertNextId(1)
        cells.InsertNextCell(pts) # bottom edge
        
        pts = vtk.vtkIdList()
        pts.InsertNextId(0)
        pts.InsertNextId(3)
        cells.InsertNextCell(pts) # left edge
        
        pts = vtk.vtkIdList()
        pts.InsertNextId(1)
        pts.InsertNextId(2)
        cells.InsertNextCell(pts) # right edge
        
        self._planeOutlinePolyData.SetPoints(points)
        del points
        
        self._planeOutlinePolyData.SetLines(cells)
        del cells
        
        planeOutlineMapper = vtk.vtkPolyDataMapper()
        planeOutlineMapper.SetInput(self._planeOutlinePolyData)
        planeOutlineMapper.SetResolveCoincidentTopologyToPolygonOffset()
        
        self._planeOutlineActor.SetMapper(planeOutlineMapper)
        self._planeOutlineActor.PickableOff()
        del planeOutlineMapper
        
    def createDefaultLookupTable(self):
        logging.debug("In VtkSliceImagePlane::createDefaultLookupTable()")
        lut = vtk.vtkWindowLevelLookupTable()
        lut.Register(self.interactor)
        lut.SetNumberOfColors(256)
        lut.SetHueRange(0, 0)
        lut.SetSaturationRange(0, 0)
        lut.SetValueRange(0, 1)
        lut.SetAlphaRange(1, 1)
        lut.Build()
        return lut
    
    def createDefaultProperties(self):
        logging.debug("In VtkSliceImagePlane::createDefaultProperties()")
        if not self._planeProperty:
            self._planeProperty = vtk.vtkProperty()
            self._planeProperty.SetAmbient(1)
            self._planeProperty.SetColor(1, 1, 1)
            self._planeProperty.SetRepresentationToWireframe()
            self._planeProperty.SetInterpolationToFlat()
        if not self._selectedPlaneProperty:
            self._selectedPlaneProperty = vtk.vtkProperty()
            self._selectedPlaneProperty.SetAmbient(1)
            self._selectedPlaneProperty.SetColor(0, 1, 0)
            self._selectedPlaneProperty.SetRepresentationToWireframe()
            self._selectedPlaneProperty.SetInterpolationToFlat()
        if not self._cursorProperty:
            self._cursorProperty = vtk.vtkProperty()
            self._cursorProperty.SetAmbient(1)
            self._cursorProperty.SetColor(0, 0, 1)
            self._cursorProperty.SetRepresentationToWireframe()
            self._cursorProperty.SetInterpolationToFlat()
        if not self._texturePlaneProperty:
            self._texturePlaneProperty = vtk.vtkProperty()
            self._texturePlaneProperty.SetAmbient(1)
            self._texturePlaneProperty.SetInterpolationToFlat()
            self._texturePlaneProperty.EdgeVisibilityOn()
            self._texturePlaneProperty.SetEdgeColor( self._texturePlaneActorColor[0], self._texturePlaneActorColor[1], self._texturePlaneActorColor[2] )

    def createTexturePlane(self):
        logging.debug("In VtkSliceImagePlane::createTexturePlane()")
        self._reslice.SetInterpolationModeToLinear()
        self._texture.SetInterpolate(self._textureInterpolate)
        
        self._lookupTable = self.createDefaultLookupTable()
        
        self._colorMap.SetLookupTable(self._lookupTable)
        self._colorMap.SetOutputFormatToRGBA()
        self._colorMap.PassAlphaToOutputOn()
        
        texturePlaneMapper = vtk.vtkPolyDataMapper()
        texturePlaneMapper.SetInput( vtk.vtkPolyData.SafeDownCast(self._planeSource.GetOutput()) )
        
        self._texture.SetQualityTo32Bit()
        self._texture.MapColorScalarsThroughLookupTableOff()
        self._texture.SetInterpolate(self._textureInterpolate)
        self._texture.RepeatOff()
        self._texture.SetLookupTable(self._lookupTable)
        
        self._texturePlaneActor.SetMapper( texturePlaneMapper )
        self._texturePlaneActor.SetTexture(self._texture)
        self._texturePlaneActor.PickableOn()
        self._texturePlaneActor.GetProperty().EdgeVisibilityOn()
        self._texturePlaneActor.GetProperty().SetEdgeColor( self._texturePlaneActorColor[0], self._texturePlaneActorColor[1], self._texturePlaneActorColor[2] )
        #self.actor = self._texturePlaneActor

        self._texturePlaneWidgetActor.SetMapper( texturePlaneMapper )
        self._texturePlaneWidgetActor.SetTexture( self._texture )
        self._texturePlaneWidgetActor.PickableOn()
        self._texturePlaneWidgetActor.GetProperty().SetOpacity( 0.9 )
        self._texturePlaneWidgetActor.GetProperty().EdgeVisibilityOn()
        self._texturePlaneWidgetActor.GetProperty().SetEdgeColor( self._texturePlaneActorColor[0], self._texturePlaneActorColor[1], self._texturePlaneActorColor[2] )

        self._textureLineWidgetActor.SetMapper( texturePlaneMapper )
        self._textureLineWidgetActor.PickableOn()
        self._textureLineWidgetActor.GetProperty().SetOpacity( 0.9 )
        self._textureLineWidgetActor.GetProperty().EdgeVisibilityOn()
        self._textureLineWidgetActor.GetProperty().SetEdgeColor( self._texturePlaneActorColor[0], self._texturePlaneActorColor[1], self._texturePlaneActorColor[2] )

        del texturePlaneMapper

    def createLineWidgetActor( self, scene ):

        from multisliceimageplane import VtkMultiSliceImagePlane
        if self.parent.title.split()[0] == "Transversal":
            from slicewidget import TransversalSlicePlaneWidget
            return TransversalSlicePlaneWidget( self, scene, color=self._texturePlaneActorColor )

        else:
            from slicewidget import SlicePlaneWidget
            self._lineWidgetActor = SlicePlaneWidget( self, scene, color=self._texturePlaneActorColor )

        return self._lineWidgetActor

    def getLineWidget( self, scene ):

        return self.createLineWidgetActor( scene )

    def getPlaneWidget( self, scene ):

        return self._texturePlaneWidgetActor

    def addLinePlaneWidget( self, planeWidget ):
        if  planeWidget not in self.__imageWidgetList:
            self.__imageWidgetList.append( planeWidget )
            self.addActor( planeWidget )
            self.renderer.ResetCameraClippingRange()
            self.window.Render()

    def removeLinePlaneWidget( self, planeWidget ):
        if  planeWidget in self.__imageWidgetList:
            self.__imageWidgetList.remove( planeWidget )
            self.removeActor( planeWidget )
            self.window.Render()
        
    def createCursor(self):
        logging.debug("In VtkSliceImagePlane::createCursor()")
        
    def createMargins(self):
        logging.debug("In VtkSliceImagePlane::createMargins()")
        # Construct initial points
        points = vtk.vtkPoints()
        points.SetNumberOfPoints(8)
        for i in range(8):
            points.SetPoint(i, 0, 0, 0)
        
        cells = vtk.vtkCellArray()
        cells.Allocate(0, cells.EstimateSize(4, 2))
        
        pts = vtk.vtkIdList()
        pts.InsertNextId(0)
        pts.InsertNextId(1)
        cells.InsertNextCell(pts) # top margin
        
        pts = vtk.vtkIdList()
        pts.InsertNextId(2)
        pts.InsertNextId(3)
        cells.InsertNextCell(pts) # bottom margin
        
        pts = vtk.vtkIdList()
        pts.InsertNextId(4)
        pts.InsertNextId(5)
        cells.InsertNextCell(pts) # left margin
        
        pts = vtk.vtkIdList()
        pts.InsertNextId(6)
        pts.InsertNextId(7)
        cells.InsertNextCell(pts) # right margin
        
        self._marginPolyData.SetPoints(points)
        del points
        
        self._marginPolyData.SetLines(cells)
        del cells
        
        marginMapper = vtk.vtkPolyDataMapper()
        marginMapper.SetInput(self._marginPolyData)
        marginMapper.SetResolveCoincidentTopologyToPolygonOffset()
        self._marginActor.SetMapper(marginMapper)
        self._marginActor.PickableOff()
        self._marginActor.VisibilityOff()
        del marginMapper       
        
    def createText(self):
        logging.debug("In VtkSliceImagePlane::createText()")
        
    def updatePlane(self):

        logging.debug("In VtkSliceImagePlane::updatePlane()")
        if not self._imageData :
            return
        # Calculate appropriate pixel spacing for the reslicing
        self._imageData.UpdateInformation()
        spacing = self._imageData.GetSpacing()
#        origin = self._imageData.GetOrigin()
        extent = self._imageData.GetWholeExtent()

        for i in range(3):
            if extent[2*i] > extent[2*i + 1]:
                raise Exception("Invalid extent " \
                                "[{0}, {1}, {2}, {3}, {4}, {5}] " \
                                "Perhaps the input data is empty?" \
                                    .format(extent[0], extent[1], extent[2],
                                            extent[3], extent[4], extent[5]))
                
        
        # Generate the slicing matrix
        self._resliceAxes.Identity()
        pt1 = self._slice.plane.GetPoint1()
        origin = self._slice.plane.GetOrigin()
        planeAxis1 = [p1-o for p1, o in zip(pt1, origin)]
        pt2 = self._slice.plane.GetPoint2()
        planeAxis2 = [p2-o for p2, o in zip(pt2, origin)]
        
        vtk.vtkMath.Normalize(planeAxis1)
        vtk.vtkMath.Normalize(planeAxis2)
        planeAxis3 = [0.0, 0.0, 0.0]
        vtk.vtkMath.Cross(planeAxis1, planeAxis2, planeAxis3)
        vtk.vtkMath.Normalize(planeAxis3)
        
        self._reslice.SetResliceAxesDirectionCosines(planeAxis1, planeAxis2, planeAxis3)
        self._reslice.SetResliceAxesOrigin(self._slice.plane.GetOrigin())
        self._reslice.SetOutputOrigin(0.0, 0.0, 0.0)
        
        if self._slabThickness > 0:
            spacing = self._slabSpacing
            self._reslice.SetOutputExtent(0, int(self._slice.width /spacing[0]), 0, int(self._slice.height / spacing[1]), int((self._slabThickness/ spacing[2]) / -2.), int((self._slabThickness/ spacing[2]) / 2.))
        else:    
            self._reslice.SetOutputExtent(0, int(self._slice.width /spacing[0]), 0, int(self._slice.height / spacing[1]), 0, 1)
        self._reslice.SetOutputSpacing(spacing[0], spacing[1], spacing[2])
        #updating plane source
#        print "Origin:", self._slice.plane.GetOrigin()
        self._planeSource.SetOrigin(self._slice.plane.GetOrigin())
#        self.addBall(self._slice.plane.GetOrigin(), [0,1,0])
        self._planeSource.SetPoint1(self._slice.plane.GetPoint1())
#        self.addBall(self._slice.plane.GetPoint1(), [1,0,0])
        self._planeSource.SetPoint2(self._slice.plane.GetPoint2())
#        self.addBall(self._slice.plane.GetPoint2(), [0,0,1])
        self._planeSource.Update()

        if self._firstUpdate:
            self.updateCamera()
            self._firstUpdate = False
        if self.planeOrientation == VtkImagePlane.PLANE_ORIENTATION_PANORAMIC_SLICE:
            self.updateCameraPosition()
        self.notifySliceChangeListeners()

    def notifySliceChangeListeners(self):
        for listener in self._sliceChangeListeners:
            listener(self)
            
    def addSliceChangeListener(self, listener):
        self._sliceChangeListeners.append(listener)
        
    def removeSliceChangeListener(self, listener):
        if self._sliceChangeListeners.count(listener):
            self._sliceChangeListeners.remove(listener)
                
    def vector1(self):
        logging.debug("In VtkSliceImagePlane::vector1()")
        pt1 = self._planeSource.GetPoint1()
        origin = self._planeSource.GetOrigin()
        return [p1-o for p1, o in zip(pt1, origin)]
        
    def vector2(self):
        logging.debug("In VtkSliceImagePlane::vector2()")
        pt2 = self._planeSource.GetPoint2()
        origin = self._planeSource.GetOrigin()
        return [p2-o for p2, o in zip(pt2, origin)]
            
    def updateState(self):
        logging.debug("In VtkSliceImagePlane::updateState()")
        v1 = self.vector1()
        v2 = self.vector2()
        planeSize1 = vtk.vtkMath.Normalize(v1)
        planeSize2 = vtk.vtkMath.Normalize(v2)
        planeOrigin = self._planeSource.GetOrigin()
        
        ppo = [0 - planeOrigin[0],
               0 - planeOrigin[1],
               0 - planeOrigin[2]]
        
        x2D = vtk.vtkMath.Dot(ppo, v1)
        y2D = vtk.vtkMath.Dot(ppo, v2)
        if x2D > planeSize1:
            x2D = planeSize1
        elif x2D < 0:
            x2D = 0
        if y2D > planeSize2:
            y2D = planeSize2
        elif y2D < 0:
            y2D = 0
        
        # Divide plane into three zones for different user interactions:
        # four corners -- spin around the plane's normal at its center
        # four edges   -- rotate around one of the plane's axes at its center
        # center area  -- push
        marginX = planeSize1 * self._marginSizeX
        marginY = planeSize2 * self._marginSizeY
        
        x0 = marginX
        y0 = marginY
        x1 = planeSize1 - marginX
        y1 = planeSize2 - marginY
        
        if x2D < x0: # left margin
            if y2D < y0: # bottom left corner
                self._marginSelectMode = 0
            elif y2D > y1: # top left corner
                self._marginSelectMode = 3
            else: # left edge
                self._marginSelectMode = 4
        elif x2D > x1: # right margin
            if y2D < y0: # bottom right corner
                self._marginSelectMode = 1
            elif y2D > y1: # top right corner
                self._marginSelectMode = 2
            else: # right edge
                self._marginSelectMode = 5
        else: # middle or  on the very edge
            if y2D < y0: # bottom edge
                self._marginSelectMode = 6
            elif y2D > y1: # top edge
                self._marginSelectMode = 7
            else: # central area
                self._marginSelectMode = 8
                
        raPtr = 0
        rvPtr = 0
        rvfac = 1
        rafac = 1
        
        if self._marginSelectMode == 0:
            raPtr = v1
            rvPtr = v2
            rvfac = -1
            rafac = -1
        elif self._marginSelectMode == 1:
            raPtr = v2
            rvPtr = v1
            rafac = -1
        elif self._marginSelectMode == 2:
            raPtr = v2
            rvPtr = v1
        elif self._marginSelectMode == 3:
            raPtr = v2
            rvPtr = v1
            rvfac = -1
        elif self._marginSelectMode == 4:
            raPtr = v2
            rvPtr = v1
            rvfac = -1
        elif self._marginSelectMode == 5:
            raPtr = v2
            rvPtr = v1
            rvfac = -1
        elif self._marginSelectMode == 6:
            raPtr = v1
            rvPtr = v2
            rvfac = -1
        elif self._marginSelectMode == 7:
            raPtr = v1
            rvPtr = v2
        else:
            raPtr = v1
            rvPtr = v2
    
        for i in range(3):
            self._rotateAxis[i] = (raPtr[i] + 1.0) * rafac
            self._radiusVector[i] = (rvPtr[i] + 1.0) * rvfac
            
    def buildRepresentation(self):
        logging.debug("In VtkSliceImagePlane::buildRepresentation()")
        self._planeSource.Update()
        o = self._planeSource.GetOrigin()
        pt1 = self._planeSource.GetPoint1()
        pt2 = self._planeSource.GetPoint2()
        
        x = [o[0] + (pt1[0]-o[0]) + (pt2[0]-o[0]),
             o[1] + (pt1[1]-o[1]) + (pt2[1]-o[1]),
             o[2] + (pt1[2]-o[2]) + (pt2[2]-o[2])]
        
        
        points = self._planeOutlinePolyData.GetPoints()
        points.SetPoint(0, o)
        points.SetPoint(1, pt1)
        points.SetPoint(2, x)
        points.SetPoint(3, pt2)
        points.GetData().Modified()
        self._planeOutlinePolyData.Modified()
        
    def updateCursor(self, X, Y):
        logging.debug("In VtkSliceImagePlane::updateCursor()")
        if not self._imageData:
            return
        
        # We're going to be extracting values with GetScalarComponentAsDouble(),
        # we might as well make sure that the data is there.  If the data is
        # up to date already, this call doesn't cost very much.  If we don't make
        # this call and the data is not up to date, the GetScalar... call will
        # cause a segfault.
        self._imageData.Update()
        
        self._planePicker.Pick(X, Y, 0, self.renderer)
        path = self._planePicker.GetPath()
        self._currentImageValue = vtk.VTK_DOUBLE_MAX
        
        found = False
        if path:
            # Deal with the possibility that we may be using a shared picker
            path.InitTraversal()
            for i in range(path.GetNumberOfItems()):
                node = path.GetNextNode()
                if node.GetViewProp() == vtk.vtkProp.SafeDownCast(
                                                self._texturePlaneActor):
                    found = True
                    break
                
        if not found or not path:
            self._cursorActor.VisibilityOff()
            return
        else:
            self._cursorActor.VisibilityOn()
            
        q = [0, 0, 0]
        self._planePicker.GetPickPosition(q)
        
        if self._userContinuousCursor:
            found = self.updateContinuosCursor(q)
        else:
            found = self.updateDiscreteCursor(q)
            
        if not found:
            self._cursorActor.VisibilityOff()
            return
        
        o = self._planeSource.GetOrigin()
        
        # q relative to the plane origin
        qro = [q[0] - o[0], q[1] - o[1], q[2] - o[2]]
        
        p1o = self.vector1()
        p2o = self.vector2()
        
        lp1 = vtk.vtkMath.Dot(qro, p1o) / vtk.vtkMath.Dot(p1o, p1o)
        lp2 = vtk.vtkMath.Dot(qro, p2o) / vtk.vtkMath.Dot(p2o, p2o)
        
        p1 = self._planeSource.GetPoint1()
        p2 = self._planeSource.GetPoint2()
        
        a = [0, 0, 0]
        b = [0, 0, 0]
        c = [0, 0, 0]
        d = [0, 0, 0]
        for i in range(3):
            a[i] = o[i] + lp2*p2o[i] # left
            b[i] = p1[i] + lp2*p2o[i] # right
            c[i] = o[i] + lp1*p1o[i] # bottom
            d[i] = p2[i] + lp1*p1o[i] # top
        
        cursorPts = self._cursorPolyData.GetPoints()
        cursorPts.SetPoint(0, a)
        cursorPts.SetPoint(1, b)
        cursorPts.SetPoint(2, c)
        cursorPts.SetPoint(3, d)
        
        self._cursorPolyData.Modified()
        
    def updateContinuosCursor(self, q):
        logging.debug("In VtkSliceImagePlane::updateContinuosCursor()")
        
    def updateDiscreteCursor(self, q):
        logging.debug("In VtkSliceImagePlane::updateDiscreteCursor()")
        
    def updatePlacement(self):
        logging.debug("In VtkSliceImagePlane::updatePlacement()")
        self.updatePlane()
        self.updateMargins()
        self.buildRepresentation()
        
    def updateMargins(self):
        logging.debug("In VtkSliceImagePlane::updateMargins()")
        v1 = self.vector1()
        v2 = self.vector2()
        o = self._planeSource.GetOrigin()
        p1 = self._planeSource.GetPoint1()
        p2 = self._planeSource.GetPoint2()
        
        a = [0, 0, 0]
        b = [0, 0, 0]
        c = [0, 0, 0]
        d = [0, 0, 0]
        
        s = self._marginSizeX
        t = self._marginSizeY
        
        for i in range(3):
            a[i] = o[i] + v2[i]*(1-t)
            b[i] = p1[i] + v2[i]*(1-t)
            c[i] = o[i] + v2[i]*t
            d[i] = p1[i] + v2[i]*t
            
        marginPts = self._marginPolyData.GetPoints()
        marginPts.SetPoint(0, a)
        marginPts.SetPoint(1, b)
        marginPts.SetPoint(2, c)
        marginPts.SetPoint(3, d)
        
        for i in range(3):
            a[i] = o[i] + v1[i]*s
            b[i] = p2[i] + v1[i]*s
            c[i] = o[i] + v1[i]*(1-s)
            d[i] = p2[i] + v1[i]*(1-s)
            
        marginPts.SetPoint(4, a)
        marginPts.SetPoint(5, b)
        marginPts.SetPoint(6, c)
        marginPts.SetPoint(7, d)
        
        self._marginPolyData.Modified()
        
    def updateCamera(self, oldScale = None):
        logging.debug("In VtkSliceImagePlane::highlightPlane()")
        flipper = 1
        if self.planeOrientation == VtkImagePlane.PLANE_ORIENTATION_AXIAL:
            flipper = -1
        elif self.planeOrientation == VtkImagePlane.PLANE_ORIENTATION_CORONAL:
            flipper = -1
        elif self.planeOrientation == VtkImagePlane.PLANE_ORIENTATION_SAGITTAL:
            flipper = 1
        
        extent = self._imageData.GetWholeExtent()
        xs = extent[5] - extent[4] + 1
        scale = 150 if xs < 150 else (xs - 1) / 2.0
        center = self._planeSource.GetCenter()
        self.camera.SetPosition([c - n * 600 * flipper for c, n in zip(center,  self._planeSource.GetNormal())])
        up = [p2 - o for p2, o in zip(self._planeSource.GetPoint2(),  self._planeSource.GetOrigin())]
        vtk.vtkMath.Normalize(up)
        self.camera.SetViewUp(up)
        self.camera.SetFocalPoint([p1+p2 for p1, p2 in zip(center, self._planeSource.GetNormal())])
        self.camera.ComputeViewPlaneNormal()
        self.camera.OrthogonalizeViewUp()
        self.camera.ParallelProjectionOn()
        self.camera.SetParallelScale(scale)
        self.renderer.ResetCameraClippingRange()
        self.renderer.ResetCamera()
        if oldScale != None:
            self.camera.Zoom(self.camera.GetParallelScale() / oldScale)
        self.renderer.Render()
        self.lastNormal = self.getSlicePositionNormal(self.actualPosition)
        
    def updateCameraPosition(self):
        logging.debug("In VtkSliceImagePlane::highlightPlane()")
        revertConst = 1
        if self.lastNormal != None:
            total = 0;
            for n, cn in zip(self.lastNormal, self.camera.GetViewPlaneNormal()):
                total = total + (n + cn)
            if 0.00001 < total or total < -0.00001:
                revertConst = -1
        else:
            if self.planeOrientation == VtkImagePlane.PLANE_ORIENTATION_AXIAL:
                revertConst = -1
            elif self.planeOrientation == VtkImagePlane.PLANE_ORIENTATION_CORONAL:
                revertConst = -1
            elif self.planeOrientation == VtkImagePlane.PLANE_ORIENTATION_SAGITTAL:
                revertConst = 1
        center = self._planeSource.GetCenter()
        self.camera.SetPosition([c - n * 600 * revertConst for c, n in zip(center,  self._planeSource.GetNormal())])
        self.camera.SetFocalPoint([p1+p2 for p1, p2 in zip(center, self._planeSource.GetNormal())])
        self.renderer.Render()
        self.lastNormal = self.getSlicePositionNormal(self.actualPosition)
        
    def highlightPlane(self, highlight=True):
        logging.debug("In VtkSliceImagePlane::highlightPlane()")
        if highlight:
            self._planeOutlineActor.SetProperty(self._selectedPlaneProperty)
            self._lastPickPosition = self._planePicker.GetPickPosition()
        else:
            self._planeOutlineActor.SetProperty(self._planeProperty)
        
    def invertTable(self):
        logging.debug("In VtkSliceImagePlane::invertTable()")
        index = self._lookupTable.GetNumberOfTableValues()
        table = self._lookupTable.GetTable()
        for count in range(index-1):
            rgba1 = table.GetPointer(4*count)
            rgba2 = table.GetPointer(4*index)
            rgba1, rgba2 = rgba2, rgba1
        
        # force the lookuptable to update its InsertTime to avoid
        # rebuilding the array
        self._lookupTable.SetTableValue(0, self._lookupTable.GetTableValue(0))
        
    def lookupTable(self, table):
        logging.debug("In VtkSliceImagePlane::lookupTable()")
        if self._lookupTable != table:
            temp = self._lookupTable
            self._lookupTable = table
            if temp:
                temp.UnRegister(self.interactor)
            if self._lookupTable:
                self._lookupTable.Register(self.interactor)
            else:
                self._lookupTable = self.createDefaultLookupTable()
            self._colorMap.SetLookupTable(self._lookupTable)
            self._texture.SetLookupTable(self._lookupTable)
            
        if self._imageData and not self._userControlledLookupTable:
            range = self._imageData.GetScalarRange()
            
            self._lookupTable.SetTableRange(range[0], range[1])
            self._lookupTable.Build()
            
            self._originalWindow = range[1] - range[0]
            self._originalLevel = 0.5*(range[0] + range[1])
            
            if abs(self._originalWindow) < 0.001:
                self._originalWindow = 0.001 * (-1 if self._originalWindow < 0 else 1)
            if abs(self._originalLevel) < 0.001:
                self._originalLevel = 0.001 * (-1 if self._originalLevel < 0 else 1)
                
            self.windowLevel(self._originalWindow, self._originalLevel)
    
    @property
    def brightness(self):
        rmin = self._currentLevel - 0.5*abs(self._currentWindow)
        rmax = rmin + abs(self._currentWindow)
        b = 100*(self._currentLevel-rmax)/(rmin-rmax)
        return b
      
    @property
    def currentLevel(self):
        return self._currentLevel
    
    @property
    def currentWindow(self):
        return self._currentWindow
      
    def windowLevel(self, window, level, copy=False):
        logging.debug("In VtkSliceImagePlane::windowLevel()")
        if copy:
            self._currentLevel = window
            self._currentLevel = level
            return
        
        if self._currentWindow == window and self._currentLevel == level:
            return
        
        # if the new window is negative and the old window was 
        # positive invert table
        if ((window < 0 and self._currentWindow > 0) \
            or (window > 0 and self._currentWindow < 0)) \
            and not self._userControlledLookupTable:
#            self.invertTable()
            pass
        
        self._currentWindow = window
        self._currentLevel = level 
        
        if not self._userControlledLookupTable:
            rmin = self._currentLevel - 0.5*abs(self._currentWindow)
            rmax = rmin + abs(self._currentWindow)
            self._lookupTable.SetTableRange(rmin, rmax)
#        self.level.SetWindow(self.cWindow)
#        self.level.SetLevel(self.cLevel)
#        self.level.SetOutputFormatToLuminance()
#        self.level.Update()
#        self.vtkrender()
#        self.vtkInteractor.Render()
        # self.interactor.Render())
        self.window.Render()
        
    def push(self, pt1, pt2):
        logging.debug("In VtkSliceImagePlane::push()")
        v = [p2-p1 for p1, p2 in zip(pt1, pt2)]
        self._planeSource.Push(
            vtk.vtkMath.Dot(v, self._planeSource.GetNormal()))
        
    def activateCursor(self, flag):
        logging.debug("In VtkSliceImagePlane::activateCursor()")
        if not self.renderer:
            return
        if flag:
            self._cursorActor.VisibilityOff()
        else:
            self._cursorActor.VisibilityOn()
            
    def activateMargins(self, flag):
        logging.debug("In VtkSliceImagePlane::activateMargins()")
        if not self.renderer:
            return
        if flag:
            self._marginActor.VisibilityOff()
        else:
            self._marginActor.VisibilityOn()
            
    def activateText(self, flag):
        logging.debug("In VtkSliceImagePlane::activateText()")
        if not self.renderer:
            return
        if flag:
            self._topLeftTextActor.VisibilityOff()
            self._bottomLeftTextActor.VisibilityOff()
        else:
            self._topLeftTextActor.VisibilityOn()
            self._bottomLeftTextActor.VisibilityOn()
    
    def activateDirections(self, flag):
        logging.debug("In VtkSliceImagePlane::activateText()")
        if not self.renderer:
            return
        if flag:
            self._topDirectionActor.VisibilityOn()
            self._bottomDirectionActor.VisibilityOn()
            self._leftDirectionActor.VisibilityOn()
            self._rightDirectionActor.VisibilityOn()
        else:
            self._topDirectionActor.VisibilityOff()
            self._bottomDirectionActor.VisibilityOff()
            self._leftDirectionActor.VisibilityOff()
            self._rightDirectionActor.VisibilityOff()
            
    @property
    def imagedata(self):
        logging.debug("In VtkSliceImagePlane::imagedata.getter()")
        return self._imageData
        
    @imagedata.setter
    def imagedata(self, imagedata):
        logging.debug("In VtkSliceImagePlane::imagedata.setter()")
        self._imageData = imagedata
        
    @property
    def planeCutter(self):
        logging.debug("In VtkSliceImagePlane::planeCutter.getter()")
        self._planeCutter.SetNormal(self._planeSource.GetNormal())
        self._planeCutter.SetOrigin(self._planeSource.GetOrigin())
        return self._planeCutter
        
    @property
    def input(self):
        logging.debug("In VtkSliceImagePlane::input.getter()")
        return self._input
        
    @input.setter
    def input(self, input):
        logging.debug("In VtkSliceImagePlane::input.setter()")
        if isinstance(input, vtk.vtkDataSet):
            try:
                self._imageData = vtk.vtkImageData.SafeDownCast(
                                                    input.GetOutput())
            except AttributeError, e:
                self._imageData = vtk.vtkImageData.SafeDownCast(input)
        elif isinstance(input, vtk.vtkProp3D):
            try:
                self._imageData = vtk.vtkProp.SafeDownCast(input.GetOutput())
            except AttributeError, e:
                self._imageData = vtk.vtkProp.SafeDownCast(input)
        else:
            try:
                self._imageData = vtk.vtkImageData.SafeDownCast(
                                                    input.GetOutput())
            except AttributeError, e:
                self._imageData = vtk.vtkImageData.SafeDownCast(input)
               
        range = self._imageData.GetScalarRange()
        if not self._userControlledLookupTable:
            self._lookupTable.SetTableRange(range[0], range[1])
            self._lookupTable.Build()
        
        self._originalWindow = range[1] - range[0]
        self._originalLevel = 0.5*(range[0] + range[1])
        
        
        if abs(self._originalWindow) < 0.001:
            self._originalWindow = 0.001 * (-1 if self._originalWindow < 0 else 1)
        if abs(self._originalLevel) < 0.001:
            self._originalLevel = 0.001 * (-1 if self._originalLevel < 0 else 1)
            
        
        self.windowLevel(self._originalWindow, self._originalLevel)
    
    def updateSliceAndPath(self, slice, slideFunction = None):        
        self._slideFunction = slideFunction
        self._slice = slice
        if not self._slideFunction:
            self.createDefaultSliceFunction()
        self.updatePlane()
    
    def setSlice(self, slice, slideFunction = None):        
        self._slideFunction = slideFunction
        self._slice = slice
        
        if not self._slideFunction:
            self.createDefaultSliceFunction()
            self.actualPosition = 0
        
        self._reslice = vtk.vtkImageReslice()
        self._reslice.SetInput(self._imageData)
        self._reslice.SetInformationInput(self._imageData)
        self._reslice.SetInterpolationModeToLinear()
        self._reslice.SetOutputDimensionality(2)
        self._reslice.SetBackgroundLevel( -1024 )
        
        self._colorMap.SetInputConnection(self._reslice.GetOutputPort())
        
        self._slab = vtk.vtkImageSlab()
        self._slab.TrapezoidIntegrationOff()
        self._slab.SetOperationToMax()
        
        self._texture.SetInput(self._colorMap.GetOutput())
        self._texture.SetInterpolate(self._textureInterpolate)
        
        self.planeOrientation = self._planeOrientation
        self.startWindowLevel()
        
#        self._level = vtk.vtkImageMapToWindowLevelColors()
#        self._level.SetOutputFormatToLuminance()
#        self._level.SetInputConnection(self._colorMap.GetOutputPort())
#        self._level.SetWindow(255.0)
#        self._level.Update()
#        self._level.UpdateWholeExtent()
        
#        image_actor = vtk.vtkImageActor()
#        image_actor.SetInput(self._level.GetOutput())
#        self.vtkImageActor = image_actor
        
    def getBounds(self):
        origin2 = self._imageData.GetOrigin()
        extent = self._imageData.GetWholeExtent()
        spacing = self._imageData.GetSpacing()
        
        return [origin2[0] + spacing[0]*extent[0], # xmin
                origin2[0] + spacing[0]*extent[1], # xmax
                origin2[1] + spacing[1]*extent[2], # ymin
                origin2[1] + spacing[1]*extent[3], # ymax
                origin2[2] + spacing[2]*extent[4], # zmin
                origin2[2] + spacing[2]*extent[5]] # zmax

    def createDefaultSliceFunction(self):
#        :/ mas saiu
        p = self._slice.plane
        
        center  = p.GetCenter()
        normal  = p.GetNormal()
        line = [center, [pp + n1 for pp, n1 in zip(center, normal)]]
        planes = []
        
        bounds = self.getBounds()
        
        p1 = vtk.vtkPlaneSource()
        p1.SetOrigin(bounds[0], bounds[2], bounds[4])
        p1.SetPoint1(bounds[1], bounds[2], bounds[4])
        p1.SetPoint2(bounds[0], bounds[3], bounds[4])
        p1.Update()
        p1.type = "inferior"
        planes.append(p1)
        
        p1 = vtk.vtkPlaneSource()
        p1.SetOrigin(bounds[0], bounds[2], bounds[4])
        p1.SetPoint1(bounds[0], bounds[2], bounds[5])
        p1.SetPoint2(bounds[0], bounds[3], bounds[4])
        p1.Update()
        p1.type = "rigth"
        planes.append(p1)
        
        p1 = vtk.vtkPlaneSource()
        p1.SetOrigin(bounds[0], bounds[2], bounds[4])
        p1.SetPoint1(bounds[1], bounds[2], bounds[4])
        p1.SetPoint2(bounds[0], bounds[2], bounds[5])
        p1.Update()
        p1.type = "anterior" 
        planes.append(p1)
        
        p1 = vtk.vtkPlaneSource()
        p1.SetOrigin(bounds[1], bounds[3], bounds[5])
        p1.SetPoint1(bounds[1], bounds[3], bounds[4])
        p1.SetPoint2(bounds[1], bounds[2], bounds[5])
        p1.Update()
        p1.type = "left" 
        planes.append(p1)
        
        p1 = vtk.vtkPlaneSource()
        p1.SetOrigin(bounds[1], bounds[3], bounds[5])
        p1.SetPoint1(bounds[1], bounds[3], bounds[4])
        p1.SetPoint2(bounds[0], bounds[3], bounds[5])
        p1.Update()
        p1.type = "posterior"
        planes.append(p1)
        
        p1 = vtk.vtkPlaneSource()
        p1.SetOrigin(bounds[1], bounds[3], bounds[5])
        p1.SetPoint1(bounds[1], bounds[2], bounds[5])
        p1.SetPoint2(bounds[0], bounds[3], bounds[5])
        p1.Update()
        p1.type = "superior"
        planes.append(p1)
        
        def inbounds(point):
            return point[0] - bounds[0] > -0.01 and bounds[1]-point[0] > -0.01 and\
                   point[1] - bounds[2] > -0.01 and bounds[3]-point[1] > -0.01 and\
                   point[2] - bounds[4] > -0.01 and bounds[5]-point[2] > -0.01
                     
        
        def distance_compare(x, y):
            result = intersect_line_with_plane(line[0], line[1], x.GetNormal(), x.GetCenter())
            result2 = intersect_line_with_plane(line[0], line[1], y.GetNormal(), y.GetCenter())            
            if result == None or not inbounds(result):
                distx = sys.maxint
            else:
                distx = math.sqrt(vtk.vtkMath.Distance2BetweenPoints(line[0], result))
                
            if result2 == None or not inbounds(result2):
                disty = sys.maxint
            else:
                disty = math.sqrt(vtk.vtkMath.Distance2BetweenPoints(line[0], result2))
            
            if distx > disty:
                return 1
            if distx == disty:
                return 0
            return -1
        planes.sort(cmp=distance_compare)
        
        firstPlane = planes[0]
        secondPlane =planes[1]
        
        fPoint = intersect_line_with_plane(line[0], line[1], firstPlane.GetNormal(), firstPlane.GetCenter())
        sPoint = intersect_line_with_plane(line[0], line[1], secondPlane.GetNormal(), secondPlane.GetCenter())
        for plane in planes:
            intersect = intersect_line_with_plane(line[0], line[1], plane.GetNormal(), plane.GetCenter())
            if intersect != None:
                if math.sqrt(vtk.vtkMath.Distance2BetweenPoints(fPoint, intersect)) > 0.1:
                    sPoint = intersect
                    break
                
        fDist = math.sqrt(vtk.vtkMath.Distance2BetweenPoints(fPoint, center))
        sDist = math.sqrt(vtk.vtkMath.Distance2BetweenPoints(sPoint, center))
        p.Push(0.1)
        center  = p.GetCenter()
        normal  = p.GetNormal()
        line = [center, [pp + n1 for pp, n1 in zip(center, normal)]]
        fDist2 = math.sqrt(vtk.vtkMath.Distance2BetweenPoints(fPoint, center))
        sDist2 = math.sqrt(vtk.vtkMath.Distance2BetweenPoints(sPoint, center))
        p.Push(-0.1)
        
        if fDist2 < fDist and sDist2 > sDist:
            aux = sPoint
            sPoint = fPoint 
            fPoint = aux
        self._slideFunction = [fPoint, sPoint]
        
        
    @property
    def planeOrientation(self):
        logging.debug("In VtkSliceImagePlane::planeOrientation.getter()")
        return self._planeOrientation
        
    @planeOrientation.setter
    def planeOrientation(self, value):
        logging.debug("In VtkSliceImagePlane::planeOrientation.setter()")
        self._planeOrientation = value
        
    @property
    def planeSource(self):
        logging.debug("In VtkSliceImagePlane::planeSource.getter()")
        return self._planeSource
        
    @planeSource.setter
    def planeSource(self, planeSource):
        logging.debug("In VtkSliceImagePlane::picker.setter()")    
        
    @property
    def picker(self):
        logging.debug("In VtkSliceImagePlane::picker.getter()")
        return self._picker
        
    @picker.setter
    def picker(self, picker):
        logging.debug("In VtkSliceImagePlane::picker.setter()")
        # we have to have a picker for slice motion, window level and 
        # cursor to work
        if self._planePicker != picker:
            temp = self._planePicker
            self._planePicker = picker
            if temp:
                temp.UnRegister(self.interactor)
            
            delPicker = 0
            if self._planePicker == 0:
                self._planePicker = vtk.vtkCellPicker()
                vtk.vtkCellPicker.SafeDownCast(self._planePicker) \
                    .SetTolerance(0.0001)
                delPicker = 1
            
            self._planePicker.Register(self.interactor)
            self._planePicker.AddPickList(self._texturePlaneActor)
            self._planePicker.PickFromListOn()
            
            if delPicker:
                del self._planePicker
        self._picker = picker
        
    @property
    def transform(self):
        logging.debug("In VtkSliceImagePlane::transform.getter()")
        return self._transform
        
    @transform.setter
    def transform(self, transform):
        logging.debug("In VtkSliceImagePlane::transform.setter()")
        #Todo checkar inclinacao de multiplos planos / redimensionar width e height 
#        for slice in self.slices:
#            slice.plane.SetOrigin(transform.TransformPoint(slice.plane.GetOrigin()))
#            slice.plane.SetPoint1(transform.TransformPoint(slice.plane.GetPoint1()))
#            slice.plane.SetPoint2(transform.TransformPoint(slice.plane.GetPoint2()))
        self.camera.ApplyTransform(transform)
        self.updatePlane()
        self.buildRepresentation()
        self.updatePlaneCutter()
        self.modified() 
        self._transform.Concatenate(transform.GetMatrix())
    
    @property
    def topLeftTextActor(self):
        logging.debug("In VtkSliceImagePlane::topLeftTextActor.getter()")
        return self._topLeftTextActor
       
    @topLeftTextActor.setter
    def topLeftTextActor(self, topLeftTextActor):
        logging.debug("In VtkSliceImagePlane::topLeftTextActor.setter()")
        self._topLeftTextActor = topLeftTextActor
    
    @property
    def bottomLeftTextActor(self):
        logging.debug("In VtkSliceImagePlane::bottomLeftTextActor.getter()")
        return self._bottomLeftTextActor
       
    @bottomLeftTextActor.setter
    def bottomLeftTextActor(self, bottomLeftTextActor):
        logging.debug("In VtkSliceImagePlane::bottomLeftTextActor.setter()")
        self._bottomLeftTextActor = bottomLeftTextActor
    
    @property
    def slicePosition(self):
        logging.debug("In VtkSliceImagePlane::slicePosition.getter()")
        
#        TODO proporcional ao tamanho da linha
        
        
    @slicePosition.setter
    def slicePosition(self, position):
        logging.debug("In VtkSliceImagePlane::slicePosition.setter()")
        self.actualPosition = position
        self.slicePositionFunction(position)
        
        self.updatePlane()
#        self.buildRepresentation()
        self.updatePlaneCutter()
        self.modified()
    
    
    def slicePositionFunction(self, newPosition):
        sum = 0
        anterior = self._slideFunction[0]
        newPosition = newPosition * self._sliceThickness
        for point in self._slideFunction:
            actual = point 
            dist = math.sqrt(vtk.vtkMath.Distance2BetweenPoints(anterior, actual))
            if sum + dist >= newPosition:
                break
            sum = sum + dist
            anterior = point
        if anterior == actual:
            if newPosition > 0:
                anterior = self._slideFunction[-2]
                actual = self._slideFunction[-1]
            else:
                anterior = self._slideFunction[0]
                actual = self._slideFunction[1]
                sum = newPosition
    
        normal = [p1-p2 for p1, p2 in zip(anterior, actual)]
        vtk.vtkMath.Normalize(normal)
        self._slice.setNormal(normal)
        self._slice.setCenter(anterior)
        self._slice.push(-(newPosition - sum))
    
    def getSlicePositionNormal(self, position):
        sum = 0
        anterior = self._slideFunction[0]
        newPosition = position * self._sliceThickness
        for point in self._slideFunction:
            actual = point 
            dist = math.sqrt(vtk.vtkMath.Distance2BetweenPoints(anterior, actual))
            if sum + dist > newPosition:
                break
            sum = sum + dist
            anterior = point
        if anterior == actual:
            if newPosition > 0:
                anterior = self._slideFunction[-2]
                actual = self._slideFunction[-1]
            else:
                anterior = self._slideFunction[0]
                actual = self._slideFunction[1]
                sum = newPosition
    
        normal = [p1-p2 for p1, p2 in zip(anterior, actual)]
        vtk.vtkMath.Normalize(normal)
        return normal
        
           
    @property
    def sliceThickness(self):
        return self._sliceThickness
    
    @sliceThickness.setter
    def sliceThickness(self, thickness):
        self._sliceThickness = thickness
    
    @property
    def slabThickness(self):
        return self._slabThickness
    
    @slabThickness.setter
    def slabThickness(self, slabThickness):
        if slabThickness < 0:
            return
        
        if slabThickness != self.slabThickness:
            if slabThickness > 0:
                if self.slabThickness == 0:
                    self._slab.SetInputConnection(self._reslice.GetOutputPort())
                    self._colorMap.SetInputConnection(self._slab.GetOutputPort())
                    self._reslice.SetOutputDimensionality(3)
            else:
                self._colorMap.SetInputConnection(self._reslice.GetOutputPort())
                self._slab.SetInputConnection(None)
                self._reslice.SetOutputDimensionality(2)
        self._slabThickness = slabThickness
                
            
    @property
    def slabSpacing(self):
        return self._slabSpacing
    
    @slabSpacing.setter    
    def slabSpacing(self, slabSpacing):
        self._slabSpacing = slabSpacing
     
    @property
    def slice(self):
        return self._slice
    
    @slice.setter
    def slice(self, slice):
        self._slice = slice
     
    def updatePlaneCutter(self): 
        self._planeCutter.SetNormal(self._planeSource.GetNormal())
        self._planeCutter.SetOrigin(self._planeSource.GetOrigin())
        
   
    @property
    def pushByScalar(self):
        logging.debug("In VtkSliceImagePlane::pushScalar.getter()")
        return 0
        
    @pushByScalar.setter
    def pushByScalar(self, value):
        logging.debug("In VtkSliceImagePlane::pushScalar.setter()")
        v = [n*value for n in self._planeSource.GetNormal()]
        self._planeSource.Push(
            vtk.vtkMath.Dot(v, self._planeSource.GetNormal()))
        
    def enabled(self, enabling=True):
        logging.debug("In VtkSliceImagePlane::enabled()")
        
        if not self.interactor:
            raise Exception("The interactor must be set prior to " \
                            "enabling/disabling widget")
        
        if enabling:
            if self._enabled: # already enabled, just return
                return

        if not self.renderer:
            self.renderer = self.interactor.FindPokedRenderer(
                    self.interactor.GetLastEventPosition()[0],
                    self.interactor.GetLastEventPosition()[1])
            if not self.renderer:
                return
        self._enabled = True
        
        #we have to honour this ivar: it could be that this->Interaction was
        # set to off when we were disabled
        if self.interactor:
            self.addObservers()
                
        # Add the plane
        #self.renderer.AddViewProp(self._planeOutlineActor)
        self._planeOutlineActor.SetProperty(self._planeProperty)
        
        # add the TexturePlaneActor
        if self._textureVisibility:
            self.renderer.AddViewProp(self._texturePlaneActor)
        self._texturePlaneActor.SetProperty(self._texturePlaneProperty)
        self._texturePlaneActor.PickableOn()
        
        # Add the cross-hair cursor
        self.renderer.AddViewProp(self._cursorActor)
        self._cursorActor.SetProperty(self._cursorProperty)
        
        # Add the margins
        #self.renderer.AddViewProp(self._marginActor)
        self._marginActor.SetProperty(self._marginProperty)
        
        # Add the image data annotation
        self.renderer.AddViewProp(self._topLeftTextActor)
        self.renderer.AddViewProp(self._bottomLeftTextActor)
        
        #Add directions
        self.renderer.AddActor2D(self._topDirectionActor)
        self.renderer.AddActor2D(self._bottomDirectionActor)
        self.renderer.AddActor2D(self._leftDirectionActor)
        self.renderer.AddActor2D(self._rightDirectionActor)
        
        self.renderer.SetBackground(0, 0, 0)
        
        self.renderer.ResetCamera(self.imageBounds)
        
    def scale(self, pt1, pt2):
        logging.debug("In VtkSliceImagePlane::scale()")
        
    def rotate(self, pt1, pt2):
        logging.debug("In VtkSliceImagePlane::rotate()")
        
    def spin(self, pt1, pt2):
        logging.debug("In VtkSliceImagePlane::spin()")
        # Disable cursor snap
        self._planeOrientation = 3
        
        # Get the motion vector, in world coords
        v = [p2-p1 for p1, p2 in zip(pt1, pt2)]
        
        # Plane center and normal before transform
        wc = self._planeSource.GetCenter()
        wn = self._planeSource.GetNormal()
        
        # Radius vector from center to cursor position
        rv = [p2[0]-wc[0], p2[1]-wc[1], p2[2]-wc[2]]
        
        # Distance between center and cursor location
        rs = vtk.vtkMath.Normalize(rv)
        
        # Spin direction
        crossWvRv = [0, 0, 0]
        vtk.vtkMath.Cross(wn, rv, crossWvRv)
        
        # Sping angle
        dw = vtk.vtkMath.DegreesFromRadians(vtk.vtkMath.Dot(v, crossWvRv)/rs)
        self._transform.Identity()
        self._transform.Translate(wc[0], wc[1], wc[2])
        self._transform.RotateWXYZ(dw, wn)
        self._transform.Translate(-wc[0], -wc[1], -wc[2])
        
        newpt = [0, 0, 0]
        self._transform.TransformPoint(self._planeSource.GetPoint1(), newpt)
        self._planeSource.SetPoint1(newpt)
        self._transform.TransformPoint(self._planeSource.GetPoint2(), newpt)
        self._planeSource.SetPoint2(newpt)
        self._transform.TransformPoint(self._planeSource.GetOrigin(), newpt)
        self._planeSource.SetOrigin(newpt)
        
    def addBall(self, position, color):
        sphereSource = vtk.vtkSphereSource()
        sphereSource.SetCenter(position)
        sphereSource.SetRadius(1)

        sphereMapper = vtk.vtkPolyDataMapper()
        sphereMapper.SetInputConnection(sphereSource.GetOutputPort())
        sphereMapper.SetResolveCoincidentTopologyToPolygonOffset()

        sphereActor = vtk.vtkActor()
        sphereActor.SetMapper(sphereMapper)
        sphereActor.PickableOff()
        sphereActor.GetProperty().SetColor(color)
        
        self._renderer.AddActor(sphereActor)
        
    def getOrientation(self):
        transform = vtk.vtkTransform()
        transform.Concatenate(self.camera.GetViewTransformMatrix())
        if self.resliceTransform:
            transform.Concatenate(self.resliceTransform.GetInverse())
        matrix = transform.GetMatrix()
        o = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        for i in range(3):
            for j in range(3):
                o[ 3*i + j] = matrix.GetElement( i , j);
            
        o[3] = -o[ 3];
        o[4] = -o[ 4];
        o[5] = -o[ 5];
        return o

    def computeOrientationText(self):
        vectors = self.getOrientation()
    
        leftLegend = self.getOrientationText(vectors, True)
        
        rightLegend = self.getOrientationText(vectors, False)
        
        bottomLegend = self.getOrientationText(vectors[3:], False)
        
        topLegend = self.getOrientationText(vectors[3:], True)
        self._topDirectionActor.GetMapper().SetInput(topLegend)
        self._leftDirectionActor.GetMapper().SetInput(leftLegend)
        self._bottomDirectionActor.GetMapper().SetInput(bottomLegend)
        self._rightDirectionActor.GetMapper().SetInput(rightLegend)

    def getOrientationText(self, vector, inv):
        result = ""
        if inv:
            if -vector[0] < 0:
                orientationX = QtGui.QApplication.translate("ImagePlane", 
                                                     "R", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8)
            else:
                orientationX = QtGui.QApplication.translate("ImagePlane", 
                                                     "L", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8)
            if -vector[1] < 0:
                orientationY = QtGui.QApplication.translate("ImagePlane", 
                                                     "A", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8)
            else:
                orientationY = QtGui.QApplication.translate("ImagePlane", 
                                                     "P", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8)
                
            if -vector[2] < 0:
                orientationZ = QtGui.QApplication.translate("ImagePlane", 
                                                     "I", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8)
            else:
                orientationZ = QtGui.QApplication.translate("ImagePlane", 
                                                     "S", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8)   
        else :
            if vector[0] < 0:
                orientationX = QtGui.QApplication.translate("ImagePlane", 
                                                     "R", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8)
            else:
                orientationX = QtGui.QApplication.translate("ImagePlane", 
                                                     "L", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8)
            if vector[1] < 0:
                orientationY = QtGui.QApplication.translate("ImagePlane", 
                                                     "A", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8)
            else:
                orientationY = QtGui.QApplication.translate("ImagePlane", 
                                                     "P", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8)
                
            if vector[2] < 0:
                orientationZ = QtGui.QApplication.translate("ImagePlane", 
                                                     "I", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8)
            else:
                orientationZ = QtGui.QApplication.translate("ImagePlane", 
                                                     "S", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8)
        
        absX = abs( vector[0]);
        absY = abs( vector[1]);
        absZ = abs( vector[2]);
        
        for i in range(3):
            if absX>.2 and absX>=absY and absX>=absZ:
                result = result + orientationX
                absX=0
            elif absY>.2 and absY>=absX and absY>=absZ:
                result = result + orientationY
                absY=0
            elif absZ>.2 and absZ>=absX and absZ>=absY:
                result = result + orientationZ
                absZ=0
            else: 
                break
        
        return result
    def updateDirections(self):
        if self.imagedata:
            self.computeOrientationText()
      
    def flipHorizontal(self):
        camera = self.renderer.GetActiveCamera()
        camera.Azimuth(180.0)
        self.renderer.ResetCameraClippingRange()
        self.renderer.Render()
        self.render()
        self.notifySliceChangeListeners()
        
        
    def flipVertical(self):
        camera = self.renderer.GetActiveCamera()
        camera.Elevation(180.0)
        camera.Roll(180.0)
        self.renderer.ResetCameraClippingRange()
        self.renderer.ResetCamera()
        self.render()
        self.notifySliceChangeListeners()
        
        
    def mirror(self):
        extent = self._imageData.GetWholeExtent()
        spacing = self._imageData.GetSpacing()
        origin = self._imageData.GetOrigin()
    
        center = (
            origin[0] + spacing[0] * 0.5 * (extent[0] + extent[1]),
            origin[1] + spacing[1] * 0.5 * (extent[2] + extent[3]),
            origin[2] + spacing[2] * 0.5 * (extent[4] + extent[5])
        )
        
        resliceAxes = vtk.vtkMatrix4x4()
        vtkMatrix = (
            -1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1
        )
        resliceAxes.DeepCopy(vtkMatrix)
        resliceAxes.SetElement(0, 3, center[0])
        resliceAxes.SetElement(1, 3, center[1])
        resliceAxes.SetElement(2, 3, center[2])
        
        reslice = vtk.vtkImageReslice()
        reslice.SetInput(self._imageData)
        reslice.SetInformationInput(self._imageData)
        reslice.SetResliceAxes(resliceAxes)
        reslice.SetOutputDimensionality(3)
        reslice.Update()
        
        self._imageData = reslice.GetOutput()
    
    @property
    def directionReferences(self):
        return self._directionReferences
    
    @directionReferences.setter
    def directionReferences(self, directionReferences):
        self._directionReferences = directionReferences
    
    @property
    def imageBounds(self):
        self._imageData.UpdateInformation()
        spacing = self._imageData.GetSpacing()
        origin = self._imageData.GetOrigin()
        extent = self._imageData.GetWholeExtent()
        bounds = [origin[0] + spacing[0]*extent[0], # xmin
                  origin[0] + spacing[0]*extent[1], # xmax
                  origin[1] + spacing[1]*extent[2], # ymin
                  origin[1] + spacing[1]*extent[3], # ymax
                  origin[2] + spacing[2]*extent[4], # zmin
                  origin[2] + spacing[2]*extent[5]] # zmax
        return bounds
    
    @property
    def resliceBounds(self):
        imageData = self._reslice.GetOutput()
        imageData.UpdateInformation()
        spacing = imageData.GetSpacing()
        origin = imageData.GetOrigin()
        extent = imageData.GetWholeExtent()
        bounds = [origin[0] + spacing[0]*extent[0], # xmin
                  origin[0] + spacing[0]*extent[1], # xmax
                  origin[1] + spacing[1]*extent[2], # ymin
                  origin[1] + spacing[1]*extent[3], # ymax
                  origin[2] + spacing[2]*extent[4], # zmin
                  origin[2] + spacing[2]*extent[5]] # zmax
        return bounds

    @property
    def cubeBounds(self):
        originalBounds = self.imageBounds
        corners = []
        corners.append([originalBounds[0],originalBounds[2],originalBounds[4]])
        corners.append([originalBounds[0],originalBounds[2],originalBounds[5]])
        corners.append([originalBounds[0],originalBounds[3],originalBounds[4]])
        corners.append([originalBounds[0],originalBounds[3],originalBounds[5]])
        corners.append([originalBounds[1],originalBounds[2],originalBounds[4]])
        corners.append([originalBounds[1],originalBounds[2],originalBounds[5]])
        corners.append([originalBounds[1],originalBounds[3],originalBounds[4]])
        corners.append([originalBounds[1],originalBounds[3],originalBounds[5]])
        
        bounds = [sys.maxint, -sys.maxint +1, sys.maxint, -sys.maxint +1, sys.maxint, -sys.maxint +1]
        
        for cornerO in corners:
            corner = list(self.transform.TransformPoint(cornerO))
            for i in range(3):
                if corner[i] < bounds[i * 2]:
                    bounds[i * 2] = corner[i] 
                if corner[i] > bounds[i * 2 + 1]:
                    bounds[i * 2 + 1] = corner[i]
        return bounds
    
    @property
    def resliceTransform(self):
        logging.debug("In VtkSliceImagePlane::transform.getter()")
        return self._resliceTransform
        
    @resliceTransform.setter
    def resliceTransform(self, resliceTransform):
        self._resliceTransform = resliceTransform 
        
    @property
    def parent(self):
        return self._parent
    
    @parent.setter
    def parent(self, parent):
        self._parent = parent
     
    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, id):
        self._id = id
    
    @parent.setter
    def parent(self, parent):
        self._parent = parent
        
        
    def getSlideSize(self):
        return self.getSlideFunctionSize()
            
    def getSlideFunctionSize(self):
        sum = 0
        p0 = self._slideFunction[0]
        for point in self._slideFunction:
            sum = sum + math.sqrt(vtk.vtkMath.Distance2BetweenPoints(p0, point))
            p0 = point
        return sum / self._sliceThickness
    
    def toOriginalView(self, point):
        return point
    
    def fromOriginalView(self, point):
        return point
    
    def incrementReferenceCount(self):
        self._referenceCount  = self._referenceCount + 1 
    
    def decrementReferenceCount(self):
        self._referenceCount  = self._referenceCount - 1
        
    def getPlane(self):
        return self._parent
    
    @property
    def referenceCount(self):
        return self._referenceCount
    
    def reset(self):
        self.transform = self.transform.GetInverse()
        self.updateCamera()
        self.renderer.ResetCamera()
        self.renderer.ResetCameraClippingRange()
        self.window.Render()
    
    def save(self):
        data = {"id" : self._id, 
                "sliceThickness" : self._sliceThickness, 
                "slabSpacing" : self._slabSpacing, 
                "slabThickness" : self._slabThickness,
                "sliceWidgets" : [ plane.scene._id for plane in self.parent._referencedPlanes ]
                }
        if self.planeOrientation == self.PLANE_ORIENTATION_PANORAMIC_SLICE:
            data["slice"] = self.slice.save()
            data["path"] = self._slideFunction
        save = {"planeOrientation" : self._planeOrientation, "data" : data}
        return save
    