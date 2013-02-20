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

from PySide import QtCore, QtGui

from ...bloodstone.scenes.imageplane import VtkImagePlane
from ...bloodstone.scenes.sliceimageplane import VtkSliceImagePlane
from ...bloodstone.scenes.multisliceimageplane import VtkMultiSliceImagePlane
from volumeview import VolumeView
from slicethickness import SliceThickness 

class VolumeView2D(VolumeView):

    def __init__(self, mscreenParent, planeOrientation, resliceTransform=None, parent=None, slices=None):
        logging.debug("In ViewPlane2D::__init__()")
        self.slices = slices
        super(VolumeView2D, self).__init__(mscreenParent, planeOrientation, resliceTransform, parent)
    
    def createWidgets(self):
        logging.debug("In ViewPlane2D::createWidgets()")
        super(VolumeView2D, self).createWidgets()
        self.actionThickness = QtGui.QAction(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/static/default/icon/48x48/thickness.png"), 
                       QtGui.QIcon.Normal, 
                       QtGui.QIcon.Off)
        self.actionThickness.setIcon(icon)
        self.actionThickness.setObjectName("actionThickness")
        self.toolbar.addAction(self.actionThickness)
        self.sliceThickness = SliceThickness(self)
                
                    
    def createActor(self, vtkImageData):
        logging.debug("In ViewPlane2D::createActor()")
        self.scene.input = vtkImageData
        if self._planeOrientation == -2:
            self.scene.setSlices(self.slices)
        self.scene.planeOrientation = self._planeOrientation
        if self._planeOrientation == VtkImagePlane.PLANE_ORIENTATION_SAGITTAL:
            self._spacingIndex = 0
        elif self._planeOrientation == VtkImagePlane.PLANE_ORIENTATION_CORONAL:
            self._spacingIndex = 1
        elif self._planeOrientation == VtkImagePlane.PLANE_ORIENTATION_AXIAL:
            self._spacingIndex = 2
        elif self._planeOrientation == -2:
            self._spacingIndex = 2
        else:
            raise "This is not a valid plane for create actor"
        
        self.scene.updateCamera()
        
        self.scene.enabled()
        if not self.scene.sliceThickness:
            self._planeSlideValue = 0
            self.sliceThickness.thicknessSpin.setValue(
                    self.scene.imagedata.GetSpacing()[self._spacingIndex])
        self.defaultThicknessSpin = self.scene.imagedata.GetSpacing()[self._spacingIndex]
        self.scene.activateText = True
        
    def createActions(self):
        logging.debug("In ViewPlane2D::createActions()")
        super(VolumeView2D, self).createActions()
        self.connect(self.planeSlide, QtCore.SIGNAL("valueChanged(int)"),
                     self.slotPlaneSlideChanged)
        self.connect(self.sliceThickness.thicknessSpin, 
                     QtCore.SIGNAL("valueChanged ( double)"), 
                     self.slotChangeThickness)
        self.connect(self.actionThickness, QtCore.SIGNAL("triggered()"),
                     self.slotActionThickness)
        
    @property
    def planeSlideValue(self):    
        logging.debug("In ViewPlane2D::planeSlideValue.getter()")
        return self._planeSlideValue
     
    def slotActionThickness(self):
        logging.debug("In ViewPlane2D::slotActionThickness()")
        self.sliceThickness.show()
     
    def slotChangeThickness(self, value):
        logging.debug("In ViewPlane2D::slotChangeThickness()")
        self.planeSlide.setValue(0)
        self.scene.sliceThickness = value
        if self._planeOrientation == -2:
            slicer = self.scene.getSlideSize()
            self._planeSlideValue = slicer/2
        else:
            slicer = (self.scene.imagedata.GetBounds()[self._spacingIndex*2 + 1] - \
                      self.scene.imagedata.GetBounds()[self._spacingIndex*2])/value
        self.planeSlide.setRange(0, slicer)
        self.planeSlide.setValue(slicer/2.0)
        self.planeSlide.setVisible(True)
        
        
    def slotPlaneSlideChanged(self, value):
        logging.debug("In ViewPlane2D::slotPlaneSlideChanged()")
        logging.debug("+ value: {0}".format(value))
        if self._planeOrientation == -2:
            self.scene.slicePosition = value        
        else:
            self.scene.slicePosition = (value - self._planeSlideValue)*self.scene.sliceThickness
        self.scene.topLeftTextActor.GetMapper().SetInput(QtGui.QApplication.translate("ViewPlane2D", 
                                                     "Slice : {0}", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8).format(value+1))
        #self.scene.bottomLeftTextActor.GetMapper().SetInput("Bottom : {0}".format(value+1))
        self.scene.renderer.ResetCameraClippingRange()
        self.scene.render()
        self._planeSlideValue = value
        
    def reset(self):
        self.sliceThickness.thicknessSpin.setValue(self.sliceThickness.defaultThicknessSpin)
        self.toolbar.setMaximumHeight(0)
        self.scene.reset()
        
    def load(self, data):
        if data.has_key("id"):
            self.setSceneId(data["id"])
        if data.has_key("sliceThickness"):
            self.sliceThickness.thicknessSpin.setValue(data["sliceThickness"])
            self.defaultThicknessSpin = data["sliceThickness"]
        
            
            
