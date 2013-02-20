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

from ..base import PluginBase
from gui.qt.contrastandbrightnessaction import ContrastAndBrightnessAction


class ContrastAndBrightnessPlugin(PluginBase):
        
    def __init__(self, ilsa):
        logging.debug("In ContrastAndBrightnessPlugin::__init__()")
        self._name = None
        self._action = ContrastAndBrightnessAction(ilsa)
        ilsa.add(self)
        self._ilsa = ilsa

    @property
    def ilsa(self):
        logging.debug("In ContrastAndBrightnessPlugin::ilsa()")
        return self._ilsa  
        
    @property
    def action(self):
        logging.debug("In ContrastAndBrightnessPlugin::action()")
        return self._action
        
    @property
    def name(self):
        logging.debug("In ContrastAndBrightnessPlugin::name()")
        return self._name
    
    @name.setter
    def name(self, name):
        logging.debug("In ContrastAndBrightnessPlugin::name.setter()")
        self._name = name
        
    def notify(self, vtkInteractorStyle=None):
        logging.debug("In ContrastAndBrightnessPlugin::notify()")

    def save(self):
        logging.debug("In ContrastAndBrightnessPlugin::save()")
        value = self._action.save()
        save = {"type" :  self.type, "value" : value}
        return save
        
    def restore(self, value = None):
        logging.debug("In ContrastAndBrightnessPlugin::restore()")
        if value:
            self._action.restore(value)
    @property
    def description(self):
        logging.debug("In ContrastAndBrightnessPlugin::description()")
        return "..."
    
    @property
    def separator(self):
        logging.debug("In ContrastAndBrightnessPlugin::separator()")
        return False
    
    @property
    def status(self):
        logging.debug("In ContrastAndBrightnessPlugin::status()")
        return True
    
    def addScene(self, scene):
        self._action.addScene(scene)
