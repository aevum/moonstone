import logging

from PySide import QtGui
import vtk

class TextWidget(vtk.vtkBorderWidget):

    def __init__(self, scene=None):
        logging.debug("In TextWidget::__init__()")
        self.property = vtk.vtkTextProperty()
        self.fontColor = [1,1,1]
        self.position = [0.15 ,0.15]
        self._started = False
        self._fontSize = 12
        self._visible = 1
        self._bold = 0
        self._italic = 0
        self._font = "Arial"
        self.ResizableOff()
        self.textActor = None
        self.scene = None
        self.text = QtGui.QApplication.translate("TextWidget", 
                                                     "text", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8)
        if scene:
            self.setScene(scene)
        
        
    def setScene(self, scene):
        logging.debug("In TextWidget::setScene()")
        if self.scene:
            return
        self.scene = scene
        self.rep = vtk.vtkBorderRepresentation()
        self.rep.GetPositionCoordinate().SetValue( self.position[0],self.position[1] )
        self.rep.GetPosition2Coordinate().SetValue( .2, .045 )
        self.CreateDefaultRepresentation()
        self.SetRepresentation(self.rep)
        self.rep.SetShowBorderToActive() 
        self.SetInteractor(self.scene.interactor)
        self._observers = []
        self._observers.append(self.AddObserver("StartInteractionEvent", self.startInteractionAction))
        self._observers.append(self.AddObserver("InteractionEvent", self.interactionAction))
        self.startEvent()
    
    def startEvent(self):
        logging.debug("In TextWidget::startEvent()")
        if not self._started: 
            self._started = True
            self.setText(self.text)
            coord = vtk.vtkCoordinate()
            coord.SetCoordinateSystemToNormalizedDisplay()
            coord.SetValue(self.position[0], self.position[1])
            pos = coord.GetComputedDisplayValue(self.scene.renderer)
            x = self.position[0]/pos[0]
            y = self.position[1]/pos[1]
            pos = self.scene.interactor.GetEventPosition()
            self.position[0] = pos[0]*x
            self.position[1] = pos[1]*y
            
            self.rep.GetPositionCoordinate().SetValue(self.position[0], self.position[1])
            self.setText(self.text)
            self.On()
    
    def startInteractionAction(self, obj, evt):
        logging.debug("In TextWidget::startInteractionAction()")
    
    def interactionAction(self, obj, evt):
        logging.debug("In TextWidget::interactionAction()")
        if self.textActor and self.text:
            self.autoResizeBox()
            
    def removeObservers(self):
        for observer in self._observers:
            self.RemoveObserver(observer)
            
    def autoResizeBox(self):
        logging.debug("In TextWidget::autoResizeBox()")
        self.position = list(self.rep.GetPositionCoordinate().GetValue())
        self.textActor.GetPositionCoordinate().SetValue(self.position)
        p2 = list(self.rep.GetPosition2Coordinate().GetValue())
        x = len(self.text)*0.016
        p2[0] = x
        self.rep.GetPosition2Coordinate().SetValue(p2)
    
    def setPosition(self, position):
        logging.debug("In TextWidget::setPosition()")
        self.rep.GetPositionCoordinate().SetValue(*position)
        self.position = position
        self._started = True
        self.On()
        
    def getText(self):
        logging.debug("In TextWidget::getText()")
        return self.text
    
    def getFontColor(self):
        logging.debug("In TextWidget::getFontColor()")
        return self.fontColor
    
    def getStarted(self):
        logging.debug("In TextWidget::getStarted()")
        return self._started
    
    def setFontColor(self, red, green, blue):
        logging.debug("In TextWidget::setFontColor()")
        self.fontColor = (red, green, blue)
        self.property.SetColor(self.fontColor)
        self.scene.window.Render()
        
    def setBold(self, bold):
        logging.debug("In TextWidget::setBold()")
        self.property.SetBold(bold)
        self._bold = bold
        self.scene.window.Render()
    
    def getBold(self):
        logging.debug("In TextWidget::getBold()")
        return self._bold
    
    def setFontSize(self, size):
        logging.debug("In TextWidget::setFontSize()")
        self.property.SetFontSize(size)
        self._fontSize = size
        self.scene.window.Render()
    
    def getFontSize(self):
        logging.debug("In TextWidget::getFontSize()")
        return self._fontSize
    
    def setFont(self, font):
        logging.debug("In TextWidget::setFont()")
        self.property.SetFontFamilyAsString(str(font))
        self._font = font
        self.scene.window.Render()
    
    def getFont(self):
        logging.debug("In TextWidget::getFont()")
        return self._font
    
    def setItalic(self, italic):
        logging.debug("In TextWidget::setItalic()")
        self.property.SetItalic(italic)
        self._italic = italic
        self.scene.window.Render()
    
    def getItalic(self):
        logging.debug("In TextWidget::getItalic()")
        return self._italic
    
    def setVisible(self, visible):
        logging.debug("In TextWidget::setVisible()")
        self.textActor.SetVisibility(visible)
        self._visible = visible
        self.scene.window.Render()
    
    def getVisible(self):
        logging.debug("In TextWidget::getVisible()")
        return self._visible
    
    def setText(self, text):
        logging.debug("In TextWidget::setText()")
        self.text = text
        if self.scene:
            self.property.SetJustificationToLeft()
            self.property.SetVerticalJustificationToBottom()
            self.property.SetColor(self.fontColor)
    
            self.mapper = vtk.vtkTextMapper()
            self.mapper.SetTextProperty(self.property)
            self.mapper.SetInput(self.text)
            if self.textActor:
                self.scene.renderer.RemoveActor(self.textActor)
            self.textActor = vtk.vtkActor2D()
            self.textActor.SetMapper(self.mapper)
            self.textActor.PickableOff()
            self.textActor.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
            self.textActor.GetPositionCoordinate().SetValue(self.position[0], self.position[1])
            self.textActor.VisibilityOn()
            self.scene.renderer.AddActor(self.textActor)   
            self.autoResizeBox()
            self.scene.window.Render()
            
    def save(self):
        logging.debug("In TextWidget::save()")
        yaml = {}
        yaml["fontColor"] = self.fontColor
        yaml["position"] = self.rep.GetPosition()
        yaml["text"] = self.text
        yaml["sceneId"] = self.scene.id
        yaml["bold"] = self.getBold()
        yaml["italic"] = self.getItalic()
        yaml["visible"] = self.getVisible()
        yaml["font"] = self.getFont()
        yaml["fontSize"] = self.getFontSize()
        return yaml
