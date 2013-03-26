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

class Protractor(object):

    def __init__(self, scene=None):
        logging.debug("In Protractor::__init__()")
        self._status = 0
        self._angleWidget = vtk.vtkAngleWidget()
        self._handle = vtk.vtkPointHandleRepresentation3D()
        self._representation = vtk.vtkAngleRepresentation2D()
        self._representation.SetHandleRepresentation(self._handle)
        self._angleWidget.CreateDefaultRepresentation()
        self._angleWidget.SetRepresentation(self._representation)
        self._angleWidget.parent = self
        self._started = False
        self._pointColor = self._handle.GetProperty().GetColor()
        self._lineColor = self._representation.GetRay1().GetProperty().GetColor()
        self._fontColor = self._representation.GetArc().GetLabelTextProperty().GetColor()
        self._placePointEvent = self._angleWidget.AddObserver("PlacePointEvent", self._startEvent)

    def desactivate(self):
        logging.debug("In Protractor::desactivate()")
        self._angleWidget.Off()
        self._angleWidget.RemoveObserver(self._placePointEvent)

    def started(self):
        logging.debug("In Protractor::started()")
        return self._started

    @property
    def angleWidget(self):
        logging.debug("In Protractor::angleWidget.getter()")
        return self._angleWidget

    @property
    def scene(self):
        logging.debug("In Protractor::scene()")
        return self._scene       

    @scene.setter
    def scene(self, scene):
        logging.debug("In Protractor::scene.setter()")
        self._scene = scene
        self._angleWidget.SetInteractor(scene.interactor)
        self.activate()
        
    def mouseEvent(self):
        logging.debug("In Protractor::mouseEvent()")
        return self._mouseEvent

    def activate(self):
        logging.debug("In Protractor::activate()")
        if not self._angleWidget.GetEnabled():
            self._angleWidget.On()
    
    @property
    def status(self):
        return self._status
    
    def _startEvent(self, obj, evt):
        logging.debug("In Protractor::_startEvent()")
        self._status = self._status + 1
        self._started = True

    @property
    def pointColor(self):
        logging.debug("In Protractor::pointColor()")
        return self._pointColor

    @pointColor.setter
    def pointColor(self, pointColor):
        logging.debug("In Protractor::setPointColor()")
        self._pointColor = pointColor
        self._handle.GetProperty().SetColor(*self._pointColor)
        self._scene.window.Render()

    @property
    def fontColor(self):
        logging.debug("In Protractor::fontColor()")
        return self._fontColor
    
    @fontColor.setter
    def fontColor(self, fontColor):
        logging.debug("In Protractor::setFontColor()")
        self._fontColor = fontColor
        self._representation.GetArc().GetLabelTextProperty().SetColor(*self._fontColor)
        self._scene.window.Render()

    @property
    def lineColor(self):
        logging.debug("In Protractor::lineColor()")
        return self._lineColor

    @lineColor.setter
    def lineColor(self, lineColor):
        logging.debug("In Protractor::setLineColor()")
        self._lineColor = lineColor
        self._representation.GetRay1().GetProperty().SetColor(*self._lineColor)
        self._representation.GetRay2().GetProperty().SetColor(*self._lineColor)
        self._representation.GetArc().GetProperty().SetColor(*self._lineColor)
        self._scene.window.Render()

    @property
    def angle(self):
        logging.debug("In Protractor::angle()")
        angle = self._representation.GetAngle()
        if angle:
            return angle
        return 0.0