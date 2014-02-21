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
import copy
import time

import vtk
from PySide import QtCore, QtGui

from ..volumeview import VolumeView
from ....bloodstone.scenes.data.slice import Slice
from ..multisliceview import MultiSliceView
from ..singlesliceview import SingleSliceView
from ....bloodstone.scenes.imageplane import VtkImagePlane

class MScreen(QtGui.QMainWindow):

    def __init__(self, mWindow=None, parent=None, vtkImageData=None, cubeCorners=None, name="", creationTime=None):
        logging.debug("In MScreen::__init__()")
        super(MScreen, self).__init__(parent)
        self._name = name
        self.vtkImageData = vtkImageData
        self._ilsa = mWindow.ilsa
        self._mWindow = mWindow
        self._planes = []
        self._activePlanes = []
        self._inactivePlanes = []
        self._scenes = {}
        self.createCubeCorners(cubeCorners)
        self.createWidgets()
        self.updateWidgets()
        self.createActions()
        self._lastChildId = 0
        self._resliceTransform = None
        self._main = False
        self._menu = QtGui.QMenu()
        self._actions = {}
        self._referenceCount = 0
        if creationTime:
            self._creationTime = creationTime
        else:
            self._creationTime = time.time()
        
    def createCubeCorners(self, cubeCorners):
        if cubeCorners == None:
            cubeCorners = self.getImageDataCorners()
        self._cubeCorners = cubeCorners
        self._originalCubeCorners = copy.copy(self._cubeCorners)
        
    def getImageDataBounds(self):
        spacing = self.vtkImageData.GetSpacing()
        origin = self.vtkImageData.GetOrigin()
        extent = self.vtkImageData.GetWholeExtent()
        bounds = [origin[0] + spacing[0]*extent[0], # xmin
                  origin[0] + spacing[0]*extent[1], # xmax
                  origin[1] + spacing[1]*extent[2], # ymin
                  origin[1] + spacing[1]*extent[3], # ymax
                  origin[2] + spacing[2]*extent[4], # zmin
                  origin[2] + spacing[2]*extent[5]] # zmax
        return bounds
    
    def getImageDataCorners(self):
        bounds = self.getImageDataBounds()
        corners = []
        corners.append([bounds[0],bounds[2],bounds[4]])
        corners.append([bounds[0],bounds[2],bounds[5]])
        corners.append([bounds[0],bounds[3],bounds[4]])
        corners.append([bounds[0],bounds[3],bounds[5]])
        corners.append([bounds[1],bounds[2],bounds[4]])
        corners.append([bounds[1],bounds[2],bounds[5]])
        corners.append([bounds[1],bounds[3],bounds[4]])
        corners.append([bounds[1],bounds[3],bounds[5]])
        return corners
    
    def createPopupMenu(self):
        self.menu = QtGui.QMenu()
        for plane in self._planes:
            action = QtGui.QAction(self)
            action.setText(plane.windowTitle())
            action.setCheckable(True)
            if plane.isVisible():
                action.setChecked(True)
            else:
                action.setChecked(False)
            self.menu.addAction(action)
            self.connect(action, QtCore.SIGNAL("triggered()"),
                         plane.changeVisibility)
        pos = QtGui.QCursor.pos()
        self.menu.exec_(pos)

    def mouseReleaseEvent( self, event ):
        if event.type == QtCore.Qt.RightButton:
            self.createPopupMenu()
        
    def resizeEvent(self, event):
        logging.debug("In MScreen::resizeEvent()")
        super(MScreen, self).resizeEvent(event)
    
    def createActions(self):
        pass
 
    def createWidgets(self):
        logging.debug("In MScreen::createWidgets()")
        
        
    def updateWidgets(self):
        logging.debug("In MScreen::updateWidgets()")
        try:
            self._ilsa.loadScreen()
        except:
            logging.debug("not ready")
        for plane in self._planes:
            plane.resizeAction()
            
    def close(self, force=False, closeTab=False):
        logging.debug("In MScreen::close()")
        ps = self._planes[:]
        #self._ilsa.removeAllScenes()
        for plane in ps:
            if not force:
                self._ilsa.removeScene(plane.scene)
            self.deleteScene(plane)
        if self._main:
            self.vtkImageData.ReleaseData()
        if closeTab:
            self._mWindow.removeTab(self._mWindow.indexOf(self))
        self.vtkImageData = None

    @property
    def matrix(self):
        matrix = []
        for i in range(4):
            line = []
            for j in range(4):
                line.append(self.plane.transform.GetMatrix().GetElement(i,j))
            matrix.append(line)
        return matrix
    
    @matrix.setter
    def matrix(self, matrix):
        vtkMatrix = vtk.vtkMatrix4x4()
        for i in range(4):
            for j in range(4):
                vtkMatrix.SetElement(i, j, matrix[i][j])
        transform = vtk.vtkTransform()
        transform.SetMatrix(vtkMatrix)
        for plane in self._planes:
            if not isinstance(plane, VolumeView):
                plane.scene.transform = transform
    
    @property
    def resliceMatrix(self):
        matrix = []
        if self._resliceTransform:
            for i in range(4):
                line = []
                for j in range(4):
                    line.append(self._resliceTransform.GetMatrix().GetElement(i,j))
                matrix.append(line)
        return matrix
    
    @resliceMatrix.setter
    def resliceMatrix(self, matrix):
        transform = None
        if matrix:
            vtkMatrix = vtk.vtkMatrix4x4()
            for i in range(4):
                for j in range(4):
                    vtkMatrix.SetElement(i, j, matrix[i][j])
            transform = vtk.vtkTransform()
            transform.SetMatrix(vtkMatrix)
        for plane in self._planes:
            plane.scene._resliceTransform = transform
        self._resliceTransform = transform
        
    
    @property    
    def planes(self):
        return self._planes            
        
    def reset(self):
        self.setCubeCorners(self._originalCubeCorners)
        for plane in self.planes:
            plane.reset()
            
    def duplicate(self):
        d3 = 0
        for plane in self.planes:
            if plane.planeOrientation == VtkImagePlane.PLANE_ORIENTATION_VOLUME:
                d3 = 1
                break

        self._mWindow.createMScreensFromImagedata(self.vtkImageData, copy.copy(self._cubeCorners), self._name, d3);
                    
        
    def layout2xX(self, planes):
        logging.debug("In MScreen::layoutXxX()")
        self.createSpliters()
        # Out!
        self._planes = planes
        
        for plane in planes:
            plane.createActor(self.vtkImageData)
            plane.mScreenParent = self
            
        if len(planes) < 3: 
            if len(planes) > 0 :
                planes[0].setParent(self.hsplitter1)
            if len(planes) > 1 :
                planes[1].setParent(self.hsplitter1)
        else :
            center = len(planes) / 2
            math.ceil(center)
            for i in range(center):
                planes[i].setParent(self.hsplitter1)
            for i in range(center, len(planes)):
                planes[i].setParent(self.hsplitter2)
        
    @property
    def scenes(self):
        logging.debug("In MScreen::scenes()")
        return self._scenes
    
    def addScene(self, scenePlane):
        self.openScene(scenePlane)

    def closeScene(self, scenePlane):
        logging.debug("In MScreen::closeScene()")
        self.removeScene(scenePlane)
        
    def getPlaneSlice(self, planeOrientation):
        if planeOrientation == VtkImagePlane.PLANE_ORIENTATION_SAGITTAL:
            origin = self._cubeCorners[2]#[self._cubeBounds[0], self._cubeBounds[3], self._cubeBounds[4]]
            p1 = self._cubeCorners[0]#[self._cubeBounds[0], self._cubeBounds[2], self._cubeBounds[4]]
            p2 = self._cubeCorners[3]#[self._cubeBounds[0], self._cubeBounds[3], self._cubeBounds[5]]
        if planeOrientation == VtkImagePlane.PLANE_ORIENTATION_CORONAL:
            origin = self._cubeCorners[0]#[self._cubeBounds[0], self._cubeBounds[2], self._cubeBounds[4]]
            p1 = self._cubeCorners[4]#[self._cubeBounds[1], self._cubeBounds[2], self._cubeBounds[4]]
            p2 = self._cubeCorners[1]#[self._cubeBounds[0], self._cubeBounds[2], self._cubeBounds[5]]
        if planeOrientation == VtkImagePlane.PLANE_ORIENTATION_AXIAL:
            origin = self._cubeCorners[2]#[self._cubeBounds[0], self._cubeBounds[3], self._cubeBounds[4]]
            p1 = self._cubeCorners[6]#[self._cubeBounds[1], self._cubeBounds[3], self._cubeBounds[4]]
            p2 = self._cubeCorners[0]#[self._cubeBounds[0], self._cubeBounds[2], self._cubeBounds[4]]
#        result = [0,0,0]
#        vtk.vtkMath.Cross([b-a for a,b in zip(origin, p1)],[b-a for a,b in zip(origin, p2)], result)
#        vtk.vtkMath.Normalize(result)
#        print result
        return Slice(origin, p1, p2, math.sqrt(vtk.vtkMath.Distance2BetweenPoints(origin, p1)), 
                                     math.sqrt(vtk.vtkMath.Distance2BetweenPoints(origin, p2)))
        
    def getSlicePath(self, planeOrientation):
        result = None
        if planeOrientation == VtkImagePlane.PLANE_ORIENTATION_SAGITTAL:
            result = [[(p1 + p2)/2.0 for p1, p2 in zip(self._cubeCorners[1], self._cubeCorners[2])],
                      [(p1 + p2)/2.0 for p1, p2 in zip(self._cubeCorners[5], self._cubeCorners[6])]]
        if planeOrientation == VtkImagePlane.PLANE_ORIENTATION_CORONAL:
            result = [[(p1 + p2)/2.0 for p1, p2 in zip(self._cubeCorners[1], self._cubeCorners[4])],
                      [(p1 + p2)/2.0 for p1, p2 in zip(self._cubeCorners[3], self._cubeCorners[6])]]           
        if planeOrientation == VtkImagePlane.PLANE_ORIENTATION_AXIAL:
            result = [[(p1 + p2)/2.0 for p1, p2 in zip(self._cubeCorners[0], self._cubeCorners[6])],
                      [(p1 + p2)/2.0 for p1, p2 in zip(self._cubeCorners[1], self._cubeCorners[7])]] 
        return result
    
    def createScene(self, planeOrientation, data=None, slices = None, title = "", resize=True):
        logging.debug("In MScreen::createScene()")
        scenePlane = None
        typeCount = 0 
        for p in self._planes:
            if p.planeOrientation == planeOrientation:
                typeCount = max(typeCount, p.planeNumber)
        typeCount = typeCount + 1
        
        if planeOrientation == VtkImagePlane.PLANE_ORIENTATION_PANORAMIC:
            if slices == None:
                slices = []
                for s in data["slices"]:
                    slices.append(Slice(s["origin"], s["point1"], s["point2"], s["width"],s["height"]))
            t = QtGui.QApplication.translate("MScreen",  "Panoramic", None, QtGui.QApplication.UnicodeUTF8)
            scenePlane = MultiSliceView(self, slices = slices, title=t, planeNumber=typeCount)
            scenePlane.setObjectName("dockWidget3-{0}".format(len(self._planes)+1))
        elif planeOrientation == VtkImagePlane.PLANE_ORIENTATION_VOLUME:
            t = QtGui.QApplication.translate("MScreen", "Volume", None, QtGui.QApplication.UnicodeUTF8)
            scenePlane = VolumeView(self, cubeCorners=self._cubeCorners, title=t, planeNumber=typeCount)
            scenePlane.setObjectName("dockWidget2-{0}".format(len(self._planes)+1))
        else :
            path = None
            if planeOrientation == VtkImagePlane.PLANE_ORIENTATION_PANORAMIC_SLICE:
                if not title:
                    title = "Transversal"
                if data and data.has_key("path"):
                    path = data["path"]
                if slices == None:
                    s = data["slice"]
                    slices = Slice(s["origin"], s["point1"], s["point2"], s["width"],s["height"])
            else:
                if planeOrientation == VtkImagePlane.PLANE_ORIENTATION_AXIAL:
                    title = "Axial"
                elif planeOrientation == VtkImagePlane.PLANE_ORIENTATION_CORONAL:
                    title = "Coronal"
                elif planeOrientation == VtkImagePlane.PLANE_ORIENTATION_SAGITTAL:
                    title = "Sagittal"
                slices = self.getPlaneSlice(planeOrientation)
                path = self.getSlicePath(planeOrientation)
            t = QtGui.QApplication.translate("MScreen", title, None, QtGui.QApplication.UnicodeUTF8)
            scenePlane = SingleSliceView(self, slice = slices, planeOrientation=planeOrientation, title = t, slicePath=path, planeNumber=typeCount)
            scenePlane.setObjectName("dockWidget3-{0}".format(len(self._planes)+1))

        if scenePlane:
            areas = {QtCore.Qt.TopDockWidgetArea:0, QtCore.Qt.BottomDockWidgetArea:0}
            for plane in self._planes:
                area = self.dockWidgetArea(plane)
                areas[area] = areas[area] + 1
            if areas[QtCore.Qt.TopDockWidgetArea] < areas[QtCore.Qt.BottomDockWidgetArea]:
                self.addDockWidget(QtCore.Qt.TopDockWidgetArea, scenePlane) 
            else:
                self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, scenePlane)
            QtCore.QCoreApplication.processEvents()
            
            if resize:
                self.resize(self.sizeHint())
                            
            scenePlane.createActor(self.vtkImageData)
            self._planes.append(scenePlane)
            self._activePlanes.append(scenePlane)
            self._ilsa.addScene(scenePlane.scene)
            if data:
               scenePlane.load(data)
            self._mWindow.cameraController.updatePlanes()
        return scenePlane          

    def restoreDockGeometry(self):
        settings = QtCore.QSettings("Moonstone", "Medical");
        self.restoreGeometry(settings.value("{0}{1}geometry".format(self.id, self.name)));
        self.restoreState(settings.value("{0}{1}state".format(self.id, self.name)));
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        self._name = name
        self._mWindow.setTabText(self._mWindow.indexOf(self), name)
        self.setWindowTitle(name)
    
    def renderPlanes(self):
        for plane in self.planes:
            plane.scene.window.Render()
    
    def removeScene(self, scenePlane):
        logging.debug("In MScreen::removeScene()")
        if len(self._planes) < 2:
            return False
        self._ilsa.removeScene(scenePlane)
        self.deleteScene(scenePlane)
        return True
    
    def deleteScene(self, scenePlane):
        if self._planes.count(scenePlane) > 0: 
            self._planes.remove(scenePlane)
        if self._activePlanes.count(scenePlane) > 0:
            self._activePlanes.remove(scenePlane)
        if self._inactivePlanes.count(scenePlane) > 0:
            self._inactivePlanes.remove(scenePlane)
                                

    def save(self, fname, index, name):            
        saveScenes = []
        for plane in self.planes:
            sceneYaml = plane.scene.save()
            sceneYaml["visible"] = plane.active
            saveScenes.append(sceneYaml)
        settings = QtCore.QSettings("Moonstone", "Medical")
        settings.setValue("{0}{1}geometry".format(self.id, name), self.saveGeometry())
        settings.setValue("{0}{1}state".format(self.id, name), self.saveState()) 
        save = {"name": name, 
                "cubeCorners" : self._cubeCorners,
                "lastChildId" : self._lastChildId, 
                "scenes" : saveScenes,
                "creationTime" : self._creationTime, 
                "main" : self._main}
        
        return save
        
    def getNewChildId(self):
        self._lastChildId = self._lastChildId + 1 
        return "{0}-{1}".format(self.id, self._lastChildId)
    
    def applyCubeTransform(self, transform):
        newCorners = []
        for c in self._cubeCorners:
            newCorners.append(list(transform.TransformPoint(c)))
        self.setCubeCorners(newCorners)
        self.updateCamerasPosition()
        
    def setCubeCorners(self, newCorners):
        self._cubeCorners = newCorners
        self.recreateSlices()
    
    def centerPlanes(self):
        for p in self.planes:
            if p.planeOrientation == VtkImagePlane.PLANE_ORIENTATION_AXIAL or  \
              p.planeOrientation == VtkImagePlane.PLANE_ORIENTATION_CORONAL or \
              p.planeOrientation == VtkImagePlane.PLANE_ORIENTATION_SAGITTAL:
                p.certerSlidePosition()
        
    def recreateSlices(self):
        for p in self.planes:
            if p.planeOrientation == VtkImagePlane.PLANE_ORIENTATION_AXIAL or  \
               p.planeOrientation == VtkImagePlane.PLANE_ORIENTATION_CORONAL or \
               p.planeOrientation == VtkImagePlane.PLANE_ORIENTATION_SAGITTAL:
                slice = self.getPlaneSlice(p.planeOrientation)
                path = self.getSlicePath(p.planeOrientation)
                p.updateSliceAndPath(slice, path)
            elif p.planeOrientation == VtkImagePlane.PLANE_ORIENTATION_VOLUME:
                p.scene.cubeCorners = self._cubeCorners
                
                
    def updateCameras(self):
        for p in self.planes:
            if p.planeOrientation != VtkImagePlane.PLANE_ORIENTATION_VOLUME:
                p.scene.updateCamera()
    
    def updateCamerasPosition(self):
        for p in self.planes:
            if p.planeOrientation == VtkImagePlane.PLANE_ORIENTATION_AXIAL\
                 or p.planeOrientation == VtkImagePlane.PLANE_ORIENTATION_CORONAL \
                 or p.planeOrientation == VtkImagePlane.PLANE_ORIENTATION_SAGITTAL:
                p.scene.updateCameraPosition()
                p.scene.renderer.ResetCameraClippingRange()
                p.scene.window.Render()            
    
    @property
    def cubeCorners(self):
        return copy.deepcopy(self._cubeCorners)
        
    @property
    def lastChildId(self):
        return self._lastChildId
    
    @lastChildId.setter
    def lastChildId(self, lastChildId):
        self._lastChildId = lastChildId
    
    @property
    def resliceTansform(self):
        return self._resliceTansform
        
    @resliceTansform.setter
    def resliceTansform(self, resliceTansform):
        self._resliceTansform = resliceTansform
    
    @property
    def main(self):
        return self._main
    
    @property
    def references(self):
        references = self.referenceCount
        for plane in self.planes:
            references = references + plane.scene.referenceCount
        return references
        
    @main.setter
    def main(self, main):
        self._main = main
    
    @property
    def id(self):
        sId = "{0}".format(self._cubeCorners)
        if self._creationTime != -1:
            sId = "{0}".format(self._creationTime)
        return hash(sId)
    
    @property
    def mainImageData(self):
        return self._mWindow.mainImageData
    

    def incrementReferenceCount(self):
        self._referenceCount  = self._referenceCount + 1 
    
    def decrementReferenceCount(self):
        self._referenceCount  = self._referenceCount - 1
    
    @property
    def referenceCount(self):
        return self._referenceCount
    
    def getWindow(self):
        return self._mWindow
    