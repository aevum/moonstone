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

from ..base import PluginBase
from gui.qt.ruleraction import RulerAction


class MeasurePlugin(PluginBase):
    def __init__(self, ilsa):
        self._ilsa = ilsa
        self._name = None
        self._action = RulerAction(self._ilsa)
        ilsa.add(self)
        
    @property
    def ilsa(self):
        logging.debug("In MeasurePlugin::ilsa()")
        return self._ilsa
        
    @property
    def action(self):
        logging.debug("In MeasurePlugin::action()")
        return self._action
        
    @property
    def name(self):
        logging.debug("In MeasurePlugin::name()")
        return self._name
    
    @name.setter
    def name(self, name):
        logging.debug("In MeasurePlugin::name.setter()")
        self._name = name

    def notify(self, *args, **kwargs):
        logging.debug("In MeasurePlugin::notify()")
    
    def save(self):
        logging.debug("In MeasurePlugin::save()")
        
    def restore(self):
        logging.debug("In MeasurePlugin::restore()")
    
    @property
    def description(self):
        logging.debug("In MeasurePlugin::description()")
        return "..."
    
    @property
    def separator(self):
        logging.debug("In MeasurePlugin::separator()")
        return False
    
    @property
    def status(self):
        logging.debug("In MeasurePlugin::status()")
        return True
    
    def removeScene(self, scene):
        self._action.removeScene(scene)
