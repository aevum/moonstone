import vtk

class Ruler(vtk.vtkDistanceWidget):


    def __init__(self, scene=None):
        self.scene = scene
        self.handle = vtk.vtkPointHandleRepresentation2D()
        self.rep = vtk.vtkDistanceRepresentation2D()
        self.rep.SetHandleRepresentation(self.handle)
        self.CreateDefaultRepresentation()
        self.SetRepresentation(self.rep)
        self._started = False
        self.pointColor = self.handle.GetProperty().GetColor()
        self.lineColor = self.rep.GetAxis ().GetProperty ().GetColor()
        self.fontColor = self.rep.GetAxis ().GetTitleTextProperty ().GetColor()
        self.AddObserver("PlacePointEvent", self.startEvent)

    def getStarted(self):
        return self._started

    def setScene(self, scene):
        self.scene = scene
        self.SetInteractor(scene.interactor)

    def activate(self):
        if not self.GetEnabled():
            self.On()
    
    def startEvent(self, obj, evt):
        self._started = True

    def setPointColor(self, red, green, blue):
        self.pointColor = (red, green, blue)
        self.handle.GetProperty().SetColor(self.pointColor)

    def setLineColor(self, red, green, blue):
        self.lineColor = (red, green, blue)
        self.rep.GetAxis ().GetProperty ().SetColor(self.lineColor)

    def setFontColor(self, red, green, blue):
        self.fontColor = (red, green, blue)
        self.rep.GetAxis ().GetTitleTextProperty ().SetColor(self.fontColor)

    def getFontColor(self):
        return self.fontColor

    def getLineColor(self):
        return self.lineColor

    def getPointColor(self):
        return self.pointColor

    def getMeasure(self):
        return self.rep.GetDistance()