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

from ..base import PluginBase
from gui.qt.translateaction import TranslateAction


class TranslatePlugin(PluginBase):
        
    def __init__(self, ilsa):
        logging.debug("In TranslatePlugin::__init__()")
        self._name = None
        self._action = TranslateAction(ilsa)
        ilsa.add(self)
        self._ilsa = ilsa

    @property
    def ilsa(self):
        logging.debug("In TranslatePlugin::ilsa()")
        return self._ilsa
        
    @property
    def action(self):
        logging.debug("In TranslatePlugin::action()")
        return self._action
        
    @property
    def name(self):
        logging.debug("In TranslatePlugin::name()")
        return self._name
    
    @name.setter
    def name(self, name):
        logging.debug("In TranslatePlugin::name.setter()")
        self._name = name
        
    def notify(self, vtkInteractorStyle=None):
        logging.debug("In TranslatePlugin::notify()")
        
    def save(self):
        logging.debug("In TranslatePlugin::save()")
        
    def restore(self):
        logging.debug("In TranslatePlugin::restore()")
    
    @property
    def description(self):
        logging.debug("In TranslatePlugin::description()")
        return "..."
    
    @property
    def separator(self):
        logging.debug("In TranslatePlugin::separator()")
        return False
    
    @property
    def status(self):
        logging.debug("In TranslatePlugin::status()")
        return True

