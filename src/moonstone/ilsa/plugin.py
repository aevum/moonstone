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

from base import IlsaCompositeBase


class IlsaPlugin(IlsaCompositeBase):
    ACTION_TYPE_WIDGET = 0
    ACTION_TYPE_MOUSE = 1
    
    def __init__(self, mainWindowWidget):
        logging.debug("In IlsaPlugin::__init__()")
        self._mainWindowWidget = mainWindowWidget
        self._plugins = []
                            
    def add(self, plugin):
        logging.debug("In Ilsa::add()")
        #if issubclass(plugin, PluginBase):
            #print "huhuhu"
        self._plugins.append(plugin)
        #else:
        #    if plugin is None:
        #        self._plugins.append(None)
            
    def remove(self, plugin):
        logging.debug("In Ilsa::remove()")
        try:
            self._plugins.remove(plugin)
        except ValueError, e:
            logging.error(e)
        
    def childs(self, index=None):
        logging.debug("In Ilsa::childs()")
        if index is None:
            return set(self._plugins)
        return set(self._plugins[index])
    
    def lenght(self, index=None):
        logging.debug("In Ilsa::lenght()")
        if index is None:
            return len(self.getChild())
        return self.getChild(index)
    
    def parentWidget(self):
        logging.debug("In Ilsa::parentWidget()")
        return self._mainWindowWidget
    
    def menuWidget(self):
        logging.debug("In Ilsa::menuWidget()")
        return self.parentWidget().menuTools
    
    def toolBarWidget(self):
        logging.debug("In Ilsa::toolBarWidget()")
        return self.parentWidget().toolBarTools
    
    def windowArea(self):
        logging.debug("In Ilsa::windowArea()")
        return self.parentWidget().mWindow
    
    def activeSubWindow(self):
        logging.debug("In Ilsa::activeSubWindow()")
        return self.windowArea().currentTab()
    
    def volumePlane(self):
        logging.debug("In Ilsa::volumePlane()")
        from ..gui.qt.volumeview import VolumeView
        return VolumeView
        
    def axialPlane(self):
        logging.debug("In Ilsa::axialPlane()")
        from ..gui.qt.axialplane import AxialPlane
        return AxialPlane
        
    def coronalPlane(self):
        logging.debug("In Ilsa::coronalPlane()")
        from ..gui.qt.coronalplane import CoronalPlane
        return CoronalPlane
        
    def sagittalPlane(self):
        logging.debug("In Ilsa::sagittalPlane()")
        from ..gui.qt.sagittalplane import SagittalPlane
        return SagittalPlane
    
    def volumeScene(self):
        logging.debug("In Ilsa::volumeScene()")
        from ..bloodstone.vtk.scene.volume import VtkVolumeScene
        return VtkVolumeScene
        
    def axialScene(self):
        logging.debug("In Ilsa::axialScene()")
        from ..bloodstone.vtk.scene.axial import VtkAxialScene
        return VtkAxialScene
        
    def coronalScene(self):
        logging.debug("In Ilsa::coronalScene()")
        from ..bloodstone.vtk.scene.coronal import VtkCoronalScene
        return VtkCoronalScene
        
    def sagittalScene(self):
        logging.debug("In Ilsa::sagittalScene()")
        from ..bloodstone.vtk.scene.sagittal import VtkSagittalScene
        return VtkSagittalScene
    
    def addObserver(self, observer):
        subWindow = self.activeSubWindow()
        if subWindow is None:
            return
        widget = subWindow.widget()
        widget.addObserver(0, 0, observer)
    
    def observers(self):
        logging.debug("In Ilsa::observers()")
        subWindow = self.activeSubWindow()
        if subWindow is None:
            return []
        observers = []
        layout = subWindow.widget().composite
        rows = layout.allChilds()
        for i, row in enumerate(rows):
            collumns = row.allChilds()
            for j, collumn in enumerate(collumns):
                observers.append(collumn)
        return observers
    
    def planes(self):
        logging.debug("In Ilsa::planes()")
        tabs = self.windowArea().allTabs()
        planes = []
        for tab in tabs:
            planes = planes + tab.planes
        return planes
    
    def activePlanes(self):
        logging.debug("In Ilsa::planes()")
        return self.activeSubWindow().planes
    
    def activeScenes(self):
        logging.debug("In Ilsa::activeScenes()")
        vtkScenes = []
        for plane in self.activePlanes():
            vtkScenes.append(plane.scene)
        return vtkScenes
    
    def scenes(self):
        logging.debug("In Ilsa::scenes()")
        vtkScenes = []
        for plane in self.planes():
            vtkScenes.append(plane.scene)
        return vtkScenes
    
    def desactivate(self, plugins):
        for plugin in self._plugins:
            if plugin.name in plugins:
                plugin.action.uncheck()
    
    def desactivateOthers(self, name, actionType=ACTION_TYPE_WIDGET):
        for plugin in self._plugins:
            if plugin.name.split("-")[1] != name:
                plugin.action.uncheck(actionType)

if __name__ == "__main__":
    ilsa = Ilsa()
    ilsa.loadPlugins()