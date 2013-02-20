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
import types
import logging

import vtk

from interactor import VtkInteractor 


class VtkScene(VtkInteractor):
    
    def __init__(self, vtkInteractor):
        logging.debug("In VtkScene::__init__()")
        super(VtkScene, self).__init__(vtkInteractor)
        self.placeFactor = 0.5
        
        self.color = (1, 0, 0)
        self.normalCanonical = (0, 0, 1)
        self.matrixCanonical = (
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1
        )
        
        self._lastObserver = 0
        self._observers = {}
        self._activeObservers = {}
        self._renderObservers = {}
        self._renderObserverLastIndex = 0
        
    def adjustBounds(self, bounds, newBounds, center):
        logging.debug("In VtkScene::adjustBounds()")
        center[0] = (bounds[0] + bounds[1])/2.0
        center[1] = (bounds[2] + bounds[3])/2.0
        center[2] = (bounds[4] + bounds[5])/2.0
        
        newBounds[0] = center[0] + self.placeFactor*(bounds[0]-center[0])
        newBounds[1] = center[0] + self.placeFactor*(bounds[1]-center[0])
        newBounds[2] = center[1] + self.placeFactor*(bounds[2]-center[1])
        newBounds[3] = center[1] + self.placeFactor*(bounds[3]-center[1])
        newBounds[4] = center[2] + self.placeFactor*(bounds[4]-center[2])
        newBounds[5] = center[2] + self.placeFactor*(bounds[5]-center[2])
        
    def initialize(self):
        logging.debug("In VtkScene::initialize()")
                
    def createActor(self, vtkImageData):
        logging.debug("In VtkScene::createActor()")
        logging.warning("VtkScene::createActor() not implemented")
        
    def addObserver(self, event, action):
        index = self.interactorStyle.AddObserver(
                            event, action)
        if not self._observers.has_key(event):
            self._observers[event] = []
        self._observers[event].append({'id' : index, 'index' : index, 'action': action})
        if self._activeObservers.has_key(event):
            self.interactorStyle.RemoveObserver(self._activeObservers[event]["index"])
        self._activeObservers[event] = {'id' : index, 'index' : index, 'action': action}
        return index
    
    def invokeEvent(self, event):
        for evt, action, lastObserver in self._observers.values():
            if evt == event:
                try:
                    action(None,None)
                except:
                    logging.warning("Method not found")
    
    def removeObserver(self, id, recreateOnEmpty = True):
        eventToDelete = None
        for event, valueList in self._observers.items():
            for i, value in enumerate(valueList):
                if value['id'] == id:
                    valueList.pop(i)
                    eventToDelete = event
                    break
            if eventToDelete:
                if self._activeObservers[eventToDelete]['id'] == id:
                    self.interactorStyle.RemoveObserver(self._activeObservers[eventToDelete]["index"])
                    if self._observers[eventToDelete]:
                        nextEvent = self._observers[eventToDelete][
                                                len(self._observers[eventToDelete])-1]
                        index = self.interactorStyle.AddObserver(
                            eventToDelete, nextEvent['action'])
                        nextEvent['index'] = index
                        self._activeObservers[eventToDelete] = nextEvent
        if recreateOnEmpty and len(self._observers) == 0:
            self.interactorStyle = self.createInteractorStyle()

    def createInteractorStyle(self):
        return vtk.vtkInteractorStyleImage()
     
    def render(self):
        self.window.Render()       
            