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
import os
import logging

import extensions
from PySide import QtGui

import util.configure as configure
from base import IlsaCompositeBase, IlsaObserverBase
from plugin import IlsaPlugin
from plugins.base import PluginBase
from ..bloodstone.utils.data import load_vtis_from_yaml_file
from ..utils import constant

class Ilsa(IlsaCompositeBase, IlsaObserverBase):
    STATE_OLD = None
    STATE_CURRENT = None 
    
    def __init__(self, mainWindowWidget, fileConfig=None):
        logging.debug("In Ilsa::__init__()")
        self._mainWindowWidget = mainWindowWidget
        self._activeSubWindow = None
        self._plugins = []
        #TODO ML 500k a 800k ~ de memoryleak ao carregar plugins(pode ser bug da toolbar)
        configure.init_resources()
        self.load(fileConfig)
        self._pluginYamlPath = None
        
    def loadGroup(self, groupName):
        pluginsUnordered = extensions.get(group=groupName)
        plugins = {}
        for plugin in pluginsUnordered:
            split = plugin.name.split("-")
            plugins[int(split[0])] = plugin

        for key, plugin in sorted(plugins.iteritems()):
            data = plugin.load()
            if issubclass(data, PluginBase):
                pluginObject = data(IlsaPlugin(self._mainWindowWidget))
                pluginObject.name = plugin.name
                if  pluginObject.status:
                    if pluginObject.separator:
                        self.add(None)
                    self.add(pluginObject)

    def load(self, fileConfig=None):
        logging.debug("In Ilsa::load()")
        filename = os.path.join(constant.INSTALL_DIR, "resources/ilsa/plugin.conf")
        extensions.register_file(filename)
        self.loadGroup("widget")
        self.loadGroup("camera")
        for plugin in self._plugins:
            for pl in self._plugins:
                if pl.name != plugin.name:
                    plugin.ilsa.add(pl)

                    
    def update(self, activeSubWindow):
        logging.debug("In Ilsa::activeSubWindow()")
        self._activeSubWindow = activeSubWindow
                    
    def add(self, plugin):
        logging.debug("In Ilsa::add()")
        if not plugin in self._plugins:
            self._plugins.append(plugin)
        else:
            if plugin is None:
                self._plugins.append(None)
            
    def remove(self, plugin):
        logging.debug("In Ilsa::remove()")
        try:
            self._plugins.remove(plugin)
        except ValueError, e:
            logging.error(e)
        
    def notify(self, state=None):
        logging.debug("In Ilsa::notify()")
        self.STATE_OLD = self.STATE_CURRENT
        self.STATE_CURRENT = state
        for plugin in self._plugins:
            plugin.notify(self.STATE_CURRENT)
        
    def childs(self, index=None):
        logging.debug("In Ilsa::childs()")
        if index is None:
            return set(self._plugins)
        return set(self._plugins[index])
    
    def lenght(self, index=None):
        logging.debug("In Ilsa::lenght()")
        if index is None:
            return len(self.childs())
        return len(self.childs(index))
    @property
    def pluginYamlPath(self):
        return self._pluginYamlPath
    
    @pluginYamlPath.setter
    def pluginYamlPath(self, pluginYamlPath):
        self._pluginYamlPath = pluginYamlPath
    
    def loadFromFile(self, dicomProcess, start, progressRange):
        if self._pluginYamlPath:
            all_plugins = load_vtis_from_yaml_file(self._pluginYamlPath)
            if all_plugins:
                for i, pluginData in enumerate(all_plugins):
                    pluginType = pluginData["type"]
                    plugin = None
                    for plugin in self._plugins:
                        if plugin.type == pluginType:
                            dicomProcess.setProgress(start + i*progressRange/len(all_plugins), QtGui.QApplication.translate("Ilsa", 
                                                     "Loading pluging: {0}", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8).format(plugin.name.split("-")[1]))
                            #import time
                            #a = time.time()
                            plugin.restore(pluginData["value"])
                            #print plugin.name, time.time()-a
                    progress =  start + (i+1)*progressRange/len(all_plugins)
                    if plugin:
                        dicomProcess.setProgress(progress, QtGui.QApplication.translate("Ilsa", 
                                                     "Loading pluging: {0}", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8).format(plugin.name.split("-")[1]))
                    
                
        
    def save(self):
        yamlFile = []
        for plugin in self._plugins :
            yamlPlugin = plugin.save()
            if yamlPlugin:
                yamlFile.append(yamlPlugin)
        return yamlFile
        
    def addScene(self, scene):
        for plugin in self._plugins:
            plugin.addScene(scene)
            
    def removeScene(self, scene):
        for plugin in self._plugins:
            plugin.removeScene(scene)


    def loadScreen(self):
        for plugin in self._plugins:
            plugin.loadScreen()

    def removeAllScenes(self):
        for plugin in self._plugins:
            plugin.removeAllScenes()