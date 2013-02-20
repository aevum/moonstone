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
import abc
import logging

from ..base import IlsaObserverBase


class PluginBase(IlsaObserverBase):
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def __init__(self, ilsaPlugin):
        logging.debug("In PluginBase::__init__()")
        logging.info(":: PluginBase::__init__() not implemented")
        
    @abc.abstractmethod
    def notify(self, *args, **kwargs):
        logging.debug("In PluginBase::notify()")
        logging.info(":: PluginBase::notify() not implemented")

    @abc.abstractmethod
    def save(self):
        logging.debug("In PluginBase::save()")
        logging.info(":: PluginBase::save() not implemented")
    
    @abc.abstractmethod
    def restore(self):
        logging.debug("In PluginBase::restore()")
        logging.info(":: PluginBase::restore() not implemented")
        
    @abc.abstractproperty
    def description(self):
        logging.debug("In PluginBase::description()")
        logging.info(":: PluginBase::description() not implemented")
        
    @abc.abstractproperty
    def separator(self):
        logging.debug("In PluginBase::separator()")
        logging.info(":: PluginBase::separator() not implemented")
        
    @abc.abstractproperty
    def status(self):
        logging.debug("In PluginBase::status()")
        logging.info(":: PluginBase::status() not implemented")
        
    @abc.abstractproperty
    def action(self):
        logging.debug("In PluginBase::action()")
        logging.info(":: PluginBase::action() not implemented")
        
    @abc.abstractproperty
    def name(self):
        logging.debug("In PluginBase::name()")
        logging.info(":: PluginBase::name() not implemented")
    
    @abc.abstractproperty
    def ilsa(self):
        logging.debug("In PluginBase::ilsa()")
        logging.info(":: PluginBase::ilsa() not implemented")
        
    def addScene(self, scene):
        logging.debug("In PluginBase::addScene()")
        logging.info(":: PluginBase::addScene() not implemented")
        
    def removeScene(self, scene):
        logging.debug("In PluginBase::removeScene()")
        logging.info(":: PluginBase::removeScene() not implemented")

    def removeAllScenes(self):
        logging.debug("In PluginBase::removeAllScenes()")
        logging.info(":: PluginBase::removeAllScenes() not implemented")

    def loadScreen(self):
        logging.debug("In PluginBase::loadScreen()")
        logging.info(":: PluginBase::loadScreen() not implemented")

    @property
    def type(self):
        return self.__class__.__name__
    
