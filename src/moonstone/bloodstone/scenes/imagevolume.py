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
from PySide import QtGui

from data.imagedata import VtkImageData 
from .imageplane import VtkImagePlane

class VtkImageVolume(VtkImageData):
    
    def __init__(self, vtkInteractor, parent=None):
        logging.debug("In VtkImageVolume::__init__()")
        super(VtkImageVolume, self).__init__(vtkInteractor)
        self._cubeCorners = None
        self._parent = parent
        self._referenceCount = 0
        self._id = "{0}".format(self.parent.id)
        self._cubeOrientationActor = None
        self.defaultWindow = 1
        self.defaultLevel = 0.5
        self.surfaces = {}
        self.transform = vtk.vtkTransform()
        self.mapper = None
        self.__imageWidgetList = []
        
    def close(self):
        self.parent = None
        for surface in self.surfaces.values():
            surface["mapper"].RemoveAllInputs ()
            surface["mapper"].ReleaseDataFlagOn()
            surface["mapper"].Update()
            surface["volume"].SetMapper(None)
            surface["boneExtractor"].RemoveAllInputs ()
            surface["boneNormals"].SetInputConnection(None)
            surface["boneStripper"].SetInputConnection(None)
            
        self.volume.SetMapper(None)
        self.volume.SetProperty(None)
        self.mapper.RemoveAllInputs ()
        self.mapper.ReleaseDataFlagOn()
        self.mapper.Update()
        
        
        self.orientationWidget.SetInteractor(None)
        self._cubeOrientationActor.VisibilityOff()
        self.orientationWidget.Off()
        self.orientationWidget.SetOrientationMarker(None)
        self._renderer.RemoveActor(self._cubeOrientationActor)
#        ren = self._interactor._RenderWindow
        
        super(VtkImageVolume, self).destroy()
#        from meliae import scanner
#        print "start scan"
#        scanner.dump_all_objects("big.dump")
#        print "scan finished"
#        from meliae import loader
#        om = loader.load('big.dump')
#        om.remove_expensive_references()
#        om.summarize()
        
#        self._interactor.parent = None
#        self._interactor.close()
#        self._interactor.destroy()
#        self._interactor._RenderWindow = None
        self.vtkImageData = None
        self.__dict__.clear()
        
    def loadHounsfieldScales(self, scales):
        self.hounsfieldScales = {}
        for scale in scales:
            self.hounsfieldScales[scale["name"]] = scale
        
    def getPlane(self):
        return self._parent

    def updateClipPlanes(self):
        if not self.mapper or not self.cubeCorners:
            return
        
        self.updateMapperClipPlanes(self.mapper)
        for surface in self.surfaces.values():
            self.updateMapperClipPlanes(surface["mapper"])
        
    def updateMapperClipPlanes(self, mapper):
        mapper.RemoveAllClippingPlanes()
        pInferior = vtk.vtkPlane()
        pInferior.SetOrigin(self.cubeCorners[0])
        pInferior.SetNormal([p2 - p1 for (p1, p2) in zip(self.cubeCorners[0], self.cubeCorners[1])])
        pSuperior = vtk.vtkPlane()
        pSuperior.SetOrigin(self.cubeCorners[1])
        pSuperior.SetNormal([p2 - p1 for (p1, p2) in zip(self.cubeCorners[1], self.cubeCorners[0])])
        pRight = vtk.vtkPlane()
        pRight.SetOrigin(self.cubeCorners[0])
        pRight.SetNormal([p2 - p1 for (p1, p2) in zip(self.cubeCorners[0], self.cubeCorners[4])])
        pLeft = vtk.vtkPlane()
        pLeft.SetOrigin(self.cubeCorners[4])
        pLeft.SetNormal([p2 - p1 for (p1, p2) in zip(self.cubeCorners[4], self.cubeCorners[0])])
        pAnterior = vtk.vtkPlane()
        pAnterior.SetOrigin(self.cubeCorners[0])
        pAnterior.SetNormal([p2 - p1 for (p1, p2) in zip(self.cubeCorners[0], self.cubeCorners[2])])
        pPosterior = vtk.vtkPlane()
        pPosterior.SetOrigin(self.cubeCorners[2])
        pPosterior.SetNormal([p2 - p1 for (p1, p2) in zip(self.cubeCorners[2], self.cubeCorners[0])])
        mapper.AddClippingPlane(pInferior)
        mapper.AddClippingPlane(pSuperior)
        mapper.AddClippingPlane(pRight)
        mapper.AddClippingPlane(pLeft)
        mapper.AddClippingPlane(pAnterior)
        mapper.AddClippingPlane(pPosterior)

    def createActor(self, vtkImageData):
        logging.debug("In VtkImageVolume::createActor()")
        self.vtkImageData = vtkImageData
       
        self.mapper = vtk.vtkFixedPointVolumeRayCastMapper()
        self.mapper.SetInput(self.vtkImageData)#clip.GetOutput())
        
        self.updateClipPlanes()

        self.independentComponents = True
        self.scalar = self.vtkImageData.GetScalarRange()
        self.opacityWindow = self.scalar[1] - self.scalar[0]
#        print "self.scalar[1] - self.scalar[0]:", self.scalar[1] , self.scalar[0]
        self.opacityLevel = (self.scalar[1] + self.scalar[0]) / 2.0
        
         
        self.lastmousex = 0
        self.lastmousey = 0

        (xpos, ypos) = self.interactor.GetEventPosition()
        self.opacityWindow += xpos - self.lastmousex
        self.opacityLevel += ypos - self.lastmousey
        
        self.lastmousex = xpos
        self.lastmousey = ypos

        self.createCubeOrientation()

        self.colorFun = vtk.vtkColorTransferFunction()
        self.colorFun.RemoveAllPoints()
        self.opacityFun = vtk.vtkPiecewiseFunction()
        self.opacityFun.RemoveAllPoints()

        self.volumeProperty = vtk.vtkVolumeProperty()
        self.volumeProperty.SetIndependentComponents(self.independentComponents)
        self.volumeProperty.SetColor(self.colorFun)
        self.volumeProperty.SetScalarOpacity(self.opacityFun)
        self.volumeProperty.SetInterpolationTypeToLinear()

        self.volume = vtk.vtkVolume()
        self.volume.SetProperty(self.volumeProperty)
        self.volume.SetMapper(self.mapper)

        self.interactor.Modified()
        self.interactor.Render()
        
        self.mode = None
        self.changeHounsfieldMode("MIP")
            
        self.interactorStyle = vtk.vtkInteractorStyleTrackballCamera()
        self.renderer.SetBackground(0.0, 0.0, 0.0)

        self.camera.SetFocalPoint(0, 0, 0)
        self.camera.SetPosition(0, -1, 0)
        self.camera.SetViewUp(0, 0, 1)
        self.renderer.ResetCamera()
        
        
        self.defaultWindow = self.opacityWindow
        self.defaultLevel = self.opacityLevel
        self.setWindowLevel(self.opacityWindow, self.opacityLevel)
        

    def createInteractorStyle(self):
        return vtk.vtkInteractorStyleTrackballCamera()

    def addSlicePlaneWidget( self, planeWidget ):
        if  planeWidget not in self.__imageWidgetList:
            self.__imageWidgetList.append( planeWidget )
            self.addActor( planeWidget )
            self.window.Render()

    def removeSlicePlaneWidget( self, planeWidget ):
        if  planeWidget in self.__imageWidgetList:
            self.__imageWidgetList.remove( planeWidget )
            self.removeActor( planeWidget )
            self.window.Render()
        
    #This method is based on Osirix
    def createCubeOrientation(self):
        self._cubeOrientationActor = vtk.vtkAnnotatedCubeActor()
        self._cubeOrientationActor.SetXPlusFaceText(QtGui.QApplication.translate("ImagePlane", 
                                                     "L", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8))      
        self._cubeOrientationActor.SetXMinusFaceText(QtGui.QApplication.translate("ImagePlane", 
                                                     "R", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8))
        self._cubeOrientationActor.SetYPlusFaceText(QtGui.QApplication.translate("ImagePlane", 
                                                     "P", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8))
        self._cubeOrientationActor.SetYMinusFaceText(QtGui.QApplication.translate("ImagePlane", 
                                                     "A", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8))
        self._cubeOrientationActor.SetZPlusFaceText(QtGui.QApplication.translate("ImagePlane", 
                                                     "S", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8))
        self._cubeOrientationActor.SetZMinusFaceText(QtGui.QApplication.translate("ImagePlane", 
                                                     "I", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8))
        self._cubeOrientationActor.SetZFaceTextRotation(90)
        self._cubeOrientationActor.SetFaceTextScale(0.67)
        
        property = self._cubeOrientationActor.GetXPlusFaceProperty()
        property.SetColor(0, 0, 1)
        property = self._cubeOrientationActor.GetXMinusFaceProperty()
        property.SetColor(0, 0, 1)
        property = self._cubeOrientationActor.GetYPlusFaceProperty()
        property.SetColor(0, 1, 0)
        property = self._cubeOrientationActor.GetYMinusFaceProperty()
        property.SetColor(0, 1, 0)
        property = self._cubeOrientationActor.GetZPlusFaceProperty()
        property.SetColor(1, 0, 0)
        property = self._cubeOrientationActor.GetZMinusFaceProperty()
        property.SetColor(1, 0, 0)
        
        self._cubeOrientationActor.SetTextEdgesVisibility(1)
        self._cubeOrientationActor.SetCubeVisibility(1)
        self._cubeOrientationActor.SetFaceTextVisibility(1)
        
        self.orientationWidget = vtk.vtkOrientationMarkerWidget()    
        self.orientationWidget.SetInteractor(self._interactor)
        self.orientationWidget.SetViewport(0.85, 0.85, 1, 1)
        self.orientationWidget.SetOrientationMarker(self._cubeOrientationActor)
        self.orientationWidget.SetEnabled(1)
        self.orientationWidget.InteractiveOff()
        
        self.orientationWidget.On();
        
    def activateDirections(self, flag):
        if not self.renderer or not self._cubeOrientationActor:
            return
        if flag:
            self._cubeOrientationActor.VisibilityOn()
        else:
            self._cubeOrientationActor.VisibilityOff()
        
      
        
    def setWindowLevel(self, window, level):
        self.opacityWindow = window
        self.opacityLevel = level
        self.resetColorOpacityFunPoints();
        
    def resetColorOpacityFunPoints(self):        
        self.colorFun.RemoveAllPoints()
        self.opacityFun.RemoveAllPoints()
        if self.colorFunPoints:
            for point in self.colorFunPoints:
                point.set(self.colorFun, self.opacityWindow, self.opacityLevel)
        if self.opacityFunPoints:
            for point in self.opacityFunPoints:
                point.set(self.opacityFun, self.opacityWindow, self.opacityLevel)
        self.render()


    def setHounsfieldFromMap(self, hounsfieldScale):
        self.actualHounsfieldScale = hounsfieldScale            
        if self.actualHounsfieldScale.has_key("default_window"): 
            self.opacityWindow = self.actualHounsfieldScale["default_window"]
        else:
            self.opacityWindow = self.scalar[1] - self.scalar[0]
            
        if self.actualHounsfieldScale.has_key("default_level"): 
            self.opacityLevel = self.actualHounsfieldScale["default_level"]
        else:
            self.opacityLevel = (self.scalar[1] + self.scalar[0]) / 2.0
        
            
        self.defaultWindow = self.opacityWindow
        self.defaultLevel = self.opacityLevel
        
        
        self.colorFunPoints = []
        self.opacityFunPoints = []
        
        if self.actualHounsfieldScale.has_key("color_points"):
            for pointList in self.actualHounsfieldScale["color_points"]:
                for point in pointList:
                    x = point["x"]
                    r = point["r"] 
                    g = point["g"]
                    b = point["b"]
                    midpoint = None
                    if point.has_key("midpoint"):
                        midpoint = point["midpoint"]
                    sharpness = None
                    if point.has_key("sharpness"):
                        sharpness = point["sharpness"]
                    self.colorFunPoints.append(ColorTransferFunctionRGBPoint(x, r, g, b, midpoint, sharpness))
                                
        if self.actualHounsfieldScale.has_key("opacity_points"):
            for point in self.actualHounsfieldScale["opacity_points"]:
                x = point["x"]
                y = point["y"]
                midpoint = None
                if point.has_key("midpoint"):
                    midpoint = point["midpoint"]
                sharpness = None
                if point.has_key("sharpness"):
                    sharpness = point["sharpness"]
                self.opacityFunPoints.append(OpacityTransferFunctionPoint(x, y, midpoint, sharpness))
        
        if self.actualHounsfieldScale.has_key("mapper_properties"):
            mapperProperties = self.actualHounsfieldScale["mapper_properties"]
            if mapperProperties.has_key("blend_mode_to_maximum_intensity"):
                self.mapper.SetBlendModeToMaximumIntensity()
            if mapperProperties.has_key("blend_mode_to_composite"):
                self.mapper.SetBlendModeToComposite()
        if self.actualHounsfieldScale.has_key("volume_properties"):            
            volumePropertiesMap = self.actualHounsfieldScale["volume_properties"]
            if volumePropertiesMap.has_key("shade") and volumePropertiesMap["shade"]:
                self.volumeProperty.ShadeOn()            
            else:
                self.volumeProperty.ShadeOff()
            if volumePropertiesMap.has_key("ambient"):
                self.volumeProperty.SetAmbient(volumePropertiesMap["ambient"])
            if volumePropertiesMap.has_key("difuse"):
                self.volumeProperty.SetDiffuse(volumePropertiesMap["difuse"])
            if volumePropertiesMap.has_key("specular"):
                self.volumeProperty.SetSpecular(volumePropertiesMap["specular"])
            if volumePropertiesMap.has_key("specular_power"):
                self.volumeProperty.SetSpecularPower(volumePropertiesMap["specular_power"])
            if volumePropertiesMap.has_key("scalar_opacity_unit_distance"):
                self.volumeProperty.SetScalarOpacityUnitDistance(volumePropertiesMap["scalar_opacity_unit_distance"])
        self.resetColorOpacityFunPoints()
     
    def changeHounsfieldMode(self, mode):
        if mode == self.mode:
            return
        
        if self.hounsfieldScales.has_key(mode):
            self.mode = mode
            self.colorFun.RemoveAllPoints()
            self.opacityFun.RemoveAllPoints()
            self.setHounsfieldFromMap(self.hounsfieldScales[mode])
            
    def removeSurface(self, name):
        if name in self.surfaces:
            surface = self.surfaces.pop(name)
            self.removeVolume(surface["volume"])
            surface["mapper"].SetInputConnection(None)
            surface["mapper"].Update()
            surface["boneExtractor"].SetInput(None)
            surface["boneNormals"].SetInputConnection(None)
            surface["boneStripper"].SetInputConnection(None)
            surface["volume"].SetMapper(None)
            
                                    
            del surface["volume"]
            del surface["mapper"]
            del surface["boneExtractor"]
            del surface["boneNormals"]
            del surface["boneStripper"]
    
    def addSurface(self, name, value, r, g, b):
        if self.surfaces.has_key(name):
            return        
            
        surface = {}
        boneExtractor = vtk.vtkMarchingCubes()
        boneExtractor.SetInput(self.vtkImageData)
        boneExtractor.SetValue(0, value)
        surface["boneExtractor"] = boneExtractor
        
        boneNormals = vtk.vtkPolyDataNormals()
        boneNormals.SetInputConnection(boneExtractor.GetOutputPort())
        boneNormals.SetFeatureAngle(60.0)
        surface["boneNormals"] = boneNormals
        
        boneStripper = vtk.vtkStripper()
        boneStripper.SetInputConnection(boneNormals.GetOutputPort())
        surface["boneStripper"] = boneStripper
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(boneStripper.GetOutputPort())
        mapper.ScalarVisibilityOff()
        mapper.Update()
        surface["mapper"] = mapper
        
        boneProperty = vtk.vtkProperty()
        boneProperty.SetColor(r, g, b)
        
        volume = vtk.vtkActor()
        volume.SetMapper(mapper)
        volume.SetProperty(boneProperty)
        surface["volume"] = volume
        
        self.addVolume(volume)
        self.surfaces[name] = surface
        self.updateMapperClipPlanes(mapper)
        
        self.window.Render()
        
    @property
    def cubeCorners(self):
        logging.debug("In VtkImagePlane::transform.getter()")
        return self._cubeCorners
    
    @cubeCorners.setter
    def cubeCorners(self, cubeCorners):
        self._cubeCorners = cubeCorners 
        self.updateClipPlanes()
    
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

    def toOriginalView(self, point):
        return point
    
    def fromOriginalView(self, point):
        return point
    
    def incrementReferenceCount(self):
        self._referenceCount = self._referenceCount + 1 
    
    def decrementReferenceCount(self, referenceCount):
        self._referenceCount = self._referenceCount - 1
    
    @property
    def referenceCount(self):
        return self._referenceCount
    
    def reset(self):
        self.camera.SetFocalPoint(0, 0, 0)
        self.camera.SetPosition(0, -1, 0)
        self.camera.SetViewUp(0, 0, 1)
        self.renderer.ResetCamera()
        self.window.Render()
    
    def save(self):
        save =\
            {
                "planeOrientation" : VtkImagePlane.PLANE_ORIENTATION_VOLUME,
                "data" :
                        {
                            "id" : self._id,
                            "hounsfieldMode" : self.mode,
                            "window" : self.opacityWindow,
                            "level" : self.opacityLevel,
                            "sliceWidgets" : [ plane.scene._id for plane in self.parent._referencedPlanes ]
                        }
            }
        return save
    
class OpacityTransferFunctionPoint:
    def __init__ (self, x, y, midpoint = 0.5, sharpness = 0.0):
        self.x = x
        self.y = y
        #caso seja passado None
        if midpoint == None:
            self.midpoint = 0.5
        else:
            self.midpoint = midpoint
        if sharpness == None:
            self.sharpness = 0.0
        else:
            self.sharpness = sharpness
        
    def set(self, colorFunc, window, level):
        colorFunc.AddPoint(self.calcExpression(self.x, window, level), self.y, self.midpoint, self.sharpness)
    
    def calcExpression(self, value, window, level):
        return (level - window /2) + value * window
    
class ColorTransferFunctionRGBPoint:
    def __init__ (self,x, r, g, b , midpoint = 0.5, sharpness = 0.0):
        self.x = x
        self.r = r
        self.g = g
        self.b = b        
        #caso seja passado None
        if midpoint == None:
            self.midpoint = 0.5
        else:
            self.midpoint = midpoint
        if sharpness == None:
            self.sharpness = 0.0
        else:
            self.sharpness = sharpness
        
    def set(self, colorFunc, window, level):
        colorFunc.AddRGBPoint(self.calcExpression(self.x, window, level), self.r, self.g, self.b, self.midpoint, self.sharpness)
    
    def calcExpression(self, value, window, level):        
        return (level - window /2) + value * window