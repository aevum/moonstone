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
import logging
import vtk

from ..base import PluginBase
from gui.qt.pointeraction import PointerAction


class PointerPlugin(PluginBase):
        
    def __init__(self, ilsa):
        logging.debug("In PointerPlugin::__init__()")
        self._name = None
        self._action = PointerAction(ilsa)
        ilsa.add(self)
        self._ilsa = ilsa

    @property
    def ilsa(self):
        logging.debug("In PointerPlugin::ilsa()")
        return self._ilsa
    @property
    def action(self):
        logging.debug("In PointerPlugin::action()")
        return self._action
        
    @property
    def name(self):
        logging.debug("In PointerPlugin::name()")
        return self._name
    
    @name.setter
    def name(self, name):
        logging.debug("In PointerPlugin::name.setter()")
        self._name = name
        
    def notify(self, vtkInteractorStyle=None):
        logging.debug("In PointerPlugin::notify()")
    
    def save(self):
        logging.debug("In PointerPlugin::save()")
        
    def restore(self):
        logging.debug("In PointerPlugin::restore()")
    
    @property
    def description(self):
        logging.debug("In PointerPlugin::description()")
        return "..."
    
    @property
    def separator(self):
        logging.debug("In PointerPlugin::separator()")
        return False
    
    @property
    def status(self):
        logging.debug("In PointerPlugin::status()")
        return True
    
    