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


from data.imagedata import VtkImageData
from ..utils.msmath import intersect_line_with_plane
from imageplane import VtkImagePlane
from sliceplanewidget import SlicePlaneWidget
from panoramicwidget import PanoramicWidget

class VtkMultiSliceImagePlane(VtkImageData, VtkImagePlane): 
    PLANE_ORIENTATION_SAGITTAL = 0
    PLANE_ORIENTATION_CORONAL = 1
    PLANE_ORIENTATION_AXIAL = 2
    PLANE_ORIENTATION_VOLUME = -1
    
    def __init__(self, vtkInteractor, parent):
        logging.debug("In VtkMultiSliceImagePlane::__init__()")
        super(VtkMultiSliceImagePlane, self).__init__(vtkInteractor)
        
        self._firstUpdate = True
        self._parent = parent
        self._planeOrientation = VtkMultiSliceImagePlane.PLANE_ORIENTATION_AXIAL
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
        self._slabSpacing = [.4, .4, .6]
        
        # Represent the plane's outline
        self._planeSource = vtk.vtkPlaneSource()
        self._planeSource.SetXResolution(1)
        self._planeSource.SetYResolution(1)
        self._planeOutlinePolyData = vtk.vtkPolyData()
        self._planeOutlineActor = vtk.vtkActor()
        
        # Represent the resliced image plane
        self._colorMap = vtk.vtkImageMapToColors()
        self._resliceAxes = vtk.vtkMatrix4x4()
        self._texture = vtk.vtkTexture()
        self._texturePlaneActor = vtk.vtkActor()
        self._texturePlaneActorColor = (0.5, 0.5, 0.5)
        self._texturePlaneWidgetActor = PanoramicWidget()
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
        
        self._transformListeners = []
        self._sliceChangeListeners = []
        self._lineWidgets = dict()


    def close(self):
        self._parent = None
        self.camera.RemoveObserver(self.cameraEvent)
        self._input = None
        self._interactor._RenderWindow = None
        self._imageData = None
        self.processEvents = None
        
        self._parent = None
        for slab in self._imageSlabs:
            slab.SetInputConnection(None)
            slab.GetOutput().ReleaseData()
        self._colorMap.SetInput(None)
        self._texture.SetInputConnection(None)
        self._texture.ReleaseGraphicsResources(self.window)
        self.renderer.RemoveViewProp(self._texturePlaneActor)
        self._texturePlaneActor.SetMapper( None )
        self._texturePlaneActor.SetTexture(None)
        self._texturePlaneActor.ReleaseGraphicsResources(self.window)
        
        for event in self.events:
            self._interactor.RemoveObserver(event)
        self.camera.RemoveObserver(self.cameraEvent)
        
        super(VtkMultiSliceImagePlane, self).destroy()
        
        self._input = None
        self._imageData = None
        self.processEvents = None
        for reslice in self._reslices:
            reslice.GetOutput().ReleaseData()
       
        self.__dict__.clear()
        
       
          
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
        logging.debug("In VtkMultiSliceImagePlane::onLeftButtonDown()")
        if self._leftButtonAction == "cursor":
            self.startCursor()
        elif self._leftButtonAction == "slice-motion":
            self.startSliceMotion()
        elif self._leftButtonAction == "window-levels":
            self.startWindowLevel()
    
    def onLeftButtonUp(self):
        logging.debug("In VtkMultiSliceImagePlane::onLeftButtonUp()")
        
        print "opa"
#        if self._leftButtonAction == "cursor":
#            self.stopCursor()
#        elif self._leftButtonAction == "slice-motion":
#            self.stopSliceMotion()
#        elif self._leftButtonAction == "window-levels":
#            self.stopWindowLevel()
            
    def onMiddleButtonDown(self):
        logging.debug("In VtkMultiSliceImagePlane::onMiddleButtonDown()")
        if self._middleButtonAction == "cursor":
            self.startCursor()
#        elif self._middleButtonAction == "slice-motion":
#            self.startSliceMotion()
        elif self._middleButtonAction == "window-levels":
            self.startWindowLevel()
    
    def onMiddleButtonUp(self):
        logging.debug("In VtkMultiSliceImagePlane::onMiddleButtonUp()")
        if self._middleButtonAction == "cursor":
            self.stopCursor()
        elif self._middleButtonAction == "slice-motion":
            self.stopSliceMotion()
        elif self._middleButtonAction == "window-levels":
            self.stopWindowLevel()
            
    def onRightButtonDown(self):
        logging.debug("In VtkMultiSliceImagePlane::onRightButtonDown()")
        if self._rightButtonAction == "cursor":
            self.startCursor()
        elif self._rightButtonAction == "slice-motion":
            self.startSliceMotion()
        elif self._rightButtonAction == "window-levels":
            self.startWindowLevel()
    
    def onRightButtonUp(self):
        logging.debug("In VtkMultiSliceImagePlane::onRightButtonUp()")
        if self._rightButtonAction == "cursor":
            self.stopCursor()
        elif self._rightButtonAction == "slice-motion":
            self.stopSliceMotion()
        elif self._rightButtonAction == "window-levels":
            self.stopWindowLevel()
            
    def onMouseMove(self):
        logging.debug("In VtkMultiSliceImagePlane::onMouseMove()")
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
        logging.debug("In VtkMultiSliceImagePlane::onChar()")
        if self.interactor.GetKeyCode() == "r" \
           or self.interactor.GetKeyCode() == "R":
            if self.interactor.GetShiftKey() or self.interactor.GetControlKey():
                self.windowLevel(self._originalWindow, self._originalLevel)
            else:
                self.interactorStyle.OnChar()
        else:
            self.interactorStyle.OnChar()
            
    def startCursor(self):
        logging.debug("In VtkMultiSliceImagePlane::startCursor()")
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
            self.activateCursor(False)
            self.activateText(False)
            return
        else:
            self._state = "cursoring"
            self.highlightPlane(True)
            self.activateCursor(True)
            self.activateText(True)
            self.updateCursor(X, Y)
            self.manageTextDisplay()
        
        #self.startInteraction()
        self.window.Render()
        
    def startCursor(self):
        logging.debug("In VtkMultiSliceImagePlane::startCursor()")
        if self._state == "outside" or self._state == "start":
            return
        self._state = "start"
        self.highlightPlane(False)
        self.activateCursor(False)
        self.activateText(False)
        
        #self.endInteraction()
        self.window.Render()
        
    def startSliceMotion(self):
        logging.debug("In VtkMultiSliceImagePlane::startSliceMotion()")
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
        logging.debug("In VtkMultiSliceImagePlane::stopSliceMotion()")
        if self._state == "outside" or self._state == "start":
            return
        self._state = "start"
        self.highlightPlane(False)
        self.activateMargins(False)
        
        #self.interactor.EndInteraction()
        self.window.Render()
        
    def startWindowLevel(self):
        logging.debug("In VtkMultiSliceImagePlane::startWindowLevel()")
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
                if node.GetViewProp() == vtk.vtkProp.SafeDownCast(
                                                    self._texturePlaneActor):
                    found = True
                    break
                
        self._initialWindow = self._currentWindow
        self._initialLevel = self._currentLevel
                 
        self.highlightPlane(True)
        self.activateMargins(True)
        self._startWindowLevelPositionX = X
        self._startWindowLevelPositionY = Y
        self.manageTextDisplay()
        
        self.window.Render()
        
    def stopWindowLevel(self):
        logging.debug("In VtkMultiSliceImagePlane::stopWindowLevel()")
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
        logging.debug("In VtkMultiSliceImagePlane::addObservers()")
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
        logging.debug("In VtkMultiSliceImagePlane::windowLevel2()")
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
        logging.debug("In VtkMultiSliceImagePlane::manageTextDisplay()")
        if not self._displayText:
            return
        
    @property
    def textureVisibility(self):
        logging.debug("In VtkMultiSliceImagePlane::textureVisibility()")
        return self._textureVisibility
        
    @textureVisibility.setter
    def textureVisibility(self, flag):
        logging.debug("In VtkMultiSliceImagePlane::textureVisibility()")
        if self._textureVisibility == flag:
            return
        self._textureVisibility = flag
        if self._enabled and self._textureVisibility:
            self.renderer.AddViewProp(self._texturePlaneActor)
        else:
            self.renderer.RemoveViewProp(self._texturePlaneActor)
        self.modified()
        
    def modified(self):
        logging.debug("In VtkMultiSliceImagePlane::modified()")
        self._texturePlaneActor.Modified()
        
    def resliceInterpolate(self, i):
        logging.debug("In VtkMultiSliceImagePlane::resliceInterpolate()")
        
    def createPlaneOutline(self):
        logging.debug("In VtkMultiSliceImagePlane::createPlaneOutline()")
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
        logging.debug("In VtkMultiSliceImagePlane::createDefaultLookupTable()")
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
        logging.debug("In VtkMultiSliceImagePlane::createDefaultProperties()")
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
            self._texturePlaneProperty.SetAmbient( 1 )
            self._texturePlaneProperty.SetInterpolationToFlat()
            self._texturePlaneProperty.EdgeVisibilityOn()
            self._texturePlaneProperty.SetEdgeColor( self._texturePlaneActorColor[0], self._texturePlaneActorColor[1], self._texturePlaneActorColor[2] )
        
    def createTexturePlane(self):
        logging.debug("In VtkMultiSliceImagePlane::createTexturePlane()")
        self._texture.SetInterpolate( self._textureInterpolate )
        
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
        
        self._texturePlaneActor.SetMapper(texturePlaneMapper)
        self._texturePlaneActor.SetTexture(self._texture)
        self._texturePlaneActor.PickableOn()
        #self.actor = self._texturePlaneActor
        del texturePlaneMapper

    def getLineWidget( self, scene ):

        return self._texturePlaneWidgetActor

    def getPlaneWidget( self, scene ):

        return self._texturePlaneWidgetActor

    def updateLineWidget( self ):

        widgets = [ self._lineWidgets[key] for key in self._lineWidgets.keys() ]
        for widget in widgets:
            widget.onSliceChange( self )

    def addLineWidgetFromScene( self, sceneOther ):

        if not self._lineWidgets.has_key( sceneOther ):

            actor = sceneOther.getLineWidget( self )
            sceneOther.addSliceChangeListener( actor.onSliceChange )

            self._lineWidgets[sceneOther] = actor

            self.addActor( self._lineWidgets[sceneOther] )
            self.window.Render()

    def remLineWidgetFromScene( self, sceneOther ):

        if self._lineWidgets.has_key( sceneOther ):

            actor = self._lineWidgets[sceneOther]
            sceneOther.removeSliceChangeListener( actor.onSliceChange )

            self.removeActor( actor )
            del self._lineWidgets[sceneOther]
            self.window.Render()

    def createCursor(self):
        logging.debug("In VtkMultiSliceImagePlane::createCursor()")
        
    def createMargins(self):
        logging.debug("In VtkMultiSliceImagePlane::createMargins()")
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
        logging.debug("In VtkMultiSliceImagePlane::createText()")
        
    def updatePlane(self):
        logging.debug("In VtkMultiSliceImagePlane::updatePlane()")
        if not self._imageData :
            return
        # Calculate appropriate pixel spacing for the reslicing
        #TODO Calculate :D 
        self._imageData.UpdateInformation()
        spacing = self._imageData.GetSpacing()
#        origin = self._imageData.GetOrigin()
        extent = self._imageData.GetWholeExtent()
        srange = self._imageData.GetScalarRange()
        
        for i in range(3):
            if extent[2*i] > extent[2*i + 1]:
                raise Exception("Invalid extent " \
                                "[{0}, {1}, {2}, {3}, {4}, {5}] " \
                                "Perhaps the input data is empty?" \
                                    .format(extent[0], extent[1], extent[2],
                                            extent[3], extent[4], extent[5]))
        
        self._totalWidth = 0
        
        #calculating final image width
        for slice in self._slices:
            self._totalWidth = self._totalWidth + slice.width
            
#        #calculating midleslice
#        sum = 0
#        midleSlice = self._slices[0]
#        for slice in self._slices:
#            sum = sum + slice.width
#            if sum > self._totalWidth/-2.0:
#                break
#            midleSlice = slice

        height = 0
        width = 0
        i = 0 
        
        zbounds = 0.0

        self._texturePlaneWidgetActor.removeAll()

        for slice in self._slices:
            # Generate the slicing matrix
            self._resliceAxes.Identity()
            pt1 = slice.plane.GetPoint1()
            origin = slice.plane.GetOrigin()
            planeAxis1 = [p1-o for p1, o in zip(pt1, origin)]
            pt2 = slice.plane.GetPoint2()
            planeAxis2 = [p2-o for p2, o in zip(pt2, origin)]
            
            vtk.vtkMath.Normalize(planeAxis1)
            vtk.vtkMath.Normalize(planeAxis2)
            planeAxis3 = [0.0, 0.0, 0.0]
            vtk.vtkMath.Cross(planeAxis1, planeAxis2, planeAxis3)
            vtk.vtkMath.Normalize(planeAxis3)
            
            reslice = self._reslices[i]
            reslice.SetResliceAxesDirectionCosines(planeAxis1, planeAxis2, planeAxis3)
            reslice.SetResliceAxesOrigin(slice.plane.GetOrigin())
            reslice.SetOutputOrigin(0.0, 0.0, 0.0)
            
            if self._slabThickness > 0:
                spacing = self._slabSpacing
                reslice.SetOutputExtent(0, int(slice.width /spacing[0]), 0, int(slice.height / spacing[1]), int((self._slabThickness/ spacing[2]) / -2.), int((self._slabThickness/ spacing[2]) / 2.))
            else:    
                reslice.SetOutputExtent(0, int(slice.width /spacing[0]), 0, int(slice.height / spacing[1]), 0, int(self._slabThickness/ spacing[2]))
            reslice.SetOutputSpacing(spacing[0], spacing[1], spacing[2])

            self._texturePlaneWidgetActor.addSlicePlaneWidget( SlicePlaneWidget( self._texturePlaneActorColor, slice.plane, reslice, srange ) )
            
            transform = vtk.vtkTransform()
            transform.SetMatrix(reslice.GetResliceAxes())
            transform.PreMultiply()
            transform.Translate(-(self._totalWidth / -2.0 + width), -(slice.height / -2.0), -zbounds)
            transform.Update()
            slice.setResliceTransform(transform)
            
            width = slice.width + width
            height = slice.height
            reslice.Update()
                
            i = i+1
            

        self._totalHeight = height
        
        self._sliceAppend.Update()
        self._sliceAppend.UpdateWholeExtent()
        
        #updating plane source   
        self._planeSource.SetPoint1(self._totalWidth / 2.0, self._totalHeight / -2.0, zbounds)
        self._planeSource.SetOrigin(self._totalWidth / -2.0, self._totalHeight / -2.0, zbounds)
        self._planeSource.SetPoint2(self._totalWidth / -2.0, self._totalHeight / 2.0, zbounds)

        self._planeSource.Update()
#        
#        self._planeSource.SetNormal([-z for z in self._planeSource.GetNormal()])
#
#        self._planeSource.Update()
#         
#        self.notifyTransformListeners()
        if self._firstUpdate:
            self.updateCamera()    
            self._firstUpdate = False
        
        self.notifySliceChangeListeners()

        self.updateLineWidget()
        
    def notifyTransformListeners(self):
        for listener in self._transformListeners:
            listener.updateTransform()
         
    def addTransformListener(self, listener):
        self._transformListeners.append(listener)
        
    def removeTransformListener(self, listener):
        if self._transformListeners.count(listener):
            self._transformListeners.remove(listener)
            
    def notifySliceChangeListeners(self):
        for listener in self._sliceChangeListeners:
            listener(self)
            
    def addSliceChangeListener(self, listener):
        self._sliceChangeListeners.append(listener)
        
    def removeSliceChangeListener(self, listener):
        if self._sliceChangeListeners.count(listener):
            self._sliceChangeListeners.remove(listener)
                
    def vector1(self):
        logging.debug("In VtkMultiSliceImagePlane::vector1()")
        pt1 = self._planeSource.GetPoint1()
        origin = self._planeSource.GetOrigin()
        return [p1-o for p1, o in zip(pt1, origin)]
        
    def vector2(self):
        logging.debug("In VtkMultiSliceImagePlane::vector2()")
        pt2 = self._planeSource.GetPoint2()
        origin = self._planeSource.GetOrigin()
        return [p2-o for p2, o in zip(pt2, origin)]
            
    def updateState(self):
        logging.debug("In VtkMultiSliceImagePlane::updateState()")
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
        logging.debug("In VtkMultiSliceImagePlane::buildRepresentation()")
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
        logging.debug("In VtkMultiSliceImagePlane::updateCursor()")
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
        logging.debug("In VtkMultiSliceImagePlane::updateContinuosCursor()")
        
    def updateDiscreteCursor(self, q):
        logging.debug("In VtkMultiSliceImagePlane::updateDiscreteCursor()")
        
    def updatePlacement(self):
        logging.debug("In VtkMultiSliceImagePlane::updatePlacement()")
        self.updatePlane()
        self.updateMargins()
        self.buildRepresentation()
        
    def updateMargins(self):
        logging.debug("In VtkMultiSliceImagePlane::updateMargins()")
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
        logging.debug("In VtkMultiSliceImagePlane::highlightPlane()")
        extent = self._imageData.GetWholeExtent()
        xs = extent[5] - extent[4] + 1
        scale = 150 if xs < 150 else (xs - 1) / 2.0
        center = self._planeSource.GetCenter()
        self.camera.SetPosition(center)
        up = [p2 -o for p2, o in zip(self._planeSource.GetPoint2(),  self._planeSource.GetOrigin())]
        vtk.vtkMath.Normalize(up)
        self.camera.SetViewUp(up)
        self.camera.SetFocalPoint([p1-p2 for p1, p2 in zip(center, self._planeSource.GetNormal())])
        self.camera.ComputeViewPlaneNormal()
        self.camera.OrthogonalizeViewUp()
        self.camera.ParallelProjectionOn()
        self.camera.SetParallelScale(scale)
        self.renderer.ResetCameraClippingRange()
        self.renderer.ResetCamera()
        if oldScale != None:
            self.camera.Zoom(self.camera.GetParallelScale() / oldScale)
        self.renderer.Render()
        
    def highlightPlane(self, highlight=True):
        logging.debug("In VtkMultiSliceImagePlane::highlightPlane()")
        if highlight:
            self._planeOutlineActor.SetProperty(self._selectedPlaneProperty)
            self._lastPickPosition = self._planePicker.GetPickPosition()
        else:
            self._planeOutlineActor.SetProperty(self._planeProperty)
        
    def invertTable(self):
        logging.debug("In VtkMultiSliceImagePlane::invertTable()")
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
        logging.debug("In VtkMultiSliceImagePlane::lookupTable()")
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
        logging.debug("In VtkMultiSliceImagePlane::windowLevel()")
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
        logging.debug("In VtkMultiSliceImagePlane::push()")
        v = [p2-p1 for p1, p2 in zip(pt1, pt2)]
        self._planeSource.Push(
            vtk.vtkMath.Dot(v, self._planeSource.GetNormal()))
        
    def activateCursor(self, flag):
        logging.debug("In VtkMultiSliceImagePlane::activateCursor()")
        if not self.renderer:
            return
        if flag:
            self._cursorActor.VisibilityOff()
        else:
            self._cursorActor.VisibilityOn()
            
    def activateMargins(self, flag):
        logging.debug("In VtkMultiSliceImagePlane::activateMargins()")
        if not self.renderer:
            return
        if flag:
            self._marginActor.VisibilityOff()
        else:
            self._marginActor.VisibilityOn()
            
    def activateText(self, flag):
        logging.debug("In VtkMultiSliceImagePlane::activateText()")
        if not self.renderer:
            return
        if flag:
            self._topLeftTextActor.VisibilityOff()
            self._bottomLeftTextActor.VisibilityOff()
        else:
            self._topLeftTextActor.VisibilityOn()
            self._bottomLeftTextActor.VisibilityOn()
    
    def activateDirections(self, flag):
        logging.debug("In VtkMultiSliceImagePlane::activateText()")
        if not self.renderer:
            return
#        if flag:
#            self._topDirectionActor.VisibilityOn()
#            self._bottomDirectionActor.VisibilityOn()
#            self._leftDirectionActor.VisibilityOn()
#            self._rightDirectionActor.VisibilityOn()
#        else:
#            self._topDirectionActor.VisibilityOff()
#            self._bottomDirectionActor.VisibilityOff()
#            self._leftDirectionActor.VisibilityOff()
#            self._rightDirectionActor.VisibilityOff()
            
    @property
    def imagedata(self):
        logging.debug("In VtkMultiSliceImagePlane::imagedata.getter()")
        return self._imageData
        
    @imagedata.setter
    def imagedata(self, imagedata):
        logging.debug("In VtkMultiSliceImagePlane::imagedata.setter()")
        self._imageData = imagedata
        
    @property
    def planeCutter(self):
        logging.debug("In VtkMultiSliceImagePlane::planeCutter.getter()")
        self._planeCutter.SetNormal(self._planeSource.GetNormal())
        self._planeCutter.SetOrigin(self._planeSource.GetOrigin())
        return self._planeCutter
        
    @property
    def input(self):
        logging.debug("In VtkMultiSliceImagePlane::input.getter()")
        return self._input
        
    @input.setter
    def input(self, input):
        logging.debug("In VtkMultiSliceImagePlane::input.setter()")
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
        
    
    def updateSlices(self, slices):
        if len(self._slices) != slices:
            self._slices = slices
            self._reslices = []
            self._imageSlabs = []
            for slice in self._slices:
                reslice = vtk.vtkImageReslice()
                reslice.SetInput(self._imageData)
                reslice.SetInformationInput(self._imageData)
                reslice.SetInterpolationModeToLinear()
                reslice.SetOutputDimensionality(2)
                reslice.SetBackgroundLevel(-1024)
                self._reslices.append(reslice)
                
                slab = vtk.vtkImageSlab()
                slab.TrapezoidIntegrationOff()
                slab.SetOperationToMax()
                if self.slabThickness > 0: 
                    reslice.SetOutputDimensionality(3)
                    slab.SetInputConnection(reslice.GetOutputPort())
                self._imageSlabs.append(slab)
            
            if self.slabThickness == 0:
                self.setImageAppendInputs(self._reslices)
            else:
                self.setImageAppendInputs(self._imageSlabs)
            
        self.updatePlane()
        self.notifyTransformListeners()
        
    def setImageAppendInputs(self, inputs):
        self._sliceAppend = vtk.vtkImageAppend()
        self._sliceAppend.SetAppendAxis(0)
        for input in inputs:
            self._sliceAppend.AddInputConnection(input.GetOutputPort())
        self._colorMap.SetInputConnection(self._sliceAppend.GetOutputPort())
        
    def setSlice(self, slices, slideFunction = None):
        self._slices = slices
        
        self._reslices = []
        self._imageSlabs = []
        for slice in self._slices:
            reslice = vtk.vtkImageReslice()
            reslice.SetInput(self._imageData)
            reslice.SetInformationInput(self._imageData)
            reslice.SetInterpolationModeToLinear()
            reslice.SetOutputDimensionality(2)
            reslice.SetBackgroundLevel(-1024)
            self._reslices.append(reslice)
            
            slab = vtk.vtkImageSlab()
            slab.TrapezoidIntegrationOff()
            slab.SetOperationToMax()
            self._imageSlabs.append(slab)

        self.setImageAppendInputs(self._reslices)
        
        self._texture.SetInput(self._colorMap.GetOutput())
        self._texture.SetInterpolate(self._textureInterpolate)
        
        self.planeOrientation = self._planeOrientation
        self.startWindowLevel()
        
        level = vtk.vtkImageMapToWindowLevelColors()
        level.SetOutputFormatToLuminance()
        level.SetInputConnection(self._colorMap.GetOutputPort())
        level.SetWindow(255.0)
        level.Update()
        level.UpdateWholeExtent()
        
        image_actor = vtk.vtkImageActor()
        image_actor.SetInput(level.GetOutput())
        self.vtkImageActor = image_actor
        
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
        p = self._slices[0].plane
        
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
        logging.debug("In VtkMultiSliceImagePlane::planeOrientation.getter()")
        return self._planeOrientation
        
    @planeOrientation.setter
    def planeOrientation(self, value):
        logging.debug("In VtkMultiSliceImagePlane::planeOrientation.setter()")
        self._planeOrientation = value
        
    @property
    def planeSource(self):
        logging.debug("In VtkMultiSliceImagePlane::planeSource.getter()")
        return self._planeSource
        
    @planeSource.setter
    def planeSource(self, planeSource):
        logging.debug("In VtkMultiSliceImagePlane::picker.setter()")    
        
    @property
    def picker(self):
        logging.debug("In VtkMultiSliceImagePlane::picker.getter()")
        return self._picker
        
    @picker.setter
    def picker(self, picker):
        logging.debug("In VtkMultiSliceImagePlane::picker.setter()")
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
                    .SetTolerance(0.005)
                delPicker = 1
            
            self._planePicker.Register(self.interactor)
            self._planePicker.AddPickList(self._texturePlaneActor)
            self._planePicker.PickFromListOn()
            
            if delPicker:
                del self._planePicker
        self._picker = picker
        
    @property
    def transform(self):
        logging.debug("In VtkMultiSliceImagePlane::transform.getter()")
        return self._transform
        
    @transform.setter
    def transform(self, transform):
        logging.debug("In VtkMultiSliceImagePlane::transform.setter()")
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
        logging.debug("In VtkMultiSliceImagePlane::topLeftTextActor.getter()")
        return self._topLeftTextActor
       
    @topLeftTextActor.setter
    def topLeftTextActor(self, topLeftTextActor):
        logging.debug("In VtkMultiSliceImagePlane::topLeftTextActor.setter()")
        self._topLeftTextActor = topLeftTextActor
    
    @property
    def bottomLeftTextActor(self):
        logging.debug("In VtkMultiSliceImagePlane::bottomLeftTextActor.getter()")
        return self._bottomLeftTextActor
       
    @bottomLeftTextActor.setter
    def bottomLeftTextActor(self, bottomLeftTextActor):
        logging.debug("In VtkMultiSliceImagePlane::bottomLeftTextActor.setter()")
        self._bottomLeftTextActor = bottomLeftTextActor
    
    @property
    def slicePosition(self):
        logging.debug("In VtkMultiSliceImagePlane::slicePosition.getter()")
        
#        TODO proporcional ao tamanho da linha
        
        
    @slicePosition.setter
    def slicePosition(self, position):
        logging.debug("In VtkMultiSliceImagePlane::slicePosition.setter()")
        
        if position == 0 or len(self._slices) < 2:
            self.updatePlane()
            return
        position =  position * self._sliceThickness
        midPoint = self.getSlicesBaseMidPoint()
        dist = 0
        slice = None
        
        for s in self._slices:
            d = s.getBaseCenterDistance(midPoint)
            if  d >= dist:
                dist = d
                slice = s
        originDistance = slice.getBaseCenterDistance(midPoint)
        scale = position / originDistance
        self.applyScaleToSlices(scale)
        
        self.updatePlane()
#        self.pushByScalar = position - originDistance 
#        self.buildRepresentation()
#        self.updatePlaneCutter()
        self.modified()
    
    
    
    def slicePositionFunction(self, newPosition):
        sum = 0
        anterior = self._slideFunction[0]
        newPosition = newPosition * self._sliceThickness
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
    
        normal = [p2-p1 for p1, p2 in zip(anterior, actual)]
        vtk.vtkMath.Normalize(normal)
        slice = self._slices[0]
        slice.setNormal(normal)
        slice.setCenter(anterior)
        slice.push(newPosition - sum)
        
    
    def getSlicesBaseMidPoint(self):
        first = self._slices[0].plane.GetOrigin()
        last = self._slices[-1].plane.GetPoint1()
        return [(f + l) / 2.0 for f, l in zip(first, last)]
#        xmax = -sys.maxint - 1
#        xmin = sys.maxint
#        ymax = -sys.maxint - 1
#        ymin = sys.maxint
#        zmax = -sys.maxint - 1
#        zmin = sys.maxint
#        for slice in self._slices:
#            center = slice.getBaseCenter()
#            xmax = max(xmax, center[0])
#            xmin = min(xmin, center[0])
#            ymax = max(ymax, center[1])
#            ymin = min(ymin, center[1])
#            zmax = max(zmax, center[2])
#            zmin = min(zmin, center[2])
#        return [(xmax + xmin) / 2.0, (ymax + ymin) /2.0, (zmax + zmin) /2.0]
            
        
    
        
        
    def applyScaleToSlices(self, scale):
        midPoint = self.getSlicesBaseMidPoint()
        transform = vtk.vtkTransform()
        transform.PostMultiply()
        transform.Translate(-midPoint[0], -midPoint[1], -midPoint[2])
        transform.Scale(scale, scale, scale)
        transform.Translate(midPoint)
        transform.Update()
        
        for slice in self._slices:
            origin = slice.origin
            newOrigin = list(transform.TransformPoint(origin))
            slice.setWidth(slice.width * scale)
            slice.setOrigin(newOrigin)
        
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
                    for i, reslice in enumerate(self._reslices):
                        reslice.SetOutputDimensionality(3)
                        self._imageSlabs[i].SetInputConnection(reslice.GetOutputPort())
                    self.setImageAppendInputs(self._imageSlabs)
            else:   
                for i, reslice in enumerate(self._reslices):
                    self._imageSlabs[i].SetInputConnection(None)
                    reslice.SetOutputDimensionality(2)
                self.setImageAppendInputs(self._reslices)
        self._slabThickness = slabThickness
                
            
    @property
    def slabSpacing(self):
        return self._slabSpacing
    
    @slabSpacing.setter    
    def slabSpacing(self, slabSpacing):
        self._slabSpacing = slabSpacing
     
     
    def updatePlaneCutter(self): 
        self.notifyTransformListeners()
#        self._planeCutter.SetNormal(self._planeSource.GetNormal())
#        self._planeCutter.SetOrigin(self._planeSource.GetOrigin())
        
    @property
    def blendThickness(self):
        return self._blendThickness
    
    @blendThickness.setter
    def blendThickness(self, blendTickness):
        self._blendThickness = blendTickness
    
    @property
    def blendOpacity(self):
        return self._blendOpacity
    
    @blendOpacity.setter
    def blendOpacity(self, blendOpacity):
        self._blendOpacity = blendOpacity
        
    @property
    def blendBaseOpacity(self):
        return self._blendBaseOpacity
    
    @blendBaseOpacity.setter
    def blendBaseOpacity(self, blendBaseOpacity):
        self._blendBaseOpacity = blendBaseOpacity
    
    @property
    def blendNumber(self):
        return self._blendNumber
    
    @blendNumber.setter    
    def blendNumber(self, blendNumber):
        self._blendNumber = blendNumber
            
    @property
    def pushByScalar(self):
        logging.debug("In VtkMultiSliceImagePlane::pushScalar.getter()")
        return 0
        
    @pushByScalar.setter
    def pushByScalar(self, value):
        logging.debug("In VtkMultiSliceImagePlane::pushScalar.setter()")
        v = [n*value for n in self._planeSource.GetNormal()]
        self._planeSource.Push(
            vtk.vtkMath.Dot(v, self._planeSource.GetNormal()))
        
    def enabled(self, enabling=True):
        logging.debug("In VtkMultiSliceImagePlane::enabled()")
        
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
        
#        #Add directions
#        self.renderer.AddActor2D(self._topDirectionActor)
#        self.renderer.AddActor2D(self._bottomDirectionActor)
#        self.renderer.AddActor2D(self._leftDirectionActor)
#        self.renderer.AddActor2D(self._rightDirectionActor)
        
        self.renderer.SetBackground(0, 0, 0)
        
        self.renderer.ResetCamera(self.imageBounds)
        
    def scale(self, pt1, pt2):
        logging.debug("In VtkMultiSliceImagePlane::scale()")
        
    def rotate(self, pt1, pt2):
        logging.debug("In VtkMultiSliceImagePlane::rotate()")
        
    def spin(self, pt1, pt2):
        logging.debug("In VtkMultiSliceImagePlane::spin()")
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

#    def computeOrientationText(self):
#        vectors = self.getOrientation()
#    
#        leftLegend = self.getOrientationText(vectors, True)
#        
#        rightLegend = self.getOrientationText(vectors, False)
#        
#        bottomLegend = self.getOrientationText(vectors[3:], False)
#        
#        topLegend = self.getOrientationText(vectors[3:], True)
#        self._topDirectionActor.GetMapper().SetInput(topLegend)
#        self._leftDirectionActor.GetMapper().SetInput(leftLegend)
#        self._bottomDirectionActor.GetMapper().SetInput(bottomLegend)
#        self._rightDirectionActor.GetMapper().SetInput(rightLegend)

    def getOrientationText(self, vector, inv):
        result = ""
        if inv:
            if -vector[0] < 0:
                orientationX = "R"
            else:
                orientationX = "L"
            if -vector[1] < 0:
                orientationY = "A"
            else:
                orientationY = "P"
                
            if -vector[2] < 0:
                orientationZ = "I"
            else:
                orientationZ = "S"   
        else :
            if vector[0] < 0:
                orientationX = "R"
            else:
                orientationX = "L"
            if vector[1] < 0:
                orientationY = "A"
            else:
                orientationY = "P"
                
            if vector[2] < 0:
                orientationZ = "I"
            else:
                orientationZ = "S"
        
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
        return
#        if self.imagedata:
#            self.computeOrientationText()
      
    def flipHorizontal(self):
        camera = self.renderer.GetActiveCamera()
        camera.Azimuth(180.0)
        self.renderer.ResetCameraClippingRange()
        self.renderer.Render()
        self.render()
        
        
    def flipVertical(self):
        camera = self.renderer.GetActiveCamera()
        camera.Elevation(180.0)
        camera.Roll(180.0)
        self.renderer.ResetCameraClippingRange()
        self.renderer.ResetCamera()
        self.render()

        
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
        logging.debug("In VtkMultiSliceImagePlane::transform.getter()")
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
        return self.getScaleSlideSize()
       
            
    def getSlideFunctionSize(self):
        sum = 0
        p0 = self._slideFunction[0]
        for point in self._slideFunction:
            sum = sum + math.sqrt(vtk.vtkMath.Distance2BetweenPoints(p0, point))
            p0 = point
        return sum / self._sliceThickness
    
    def getScaleSlideSize(self):
        midPoint = self.getSlicesBaseMidPoint()
        dist = 0
        slice = None
        for s in self._slices:
            d = s.getBaseCenterDistance(midPoint)
            if  d > dist:
                dist = d
                slice = s  
  
        return (dist/ self._sliceThickness) * 2
     
    
    def getOriginalPointSlice(self, originalPoint):
        result = None
        closest = None
        minDistance = sys.maxint
        minDistanceInProject = sys.maxint
        for slice in self._slices:
            dist = slice.getPointDistance(originalPoint)
            if dist < minDistance:
                minDistance = dist
                closest = slice 
            if slice.isPointInProjection(originalPoint):
                if dist < minDistanceInProject:
                    minDistanceInProject = dist
                    result = slice
        if not result:
            result = closest
        return result
        
    def getPointSlice(self, point):
        if point[0] < self._totalWidth / -2.0 + self._slices[0].width:
            return self._slices[0]
        result = self._slices[-1]
        width = self._totalWidth / -2.0
        for slice in self._slices:
            width = slice.width + width
            result = slice
            if point[0] < width:
                break
        return result
        
    def toOriginalView(self, point):
        result = point
        slice = self.getPointSlice(point)
        if (slice._resliceTransform) :
            result = list(slice._resliceTransform.TransformPoint(point))
        return result
    
    def fromOriginalView(self, point):
        result = point
        slice = self.getOriginalPointSlice(point)
        if (slice.resliceTransform):
            result = list(slice.resliceTransform.GetInverse().TransformPoint(point))
        return result
    
    def incrementReferenceCount(self):
        self._referenceCount  = self._referenceCount + 1 
    
    def decrementReferenceCount(self):
        self._referenceCount  = self._referenceCount - 1
    
    @property
    def referenceCount(self):
        return self._referenceCount
    
    @property
    def slice(self):
        return self._slices
    
    def getPlane(self):
        return self._parent
    
    def reset(self):
        self.transform = self.transform.GetInverse()
        self.updateCamera()
        self.renderer.ResetCamera(self.imageBounds)
        self.window.Render()
    
    def save(self):
        slices = []
        for slice in self._slices:
            slices.append(slice.save())
        data = {
                "id" : self._id, 
                "sliceThickness" : self._sliceThickness,
                "slices" : slices,
                "slabSpacing" : self._slabSpacing, 
                "slabThickness" : self._slabThickness,
                "sliceWidgets" : [ plane.scene._id for plane in self.parent._referencedPlanes ]
                }
        save = {"planeOrientation" : self._planeOrientation, "data" : data}
        return save
    