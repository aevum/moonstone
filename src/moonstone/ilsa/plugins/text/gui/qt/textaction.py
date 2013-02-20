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

from textproperties import TextProperties
from ...textwidget import TextWidget
from ......bloodstone.scenes.imageplane import VtkImagePlane


class TextAction(QtCore.QObject):

    def __init__(self, ilsa):
        logging.debug("In TextAction::__init__()")
        super(TextAction, self).__init__(ilsa.parentWidget())
        self._ilsa = ilsa
        self.createWidgets()
        self.createActions()
        self.connected = False
        self._action = False
        self.text = None
        self.observers = None
        
    def uncheck(self, actionType):
        if self.actionText.isChecked():
            self.actionText.setChecked(False)
            self.slotActionText()
                
    def createWidgets(self):
        logging.debug("In TextAction::createWidgets()") 
        self.actionText = QtGui.QAction(self.parent())
        self.actionText.setCheckable(True)
        icon41 = QtGui.QIcon()
        icon41.addPixmap(
            QtGui.QPixmap(":/static/default/icon/48x48/draw-text.png"), 
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionText.setIcon(icon41)
        self.actionText.setObjectName("actionText")
        self.actionText.setText(
            QtGui.QApplication.translate("MainWindow", "&Text", 
                                         None, QtGui.QApplication.UnicodeUTF8))
        
        self.parent().menuTools.addAction(self.actionText)
        self.parent().toolBarTools.addAction(self.actionText)
        
        parentProperties = self.parent().scrollAreaWidgetContents
        self.propertiesAction = TextProperties(parentProperties)
        self.propertiesAction.hide()

    def createActions(self):
        logging.debug("In TranslateAction::createActions()")
        self.connect(self.actionText, QtCore.SIGNAL("triggered()"),
                     self.slotActionText)
        
    def slotActionText(self):
        logging.debug("In TranslateAction::slotActionTranslate()")
        if not self.connected:
            self.propertiesAction.connect(self.propertiesAction.newTextButton,
                                    QtCore.SIGNAL("clicked ( bool)"),
                                    self.slotNewText)
            self.propertiesAction.connect(self.propertiesAction.deleteTextButton,
                                    QtCore.SIGNAL("clicked ( bool)"),
                                    self.slotDeleteText)
            self.connected = True
        
        if not self.actionText.isChecked():
            self.removeObservers()
            self.propertiesAction.hide()
            self.parent().toolProperties.setVisible(False)
            return
        
        self._ilsa.desactivateOthers("text")
        self.parent().toolProperties.setVisible(True)
        self.propertiesAction.show()
        self.parent().scrollAreaWidgetContents.resize(self.propertiesAction.size())
        if not self.propertiesAction.texts:
            self.slotNewText(True)
    
    def slotNewText(self, checked):
        scenes = self._ilsa.scenes()
        if not self.text or self.text.getStarted():
            self.text = TextWidget()
            self.propertiesAction.addText(self.text)
        self.removeObservers()
        self.scenesMap = {}
        self.observers = {}
        for scene in scenes:
            if isinstance(scene, VtkImagePlane):
                self.observers[scene] = scene.addObserver("LeftButtonPressEvent", self.activateText) 
                self.scenesMap[scene.interactor.GetInteractorStyle()] = scene

        self.started = self.text.getStarted()
        
    def removeObservers(self):
        if self.observers:
            for scene, observer in self.observers.items():
                scene.removeObserver(observer)
        self.observers = {}
                

    def slotDeleteText(self, checked):
        self.propertiesAction.removeSelectedText()
        self.removeObservers()
        self.text = None

    def activate(self, obj, evt):
        self.text.start()
    
    
    def activateText(self, obj, evt):
        scene = self.scenesMap[obj]
        self.text.setScene(scene)
        self.removeObservers()
                
    def save(self):
        texts = self.propertiesAction.texts.values()
        yamlTexts = []
        for text in texts:
            if text.getStarted():
                yamlTexts.append(text.save()) 
        yaml = {"texts" : yamlTexts}
        return yaml
    
    def restore(self, value):
        texts = value["texts"]
        if texts:
            for text in texts:
                self.loadText(text)
        self.started = False
        
    def loadText(self, text):
        scenes = self._ilsa.scenes()
        for scene in scenes:
            if scene.id == text["sceneId"]:
                self.text = TextWidget(scene)
                self.propertiesAction.addText(self.text)
                self.text.setText(text["text"])
                self.text.setPosition(text["position"])
                self.text.setFontColor(*text["fontColor"])
                self.text.setVisible(text["visible"])
                self.text.setFont(text["font"])
                self.text.setFontSize(text["fontSize"])
                self.text.setBold(text["bold"])
                self.text.setItalic(text["italic"])
                self.text.autoResizeBox()
#                self.text.scene.removeObserver(self.text.event)
                self.propertiesAction.slotSelectButtonByText(self.text, None)
                
    def removeScene(self, scene):
        self.propertiesAction.removeScene(scene)
                

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    win = TextAction()
    win.show()
    sys.exit(app.exec_())