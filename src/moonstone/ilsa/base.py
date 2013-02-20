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


class IlsaSubjectBase(object):
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def add(self, observer):
        logging.debug("In IlsaSubjectBase::register()")
        logging.info(":: IlsaSubjectBase::register() not implemented")
        
    @abc.abstractmethod
    def remove(self, observer):
        logging.debug("In IlsaSubjectBase::remove()")
        logging.info(":: IlsaSubjectBase::remove() not implemented")
        
    @abc.abstractmethod
    def notify(self):
        logging.debug("In IlsaSubjectBase::notify()")
        logging.info(":: IlsaSubjectBase::notify() not implemented")


class IlsaObserverBase(object):
    __metaclass__ = abc.ABCMeta
        
    @abc.abstractmethod
    def notify(self, *args, **kwargs):
        logging.debug("In IlsaObserverBase::notify()")
        logging.info(":: IlsaObserverBase::notify() not implemented")


class IlsaTriggerActionBase(object):
    __metaclass__ = abc.ABCMeta
        
    @abc.abstractmethod
    def trigger(self, *args, **kwargs):
        logging.debug("In IlsaTriggerActionBase::trigger()")
        logging.info(":: IlsaTriggerActionBase::trigger() not implemented")
        

class IlsaCompositeBase(object):
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def add(self, plugin):
        logging.debug("In IlsaCompositeBase::add()")
        logging.info(":: IlsaCompositeBase::add() not implemented")
        
    @abc.abstractmethod
    def remove(self, plugin):
        logging.debug("In IlsaCompositeBase::remove()")
        logging.info(":: IlsaCompositeBase::remove() not implemented")
        
    @abc.abstractmethod
    def childs(self, index=None):
        logging.debug("In IlsaCompositeBase::childs()")
        logging.info(":: IlsaCompositeBase::childs() not implemented")
        
    @abc.abstractmethod
    def lenght(self, index=None):
        logging.debug("In IlsaCompositeBase::lenght()")
        logging.info(":: IlsaCompositeBase::lenght() not implemented")
        
