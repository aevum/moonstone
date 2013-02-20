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

from ....bloodstone.scenes.imageplane import VtkImagePlane

class Protractor(vtk.vtkAngleWidget):

    def __init__(self, scene=None):
        logging.debug("In Protractor::__init__()")
        self._status = 0
        self.handle = vtk.vtkPointHandleRepresentation2D()
        self.rep = vtk.vtkAngleRepresentation2D()
        self.rep.SetHandleRepresentation(self.handle)
        self.CreateDefaultRepresentation()
        self.SetRepresentation(self.rep)
        self._started = False
        self._pointColor = self.handle.GetProperty().GetColor()
        self._lineColor = self.rep.GetRay1().GetProperty().GetColor()
        self._fontColor = self.rep.GetArc().GetLabelTextProperty().GetColor()
        self._placePointEvent = self.AddObserver("PlacePointEvent", self._startEvent)

    def desactivate(self):
        logging.debug("In Protractor::desactivate()")
        self.Off()
        self.RemoveObserver(self._placePointEvent)

    def started(self):
        logging.debug("In Protractor::started()")
        return self._started

    def scene(self):
        logging.debug("In Protractor::scene()")
        return self._scene       
        
    def setScene(self, scene):
        logging.debug("In Protractor::setScene()")
        self._scene = scene
        self.SetInteractor(scene.interactor)
        self.activate()
        
    def mouseEvent(self):
        logging.debug("In Protractor::mouseEvent()")
        return self._mouseEvent

    def activate(self):
        logging.debug("In Protractor::activate()")
        if not self.GetEnabled():
            self.On()
    
    def status(self):
        return self._status
    
    def _startEvent(self, obj, evt):
        logging.debug("In Protractor::_startEvent()")
        self._status = self._status + 1
        self._started = True
    
    def pointColor(self):
        logging.debug("In Protractor::pointColor()")
        return self._pointColor
    
    def setPointColor(self, pointColor):
        logging.debug("In Protractor::setPointColor()")
        self._pointColor = pointColor
        self.handle.GetProperty().SetColor(*self._pointColor)
        self._scene.window.Render()
    
    def fontColor(self):
        logging.debug("In Protractor::fontColor()")
        return self._fontColor
    
    def setFontColor(self, fontColor):
        logging.debug("In Protractor::setFontColor()")
        self._fontColor = fontColor
        self.rep.GetArc().GetLabelTextProperty().SetColor(*self._fontColor)
        self._scene.window.Render()
    
        
    def lineColor(self):
        logging.debug("In Protractor::lineColor()")
        return self._lineColor

    def setLineColor(self, lineColor):
        logging.debug("In Protractor::setLineColor()")
        self._lineColor = lineColor
        self.rep.GetRay1().GetProperty().SetColor(*self._lineColor)
        self.rep.GetRay2().GetProperty().SetColor(*self._lineColor)
        self.rep.GetArc().GetProperty().SetColor(*self._lineColor)
        self._scene.window.Render()
    
    def angle(self):
        logging.debug("In Protractor::angle()")
        angle = self.rep.GetAngle()
        if angle:
            return angle
        return 0.0 