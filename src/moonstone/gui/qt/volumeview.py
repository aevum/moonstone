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

from PySide import QtCore, QtGui

from ...bloodstone.scenes.gui.qt.component.qvtkwidget import QVtkWidget
from ...bloodstone.scenes.imagevolume import VtkImageVolume
from ...bloodstone.utils.data import load_yaml_file
from ...utils.constant import HOUNSFIELD_FILE_PATH
from hounsfieldEditor import HounsfieldEditor
from surfaceEditor import SurfaceEditor
from view import View

class VolumeView( View ):

    def __init__(self, mscreenParent, cubeCorners=None, parent=None, title = "Volume", planeNumber = 1):
        logging.debug("In ViewPlane::__init__()")
        self._planeOrientation = -1
        self._cubeCorners = cubeCorners
        self.defaultHounsfeildIndex = 0
        self.maxRange = None
        self.minRange = None
        self._action = False
        self.mouseSensibility = 2000.0
        self.sliderScale = 30.0
        self._mouseMoveEvent = None
        self.hounsfieldEditor = None
        self._referencedPlanes = []
        super(VolumeView, self).__init__( title, mscreenParent, planeNumber)

    def activateAllPlanes(self):
        for plane in filter( lambda pl: not isinstance( pl, VolumeView ), self._mscreenParent._planes):
            if not plane in self._referencedPlanes:
                #plane.scene.addSliceChangeListener( self.onReferedPlanesChange )
                plane.addSliderReleasedListeners( self.onReferedPlanesChange )
                plane.addCloseListener( self.onReferedPlaneClose )
                self.addReferencedPlane(plane)
                self.scene.addSlicePlaneWidget( plane.planeWidget() )
            else:
                #plane.scene.removeSliceChangeListener( self.onReferedPlanesChange )
                plane.removeSliderReleasedListeners( self.onReferedPlanesChange )
                plane.addCloseListener( self.onReferedPlaneClose )
                self.removeReferencedPlane(plane)
                self.scene.removeSlicePlaneWidget( plane.planeWidget() )

    def desactivateAllPlanes(self):
        logging.debug("In SingleSlicePlane::desactivateAllPlanes()")
        for plane in filter( lambda pl: not isinstance( pl, VolumeView ), self._mscreenParent._planes):
            if plane in self._referencedPlanes:
                plane.scene.removeSliceChangeListener( self.onReferedPlanesChange )
                plane.removeCloseListener( self.onReferedPlaneClose )
                if plane in self._referencedPlanes:
                    self._referencedPlanes.remove( plane )
                self.scene.removeSlicePlaneWidget( plane.planeWidget() )

    def closeEvent(self, event ):
        logging.debug("In SliceView::closeEvent()")
        self.closeAction( event )
    
    def changeVisibility(self):            
        self.setVisible(not self.isVisible())
        if  self.isVisible():
            self.resizeAction()
        
    def createWidgets(self):
        logging.debug("In ViewPlane::createWidgets()")
        super( VolumeView, self ).createWidgets()

        self.actionDefaultBehavior = QtGui.QAction(self)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/edit-select.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionDefaultBehavior.setIcon(icon3)
        self.actionDefaultBehavior.setCheckable(True)
        self.actionDefaultBehavior.setChecked(True)
        self.actionDefaultBehavior.setObjectName("actionDefaultBehavior")
        self.toolbar.addAction(self.actionDefaultBehavior)

        self.actionContrastAndBrightness = QtGui.QAction(self)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/static/default/icon/48x48/color-brightness-contrast.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionContrastAndBrightness.setIcon(icon2)
        self.actionContrastAndBrightness.setObjectName("actionContrastAndBrightness")
        self.actionContrastAndBrightness.setCheckable(True)
        self.toolbar.addAction(self.actionContrastAndBrightness)

        self.setWindowTitle(self.title)
        self.action3DPresets = QtGui.QAction(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/static/default/icon/48x48/filter.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action3DPresets.setIcon(icon)
        self.action3DPresets.setObjectName("action3D")
        self.toolbar.addAction(self.action3DPresets)

        self.actionSurfacePresets = QtGui.QAction(self)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/static/default/icon/48x48/superficie.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSurfacePresets.setIcon(icon1)
        self.actionSurfacePresets.setObjectName("actionSurfacePresets")
        self.toolbar.addAction(self.actionSurfacePresets)
        self.createSurfaceWidget()

        self.actionImagePlaneWidget = QtGui.QAction( self )
        icon1 = QtGui.QIcon()
        icon1.addPixmap( QtGui.QPixmap( ':/static/default/icon/22x22/office-chart-polar.png' ), QtGui.QIcon.Normal, QtGui.QIcon.Off )
        self.actionImagePlaneWidget.setIcon( icon1 )
        self.actionImagePlaneWidget.setObjectName( 'actionSlicePlaneWidgetPresets' )
        self.toolbar.addAction( self.actionImagePlaneWidget )
    
    def splitterMoved(self, a, b):
        self.resizeAction()
    
    def resizeAction(self):
        size = self.plane.size()
        self.scene.interactor.setGeometry(0, 0, size.width(), size.height())
        self.updateGeometry()
        
    def close(self):
        if self._mouseMoveEvent != None:
            self.scene.removeObserver(self._leftButtonPressEvent, False)
            self.scene.removeObserver(self._leftButtonReleaseEvent, False)
            self.scene.removeObserver(self._mouseMoveEvent, False)
        if self.hounsfieldEditor:
            self.hounsfieldEditor.close()
            self.hounsfieldEditor.destroy()

        self._mscreenParent = None
        self.scene.close() 
        self.scene = None
        del self.scene
        self.destroy()
        self.closeEvent = None
        
    def closeAction(self, event = None, force=False):
        logging.debug("In ViewPlane::closeEvent()")
        if self.scene.referenceCount < 1 or force:
            if not self.mscreenParent.removeScene(self):
                event.ignore()
        else: 
            event.ignore()
        
    def createScene(self):
        super( VolumeView, self ).createScene()
        logging.debug("In ViewPlane::createScene()")
        self.scene = VtkImageVolume(QVtkWidget(self.plane), self)
        self.scene.cubeCorners = self._cubeCorners
        self.loadHounsFieldScales()
        self.loadSurfaces()
        
    def createActor(self, vtkImageData ):
        logging.debug("In ViewPlane::createActor()")
        self.scene.createActor(vtkImageData)
        
    def createActions(self):
        logging.debug("In ViewPlane::createActions()")
        self.closeEvent = self.closeAction

        self.connect( self.action3DPresets, QtCore.SIGNAL("triggered()"), self.slotAction3DPresets )
        self.connect( self.actionSurfacePresets, QtCore.SIGNAL("triggered()"), self.slotActionSurfacePresets )
        self.connect( self.actionContrastAndBrightness, QtCore.SIGNAL("triggered()"), self.slotActionContrastAndBrightness )
        self.connect( self.actionDefaultBehavior, QtCore.SIGNAL("triggered()"), self.slotActionDefaultBehavior )
        self.connect( self.actionImagePlaneWidget, QtCore.SIGNAL( 'triggered()' ), self.slotActionImagePlaneWidget )

    def slotActionImagePlaneWidget( self ):

        logging.debug("In VolumePlane::slotActionImagePlaneWidget()")
        self.menu = QtGui.QMenu()
        for plane in filter( lambda pl: not isinstance( pl, VolumeView ), self._mscreenParent._planes ):
            action = QtGui.QWidgetAction( self )
            action.setCheckable( True )
            action.setText(plane.title)
            action.setData( plane )
            action.setChecked( plane in self._referencedPlanes )
            self.menu.addAction( action )

        self.connect( self.menu, QtCore.SIGNAL('triggered(QAction*)'), self.slotActionImagePlaneChoose )
        pos = QtGui.QCursor.pos()
        self.menu.exec_( pos )

    def addReferencedPlane( self, plane ):
        if  plane not in self._referencedPlanes:
            self._referencedPlanes.append( plane )

    def removeReferencedPlane( self, plane ):
        if  plane in self._referencedPlanes:
            self._referencedPlanes.remove( plane )

    def slotActionImagePlaneChoose( self, action ):
        logging.debug( 'In VolumePlane::slot3DPresetChanged()' )
        plane = action.data()
        if action.isChecked():
            #plane.scene.addSliceChangeListener( self.onReferedPlanesChange )
            plane.addSliderReleasedListeners( self.onReferedPlanesChange )
            plane.addCloseListener( self.onReferedPlaneClose )
            self.addReferencedPlane(plane)
            self.scene.addSlicePlaneWidget( plane.planeWidget() )
        else:
            #plane.scene.removeSliceChangeListener( self.onReferedPlanesChange )
            plane.removeSliderReleasedListeners( self.onReferedPlanesChange )
            plane.addCloseListener( self.onReferedPlaneClose )
            self.removeReferencedPlane(plane)
            self.scene.removeSlicePlaneWidget( plane.planeWidget() )

    def onReferedPlaneClose( self, plane ):
        plane.scene.removeSliceChangeListener( self.onReferedPlanesChange )
        plane.removeCloseListener( self.onReferedPlaneClose )
        if plane in self._referencedPlanes:
            self._referencedPlanes.remove( plane )
        self.scene.removeSlicePlaneWidget( plane.planeWidget() )

    def onReferedPlanesChange( self, plane=None ):
        self.scene.window.Render()

    def slotAction3DPresets(self):
        logging.debug("In VolumePlane::slotAction3DPresets()")
        self.actionContrastAndBrightness.setChecked(False)
        self.slotActionContrastAndBrightness()
        presets = self.get3DPresets()
        self.menu = QtGui.QMenu()
        for preset in presets:
            action = QtGui.QAction(self)
            action.setText(preset["name"])
            action.setCheckable(True)
            self.menu.addAction(action)
            if preset["id"] == self.defaultHounsfeildIndex:
                action.setChecked(True)
        self.menu.addSeparator()
        action = QtGui.QAction(self)
        action.setText("Add/Remove/Edit")
        self.menu.addAction(action)
        self.connect(self.menu, QtCore.SIGNAL("triggered ( QAction*)"),
            self.slot3DPresetChanged)
        pos = QtGui.QCursor.pos()
        self.menu.exec_(pos)

    def slot3DPresetChanged(self, action):
        logging.debug("In VolumePlane::slot3DPresetChanged()")
        presets = self.get3DPresets()
        exist = False
        for preset in presets:
            if preset["name"] == action.text():
                self.defaultHounsfeildIndex = preset["id"]
                exist = True
                self.slotModeChanged(action.text())
                break
        if not exist:
            self.createHounsfieldEditorWidget()

    def slotActionSurfacePresets(self):
        logging.debug("In VolumePlane::slotActionSurfacePresets()")
        self.actionContrastAndBrightness.setChecked(False)
        self.slotActionContrastAndBrightness()
        presets = self.getSurfacePresets()
        self.menu = QtGui.QMenu()
        for preset in presets:
            action = QtGui.QAction(self)
            action.setText(preset["name"])
            action.setCheckable(True)
            self.menu.addAction(action)
            if preset.has_key("check") and preset["check"]:
                action.setChecked(True)
        self.menu.addSeparator()
        action = QtGui.QAction(self)
        action.setText("New Surface")
        self.menu.addAction(action)
        self.connect(self.menu, QtCore.SIGNAL("triggered ( QAction*)"),
            self.slotSurfacePresetChanged)
        pos = QtGui.QCursor.pos()
        self.menu.exec_(pos)

    def slotSurfacePresetChanged(self, action):
        logging.debug("In VolumePlane::slot3DPresetChanged()")
        presets = self.getSurfacePresets()
        exist = False
        for preset in presets:
            if preset["name"] == action.text():
                exist = True
                if preset.has_key("check") and preset["check"]:
                    preset["check"] = False
                    self.scene.removeSurface(preset["name"])
                else:
                    preset["check"] = True
                    self.scene.addSurface(preset["name"], preset["value"], preset["r"], preset["g"], preset["b"])
                break
        if not exist:
            self.newSurface()

    def newSurface(self):
        pos = QtGui.QCursor.pos()
        pos.setX(pos.x())
        pos.setY(pos.y())
        self.surfacesWidget.move(pos)
        self.surfacesWidget.show()

    def createWindowLevel(self):
        scalarRange = self.scene.vtkImageData.GetScalarRange()
        self.minRange = scalarRange[0]
        self.maxRange = scalarRange[1]
        self._leftButtonPressEvent = None
        self._leftButtonReleaseEvent = None
        self._mouseMoveEvent = None
        self.createWindowLevelWidget()

    def createHounsfieldEditorWidget(self):
        if self.hounsfieldEditor:
            self.hounsfieldEditor.setParent(None)
            self.hounsfieldEditor.close()
            self.hounsfieldEditor.destroy()
        self.hounsfieldEditor = HounsfieldEditor(self, self.scene.actualHounsfieldScale["name"], self.scene.vtkImageData)
        self.hounsfieldEditor.show()

    def getActualWindow(self):
        return self.scene.opacityWindow

    def getActualLevel(self):
        return self.scene.opacityLevel

    def createWindowLevelWidget(self):
        self.contrastLabel = QtGui.QLabel("Contrast")
        self.brightnessLabel = QtGui.QLabel("Brightness")

        self.brightnessSlider = QtGui.QSlider()
        self.brightnessSlider.setOrientation(QtCore.Qt.Horizontal)
        self.brightnessSlider.setObjectName("brightnessSlider")

        self.contrastSlider = QtGui.QSlider()
        self.contrastSlider.setOrientation(QtCore.Qt.Horizontal)
        self.contrastSlider.setObjectName("contrastSlider")

        levelRange = self.maxRange - self.minRange
        self.brightnessSlider.setRange(0,levelRange*self.sliderScale)
        self.contrastSlider.setRange(self.sliderScale, levelRange*self.sliderScale)

        self.contrastBrightnessPopUp = QtGui.QFrame(self.toolbar, QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool | QtCore.Qt.Window)

        vLayout = QtGui.QHBoxLayout(self.contrastBrightnessPopUp)

        windowLayout = QtGui.QHBoxLayout()
        vLayout.addLayout(windowLayout)
        windowLayout.addWidget(self.contrastLabel)
        windowLayout.addWidget(self.contrastSlider)

        levelLayout = QtGui.QHBoxLayout()
        vLayout.addLayout(levelLayout)
        levelLayout.addWidget(self.brightnessLabel)
        levelLayout.addWidget(self.brightnessSlider)

        levelValue =  self.maxRange - self.scene.opacityLevel
        self.contrastSlider.setValue(self.scene.opacityWindow * self.sliderScale)
        self.brightnessSlider.setValue(levelValue * self.sliderScale)

        self.createWindowLevelActions()

    def createSurfaceWidget(self):
        self.surfacesWidget = SurfaceEditor(self, self.newSurfaceCallback)

    def newSurfaceCallback(self, surface):
        presets = self.getSurfacePresets()
        for preset in presets:
            if preset["name"] == surface["name"]:
                return False
        self.surfaces.append(surface)
        surface["check"] = True
        self.scene.addSurface(surface["name"], surface["value"], surface["r"], surface["g"], surface["b"])
        return True

    def slotActionDefaultBehavior(self):
        logging.debug("In VolumePlane::slotActionDefaultBehavior()")
        self.actionContrastAndBrightness.setChecked(False)
        self.slotActionContrastAndBrightness()

    def get3DPresets(self):
        result = []
        i = 0
        for scale in self.hounsfieldScales:
            result.append({"id" : i, "name" : scale["name"]})
            i = i +1
        return result;

    def getSurfacePresets(self):
        return self.surfaces

    def changeHounsfieldMode(self, mode):
        presets = self.get3DPresets()
        for preset in presets:
            if preset["name"] == mode:
                self.defaultHounsfeildIndex = preset["id"]
                break
            #        self.slotModeChanged()

    def slotModeChanged(self, mode):
        logging.debug("In ViewPlane::slotModeChanged()")
        self.scene.changeHounsfieldMode(mode)
        self.resetWindowLevel();

    def resetWindowLevel(self):
        self.actionContrastAndBrightness.setChecked(False)
        if self.maxRange != None:
            self.slotActionContrastAndBrightness()
            self.contrastSlider.setValue(self.scene.defaultWindow *self.sliderScale)
            self.brightnessSlider.setValue((self.maxRange - self.scene.defaultLevel) * self.sliderScale)

    def createWindowLevelActions(self):

        self.connect( self.contrastSlider, QtCore.SIGNAL("sliderReleased()"), self.slotActionChageValues )
        self.connect( self.brightnessSlider, QtCore.SIGNAL("sliderReleased()"), self.slotActionChageValues )

    def slotActionChageValues(self):
        contrast = self.contrastSlider.value() / self.sliderScale
        brightness = self.brightnessSlider.value() / self.sliderScale
        if abs(contrast - self.scene.opacityWindow) > 0.001 or abs(brightness - self.scene.opacityLevel) > 0.001 :
            level = self.maxRange - brightness
            self.scene.setWindowLevel(contrast, level)

    def slotActionContrastAndBrightness(self):
        logging.debug("In VolumePlane::slotActionContrastAndBrightness()")
        if not self.maxRange:
            self.createWindowLevel()
        if not self.actionContrastAndBrightness.isChecked():
            if self._mouseMoveEvent != None:
                self.actionDefaultBehavior.setChecked(True)
                self.scene.removeObserver(self._leftButtonPressEvent, False)
                self.scene.removeObserver(self._leftButtonReleaseEvent, False)
                self.scene.removeObserver(self._mouseMoveEvent, False)
            self.contrastBrightnessPopUp.hide()
        else:
            self.actionDefaultBehavior.setChecked(False)
            self._leftButtonPressEvent = self.scene.addObserver("LeftButtonPressEvent",
                self.ButtonCallback)
            self._leftButtonReleaseEvent = self.scene.addObserver("LeftButtonReleaseEvent",
                self.ButtonCallback)
            self._mouseMoveEvent = self.scene.addObserver("MouseMoveEvent",
                lambda o, e, s=self.scene: self.MouseMoveCallback(o, e, s))
            pos = QtGui.QCursor.pos()
            pos.setX(pos.x() + 22)
            pos.setY(pos.y())
            self.contrastBrightnessPopUp.move(pos)
            self.contrastBrightnessPopUp.show()

    def ButtonCallback(self, obj, event):
        logging.debug("In TranslateAction::ButtonCallback()")
        if event == "LeftButtonPressEvent":
            self._action = True
        else:
            self._action = False

    def MouseMoveCallback(self, obj, event, vtkScene):
        logging.debug("In TranslateAction::MouseMoveCallback()")
        (lastX, lastY) = vtkScene.interactor.GetLastEventPosition()
        (mouseX, mouseY) = vtkScene.interactor.GetEventPosition()
        if self._action:
            cWindow = mouseX - lastX
            cLevel = mouseY - lastY
            dx = ((self.maxRange - self.minRange) / self.mouseSensibility) * cWindow
            dy = ((self.maxRange - self.minRange) / self.mouseSensibility) * cLevel

            levelRange = self.maxRange - self.minRange
            newWindow = min(max(dx + self.scene.opacityWindow, 1), levelRange)
            newLevel = min(max(self.scene.opacityLevel - dy, self.minRange), self.maxRange)

            self.contrastSlider.setValue(newWindow * self.sliderScale)
            self.brightnessSlider.setValue((self.maxRange - newLevel) * self.sliderScale)
            self.slotActionChageValues()

    def setHounsfieldScalePreview(self, scale):
        self.scene.setHounsfieldFromMap(scale)

    def setWindowLevel(self, window, level):
        self.contrastSlider.setValue(window * self.sliderScale)
        self.brightnessSlider.setValue((self.maxRange - level) * self.sliderScale)
        self.slotActionChageValues()

    def loadHounsFieldScales(self):
        self.hounsfieldScales = load_yaml_file(HOUNSFIELD_FILE_PATH)
        self.hounsfieldScales.append({"name" : "None"})
        self.scene.loadHounsfieldScales(self.hounsfieldScales)

    def loadSurfaces(self):
        self.surfaces = [{"id": 0, "name" : "Bone", "value" : 600, "r" : 1.0, "g" : 1.0, "b" :0.6},
                {"id": 1, "name" : "Skin", "value" : -500, "r" : 1.0, "g" : 0.55, "b" :0.654},
                {"id": 1, "name" : "Metal", "value" : 2000, "r" : 0.686, "g" : 0.686, "b" :0.686}]

        
    def updateWidgets(self):
        logging.debug("In ViewPlane::updateWidgets()")
        self.planeSlide.setVisible(False)
        self.setWindowTitle(self.title)
        
    def reset(self):
        logging.debug("In ViewPlane::reset()")
        self.splitter.setSizes([1,0])
        self.resizeAction()
        self.scene.reset()
    
    @property
    def mscreenParent(self):
        logging.debug("In ViewPlane::mscreenParent.getter()")
        return self._mscreenParent
    
    @mscreenParent.setter
    def mscreenParent(self, mscreenParent):
        logging.debug("In ViewPlane::mscreenParent.setter()")
        self._mscreenParent = mscreenParent

    def load(self, data):
        logging.debug("In ViewPlane::id.load()")
        if data.has_key("id"):
            self.setSceneId(data["id"])
        if data.has_key("hounsfieldMode"):
            mode = data["hounsfieldMode"]
            self.slotModeChanged(mode)
            presets = self.get3DPresets()
            for preset in presets:
                if preset["name"] == mode:
                    self.defaultHounsfeildIndex = preset["id"]
                    break
        if data.has_key("window"):
            window = data["window"]
            level = data["level"]
            self.scene.setWindowLevel(window, level)
            self.resetWindowLevel()

        if data.has_key("sliceWidgets") and ( data.has_key("id") and data["id"] == self.scene._id ):
            lst = [ plane for plane in self._mscreenParent._planes if plane.scene._id in data["sliceWidgets"] ]
            for plane in lst:

                plane.addSliderReleasedListeners( self.onReferedPlanesChange )
                plane.addCloseListener( self.onReferedPlaneClose )
                self.addReferencedPlane(plane)
                self.scene.addSlicePlaneWidget( plane.planeWidget() )
     
    @property
    def id(self):
        logging.debug("In ViewPlane::id.getter()")
        return self._id
    
    def setSceneId(self, id):
        self.scene.id = id
    
    @property
    def planeOrientation(self):
        logging.debug("In ViewPlane::planeOrientation.getter()")
        return self._planeOrientation

    @property
    def mainImageData(self):
        return self._mscreenParent.mainImageData
    
    def getScreen(self):
        return self._mscreenParent