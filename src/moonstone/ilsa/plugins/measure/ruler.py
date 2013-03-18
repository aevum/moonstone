import logging

import vtk


class Ruler(object):
    def __init__(self, scene=None):
        logging.debug("In Ruler::__init__()")
        self._scene = scene
        self._distanceWidget = vtk.vtkDistanceWidget()
        self._handle = vtk.vtkPointHandleRepresentation3D()
        self._representation = vtk.vtkDistanceRepresentation2D()
        self._representation.SetHandleRepresentation(self._handle)
        self._distanceWidget.SetRepresentation(self._representation)
        self._distanceWidget.CreateDefaultRepresentation()
        self._distanceWidget.parent = self
        self._started = False
        self._pointColor = [0, 1, 0]
        self._lineColor = [0, 1, 0]
        self._fontColor = [0, 1, 0]
        self._distanceWidget.AddObserver("PlacePointEvent", self.startEvent)

    @property
    def representation(self):
        logging.debug("In Ruler::representation.getter()")
        return self._representation

    @property
    def distanceWidget(self):
        logging.debug("In Ruler::distanceWidget.getter()")
        return self._distanceWidget

    @property
    def started(self):
        logging.debug("In Ruler::started.getter()")
        return self._started

    @property
    def scene(self):
        logging.debug("In Ruler::scene.getter()")
        return self._scene

    @scene.setter
    def scene(self, scene):
        logging.debug("In Ruler::scene.setter()")
        self._scene = scene
        self._distanceWidget.SetInteractor(scene.interactor)

    def activate(self):
        logging.debug("In Ruler::activate()")
        if not self._distanceWidget.GetEnabled():
            self._distanceWidget.On()
    
    def startEvent(self, obj, evt):
        logging.debug("In Ruler::startEvent()")
        self._started = True

    @property
    def pointColor(self):
        logging.debug("In Ruler::pointColor.getter()")
        return self._handle.GetProperty().GetColor()


    @pointColor.setter
    def pointColor(self, color):
        logging.debug("In Ruler::pointColor.setter()")
        self._handle.GetProperty().SetColor(color)

    @property
    def lineColor(self):
        logging.debug("In Ruler::lineColor.getter()")
        return self._representation.GetAxis().GetProperty().GetColor()

    @lineColor.setter
    def lineColor(self, color):
        logging.debug("In Ruler::lineColor.setter()")
        self._representation.GetAxis().GetProperty().SetColor(color)

    @property
    def fontColor(self):
        logging.debug("In Ruler::fontColor.getter()")
        return self._representation.GetAxis().GetTitleTextProperty().GetColor()

    @fontColor.setter
    def fontColor(self, color):
        logging.debug("In Ruler::fontColor.setter()")
        self._representation.GetAxis().GetTitleTextProperty().SetColor(color)

    @property
    def measure(self):
        logging.debug("In Ruler::measure.getter()")
        return self._representation.GetDistance()