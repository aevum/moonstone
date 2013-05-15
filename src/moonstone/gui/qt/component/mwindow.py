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

from mscreen import MScreen
from ....bloodstone.scenes.imageplane import VtkImagePlane
from ..rename import Rename
from ....bloodstone.scenes.cameracontroller2d import CameraController2D


class MWindow(QtGui.QTabWidget):

    def __init__(self, ilsa = None, parent=None, serie=None):
        logging.debug("In MWindow::__init__()")
        super(MWindow, self).__init__(parent)
        self._serie = serie
        self.createWidgets()
        self.createContextMenu()
        self.createActions()
        self.updateWidgets()
        self._ilsa = ilsa
        self._mScreens = []
        self._yamlPath = None
        self._mainImageData = None
        self._vtiPath = None
        self._cameraController = CameraController2D(self)
        
    def addTab(self, widget, title):
        logging.debug("In MWindow::addTab()")
        if isinstance(widget, MScreen):
            super(MWindow, self).addTab(widget, title)
            self._mScreens.append(widget)
        else:
            raise "Widget is not a instance of MScreen!"
        
    def createWidgets(self):
        logging.debug("In MWindow::createWidgets()")
        self.rename = Rename(self)
    
    def close(self):
        self._mainImageData = None
        for mscreen in self._mScreens:
            mscreen.close(force=True)
            #mscreen.destroy()
            #mscreen.setParent(None)
            #mscreen = None
            #del mscreen
        #self._mScreens = None
        #self.mouseReleaseEvent = None
        super(MWindow, self).close()
    
    def createContextMenu(self):
        logging.debug("In AxialPlane::createContextMenu()")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/im-status-message-edit.png"))
        self.renameAction = QtGui.QAction(self)
        self.renameAction.setText(QtGui.QApplication.translate("MWindow", 
                                                     "Rename", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8))
        self.renameAction.setIconVisibleInMenu(True)
        self.renameAction.setObjectName("renameAction")
        self.renameAction.setIcon(icon1)
        
        
        iconDuplicate = QtGui.QIcon()
        iconDuplicate.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/document-new.png"))
        
        self.duplicateAction = QtGui.QAction(self)
        self.duplicateAction.setText(QtGui.QApplication.translate("MWindow", 
                                                     "Duplicate", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8))
        self.duplicateAction.setIconVisibleInMenu(True)
        self.duplicateAction.setObjectName("duplicateAction")
        self.duplicateAction.setIcon(iconDuplicate)

        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/view-refresh.png"))
        self.resetAction = QtGui.QAction(self)
        self.resetAction.setText(QtGui.QApplication.translate("MWindow", 
                                                     "Reset", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8))
        self.resetAction.setIconVisibleInMenu(True)
        self.resetAction.setObjectName("resetAction")
        self.resetAction.setIcon(icon2)
        
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/dialog-close.png"))
        self.closeAction = QtGui.QAction(self)
        self.closeAction.setText(QtGui.QApplication.translate("MWindow", 
                                                     "Close", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8))
        self.closeAction.setIconVisibleInMenu(True)
        self.closeAction.setObjectName("closeAction")
        self.closeAction.setIcon(icon2)
        
        self.addAxialAction = QtGui.QAction(self)
        self.addAxialAction.setText("Axial")
        self.addAxialAction.setIconVisibleInMenu(True)
        self.addAxialAction.setObjectName("addAxialAction")
        
        self.addCoronalAction = QtGui.QAction(self)
        self.addCoronalAction.setText(QtGui.QApplication.translate("MWindow", 
                                                     "Coronal", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8))
        self.addCoronalAction.setIconVisibleInMenu(True)
        self.addCoronalAction.setObjectName("addCoronalAction")
        
        self.addSagittalAction = QtGui.QAction(self)
        self.addSagittalAction.setText(QtGui.QApplication.translate("MWindow", 
                                                     "Sagittal", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8))
        self.addSagittalAction.setIconVisibleInMenu(True)
        self.addSagittalAction.setObjectName("addSagittalAction")
        
        self.addVolumeAction = QtGui.QAction(self)
        self.addVolumeAction.setText(QtGui.QApplication.translate("MWindow", 
                                                     "Volume", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8))
        self.addVolumeAction.setIconVisibleInMenu(True)
        self.addVolumeAction.setObjectName("addVolumeAction")
        
        self.contextMenu = QtGui.QMenu(self)
        self.contextMenu.addAction(self.renameAction)
        self.contextMenu.addAction(self.resetAction)
        self.contextMenu.addAction(self.duplicateAction)
        self.contextMenu.addAction(self.closeAction)
        self.contextMenu.setIcon(icon1)
        
        windowMenu = QtGui.QMenu(self.contextMenu)
        windowMenu.addAction(self.addAxialAction)
        windowMenu.addAction(self.addCoronalAction)
        windowMenu.addAction(self.addSagittalAction)
        windowMenu.addAction(self.addVolumeAction)
        windowMenu.setTitle(QtGui.QApplication.translate("MWindow", 
                                                     "Add Scene", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8))
        self.contextMenu.addAction(windowMenu.menuAction())
        
    def createActions(self):
        logging.debug("In MWindow::createActions()")
        self.connect(self, QtCore.SIGNAL("tabCloseRequested(int)"),
                     self.slotTabCloseRequested)
        self.connect(self, QtCore.SIGNAL("currentChanged(int)"),
                     self.slotTabChanged)
        self.mouseReleaseEvent = self.rightClickAction
        self.connect(self.rename.Ok, QtCore.SIGNAL("clicked()"),
                     self.slotRenameOkButtonClicked)
        self.connect(self.rename.Cancel, QtCore.SIGNAL("clicked()"),
                     self.slotRenameCancelButtonClicked)
    
    def rightClickAction(self, event):
        if event.button() == 2: 
            pos = QtGui.QCursor.pos()
            result = self.contextMenu.exec_(pos)
            if result == self.renameAction:
                self.rename.newName.setText(self.tabText(self.currentIndex()))
                self.rename.show()
            elif result == self.closeAction:
                self.close()
            elif result == self.resetAction:
                self.reset()
            elif result == self.duplicateAction:
                self.duplicate()
            elif result == self.addAxialAction:
                mscreen = self._mScreens[self.currentIndex()]
                mscreen.createScene(VtkImagePlane.PLANE_ORIENTATION_AXIAL)
            elif result == self.addCoronalAction:
                mscreen = self._mScreens[self.currentIndex()]
                mscreen.createScene(VtkImagePlane.PLANE_ORIENTATION_CORONAL)
            elif result == self.addSagittalAction:
                mscreen = self._mScreens[self.currentIndex()]
                mscreen.createScene(VtkImagePlane.PLANE_ORIENTATION_SAGITTAL)
            elif result == self.addVolumeAction:
                mscreen = self._mScreens[self.currentIndex()]
                mscreen.createScene(VtkImagePlane.PLANE_ORIENTATION_VOLUME)
            
    def updateWidgets(self):
        logging.debug("In MWindow::updateWidgets()")
        self.setTabsClosable(True)
        self.setMovable(True)
        
    def slotTabCloseRequested(self, index):
        logging.debug("In MWindow::slotTabCloseRequested()")
        mScreen = self.widget(index)
        if mScreen.main or mScreen.references > 0:
            QtGui.QMessageBox.critical(self, 
                                       QtGui.QApplication.translate(
                                                    "Implant", "Error",
                                                    None, QtGui.QApplication.UnicodeUTF8),
                                       QtGui.QApplication.translate(
                                                    "Implant", "Some tool is locking this tab and it cannot be closed.",
                                                    None, QtGui.QApplication.UnicodeUTF8))
            return
        mScreen.close()
        self._mScreens.remove(mScreen)
        self.removeTab(index)
        if self.currentIndex() == -1:
            self.close()
    
    def slotRenameOkButtonClicked(self):
        logging.debug("In MWindow::slotRenameOkButtonClicked()")
        self.setTabText(self.currentIndex(), self.rename.newName.text())
        mScreen = self.widget(self.currentIndex())
        mScreen.name = self.rename.newName.text()
        self.rename.hide()
    
    def slotRenameCancelButtonClicked(self):
        logging.debug("In MWindow::slotRenameCancelButtonClicked()")
        self.rename.hide()
        
    def slotTabChanged(self, index):
        logging.debug("In MWindow::slotTabCloseRequested()")
        if self._mScreens:
            self.currentTab().updateWidgets()
    
    def allTabs(self):
        logging.debug("In MWindow::allTabs()")
        return self._mScreens
    
    def currentTab(self):
        logging.debug("In MWindow::currentTab()")
        return self._mScreens[self.currentIndex()]
    
    def createMScreensFromImagedata(self, imagedata, cubeCorners=None, name=None, generate3D=1):
        logging.debug("In MWindow::createMScreensFromImagedata()")
        i = self.count()
        name = QtGui.QApplication.translate("MWindow", "Region {0}", None,
                                             QtGui.QApplication.UnicodeUTF8).format(i)
        screen = MScreen(mWindow=self, vtkImageData=imagedata, cubeCorners=cubeCorners, name=name)
        
        screen.createScene(VtkImagePlane.PLANE_ORIENTATION_AXIAL)  
        if generate3D:
            screen.createScene(VtkImagePlane.PLANE_ORIENTATION_VOLUME)
        screen.createScene(VtkImagePlane.PLANE_ORIENTATION_CORONAL)
        screen.createScene(VtkImagePlane.PLANE_ORIENTATION_SAGITTAL)      
        self.addTab(screen, name)
        return screen
        
    def reset(self):
        self.currentTab().reset()
    
    def duplicate(self):
        self.currentTab().duplicate()
    
    def save(self):
        logging.debug("In MWindow::save()")
        save = {"vti": self._vtiPath}
        mscreens = []
        save["mScreens"] = mscreens
        for i, screen in enumerate(self._mScreens):
            mscreens.append(screen.save(self._yamlPath, i, self.tabText(i)))
        return save
    
    @property
    def ilsa(self):
        logging.debug("In MWindow::ilsa()")
        return self._ilsa
    
    @property
    def yamlPath(self):
        logging.debug("In MWindow::yamlPath.getter()")
        return self._yamlPath

    @property
    def cameraController(self):
        logging.debug("In MWindow::cameraContoller.getter()")
        return self._cameraController
    
    @yamlPath.setter
    def yamlPath(self, yamlPath):
        logging.debug("In MWindow::yamlPath.setter()")
        self._yamlPath = yamlPath
    
    @property
    def mainImageData(self):
        return self._mainImageData
    
    @mainImageData.setter
    def mainImageData(self, mainImageData):
        self._mainImageData = mainImageData
    
    @property
    def serie(self):
        return self._serie
    
    @serie.setter
    def serie(self, serie):
        self._serie = serie
    
    @property
    def vtiPath(self):
        return self._vtiPath
    
    @vtiPath.setter
    def vtiPath(self, vtiPath):
        self._vtiPath = vtiPath
    
    @property
    def planes(self):
        logging.debug("In MWindow::planes.getter()")
        planes = []
        for screen in self._mScreens:
            planes = planes + screen.planes
        return planes