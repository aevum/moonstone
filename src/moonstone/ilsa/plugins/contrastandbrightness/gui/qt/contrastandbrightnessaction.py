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

from ......bloodstone.scenes.imageplane import VtkImagePlane
import widget.resources_rc
from contrastandbrightnessproperties \
    import ContrastAndBrightnessProperties


class ContrastAndBrightnessAction(QtCore.QObject):

    def __init__(self, ilsa):
        logging.debug("In ContrastAndBrightnessAction::__init__()")
        super(ContrastAndBrightnessAction, self).__init__(ilsa.parentWidget())
        self._ilsa = ilsa
        self.createWidgets()
        self.createActions()
        
        self._leftButtonPressEvent = None
        self._leftButtonReleaseEvent = None
        self._mouseMoveEvent = None
        
        self._action = False
        self.window = None
        self.level = None
        self._maxRange = None
        self._minRange = None
        
        
        self.mouseSensibility = 650.0
        self.sliderScale = 30.0
        
    def createWidgets(self):
        logging.debug("In RotateAction::createWidgets()") 
        self.actionContrastAndBrightness = QtGui.QAction(self.parent())
        self.actionContrastAndBrightness.setCheckable(True)
        icon33 = QtGui.QIcon()
        icon33.addPixmap(QtGui.QPixmap(
            ":/static/default/icon/48x48/color-brightness-contrast.png"), 
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionContrastAndBrightness.setIcon(icon33)
        self.actionContrastAndBrightness \
            .setObjectName("actionContrastAndBrightness")
        self.actionContrastAndBrightness.setText(
            QtGui.QApplication.translate("MainWindow", 
                                         "Contrast and Brightness", 
                                         None, QtGui.QApplication.UnicodeUTF8))
        
        self.parent().menuTools.addAction(self.actionContrastAndBrightness)
        
        self.parent().toolBarTools.addAction(self.actionContrastAndBrightness)
        
        parentProperties = self.parent().scrollAreaWidgetContents
        self.propertiesAction = ContrastAndBrightnessProperties(parentProperties)
        self.propertiesAction.hide()

    def uncheck(self, actionType):
        if self.actionContrastAndBrightness.isChecked():
            self.actionContrastAndBrightness.setChecked(False)
            self.slotActionContrastAndBrightness()

    def createActions(self):
        logging.debug("In TranslateAction::createActions()")
        self.connect(self.actionContrastAndBrightness, 
                     QtCore.SIGNAL("triggered()"),
                     self.slotActionContrastAndBrightness)
        self.connect(self.propertiesAction.contrastSlider, 
                     QtCore.SIGNAL("valueChanged(int)"),
                     self.slotActionChageValues)
        self.connect(self.propertiesAction.brightnessSlider, 
                     QtCore.SIGNAL("valueChanged(int)"),
                     self.slotActionChageValues)
    
    def slotActionChageValues(self, i):
        contrast = self.propertiesAction.contrastSlider.value() / self.sliderScale
        brightness = self.propertiesAction.brightnessSlider.value() / self.sliderScale
        if abs(contrast - self.window) > 0.001 or abs(brightness - self.level) > 0.001 :
            self.window = contrast
            self.level = self._maxRange - brightness
            for scene in self._ilsa.scenes():
                    if isinstance(scene, VtkImagePlane):
                        scene.windowLevel(self.window, self.level)
    
    def slotActionContrastAndBrightness(self):
        logging.debug("In TranslateAction::slotActionTranslate()")
        if not self._maxRange:
            range = self._ilsa.scenes()[0].imagedata.GetScalarRange()
            self._minRange = range[0]
            self._maxRange = range[1]
            range = self._maxRange - self._minRange
            self.propertiesAction.contrastSlider.setRange(0, range*self.sliderScale)
            self.propertiesAction.brightnessSlider.setRange(0, range*self.sliderScale)
        
        self._action = False
        scenes = self._ilsa.scenes()
        if not self.actionContrastAndBrightness.isChecked():
            self.propertiesAction.hide()
            self.parent().toolProperties.setVisible(False)
            self.removeObservers()
            return 
        self._ilsa.desactivateOthers("contrastandbrightness")
        self.parent().toolProperties.setVisible(True)
        self.propertiesAction.show()
        self.parent().scrollAreaWidgetContents.resize(self.propertiesAction.size())
        self._leftButtonPressEvent = {}
        self._leftButtonReleaseEvent = {}
        self._mouseMoveEvent = {}
        for scene in scenes:
            if isinstance(scene, VtkImagePlane):
                self._leftButtonPressEvent[scene] = scene.addObserver("LeftButtonPressEvent", 
                                                     self.ButtonCallback)
                self._leftButtonReleaseEvent[scene] = scene.addObserver("LeftButtonReleaseEvent", 
                                                     self.ButtonCallback)
                self._mouseMoveEvent[scene] = scene.addObserver("MouseMoveEvent", 
                            lambda o, e, s=scene: self.MouseMoveCallback(o, e, s))

        self.updateValues()
        
    def updateValues(self):
        scenes = self._ilsa.scenes()
        self.window = scenes[0].currentWindow
        self.level = scenes[0].currentLevel
        contrast = self.window
        brightness = self._maxRange - self.level
        self.propertiesAction.contrastSlider.setValue(contrast * self.sliderScale)
        self.propertiesAction.brightnessSlider.setValue(brightness * self.sliderScale)
         
    def removeObservers(self):
        if self._leftButtonPressEvent:
            for scene, observer in self._leftButtonPressEvent.items():
                scene.removeObserver(observer)
        if self._leftButtonReleaseEvent:
            for scene, observer in self._leftButtonReleaseEvent.items():
                scene.removeObserver(observer)
        if self._mouseMoveEvent:
            for scene, observer in self._mouseMoveEvent.items():
                scene.removeObserver(observer)
        self._leftButtonPressEvent = {}
        self._leftButtonReleaseEvent = {}
        self._mouseMoveEvent = {}
        
        
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
            
            dx = ((self._maxRange - self._minRange) / self.mouseSensibility) * cWindow 
            dy = ((self._maxRange - self._minRange) / self.mouseSensibility) * cLevel
            
            
            scenes = self._ilsa.scenes()
            actualwindow = scenes[0].currentWindow
            actuallevel = scenes[0].currentLevel
            
            range = self._maxRange - self._minRange
            newWindow = min(max(dx + actualwindow, 1), range)
            newLevel = min(max(actuallevel - dy, self._minRange), self._maxRange)

            self.propertiesAction.contrastSlider.setValue(newWindow * self.sliderScale)
            self.propertiesAction.brightnessSlider.setValue((self._maxRange - newLevel) * self.sliderScale)
            self.slotActionChageValues(None)
                    
    def save(self):
        yaml = {"window" : self.window, "level" : self.level}
        return yaml

    def restore(self, value):
        if value.has_key("window"):
            self.window = value["window"]
        if value.has_key("level"):
            self.level = value["level"]
        if self.window:
            for scene in self._ilsa.scenes():
                    if isinstance(scene, VtkImagePlane):
                        scene.windowLevel(self.window, self.level)
                    
    def addScene(self, scene):
        if self.window:
            if isinstance(scene, VtkImagePlane):
                scene.windowLevel(self.window, self.level)
                    