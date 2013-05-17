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

from PySide import QtCore
from PySide import QtGui

from view import View
from slicethickness import SliceThickness
from blendthickness import BlendThickness

class SliceView(View):

    def __init__(self, mscreenParent, planeOrientation, slice, parent=None, title=None, slicePath=None, planeNumber = 1):
        logging.debug("In SliceView::__init__()")
        self.slice = slice
        self.slicePath = slicePath
        self._planeOrientation = planeOrientation
        super(SliceView, self).__init__( title, mscreenParent, planeNumber )
        self.__closeListeners = []
        self.__sliderReleasedListeners = []

    def closeEvent( self, event ):
        logging.debug("In SliceView::closeEvent()")
        self.closeAction( event )
    
    def changeVisibility(self):            
        self.setVisible(not self.isVisible())
        if  self.isVisible():
            self.resizeAction()
        
    def createWidgets(self):

        logging.debug("In SliceView::createWidgets()")
        super( SliceView, self ).createWidgets()
        self.actionThickness = QtGui.QAction(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/measure.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionThickness.setIcon(icon)
        self.actionThickness.setObjectName("actionThickness")
        self.toolbar.addAction(self.actionThickness)
        self.sliceThickness = SliceThickness(self)
        
        self.actionSlabThickness = QtGui.QAction(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/static/default/icon/48x48/thickness-1.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSlabThickness.setIcon(icon)
        self.actionSlabThickness.setObjectName("actionSlabThickness")
        self.toolbar.addAction(self.actionSlabThickness)
        self.slabThickness = BlendThickness(self)
    
    def splitterMoved(self, a, b):
        self.resizeAction()

    def resizeAction(self):
        size = self.plane.size()
        self.scene.interactor.setGeometry(0, 0, size.width(), size.height())
        self.updateGeometry()

    # def close(self):
    #     print "close"
    #     self.scene.close()
    #     self.scene = None
    #     del self.scene
    #     self.destroy()
    #     self._mscreenParent = None
    #     self.closeEvent = None
    #     #super(SliceView, self).close()

    def closeAction(self, event = None, force=False):
        logging.debug("In SliceViewPlane::closeEvent()")
        if self.scene.referenceCount < 1 or force:
            if not self.mscreenParent.removeScene(self):
                event.ignore()
            else:
                self.notifyCloseListeners()
        else:
            event.ignore()
    
    def update(self, vtkAction):
        logging.debug("In SliceViewPlane::update()")
        super(SliceView, self).update()
        
    def createScene(self):
        logging.debug("In SliceViewPlane::createScene()")
        
    def createActor(self, vtkImageData):
        logging.debug("In SliceViewPlane::createActor()")
        if not self.slice:
            raise "This is not a valid slice for create actor"
        self.scene.input = vtkImageData
        self.scene.setSlice(self.slice, self.slicePath)
        self.scene.planeOrientation = self._planeOrientation
        self.scene.updateCamera()
        self.scene.enabled()
        if not self.scene.sliceThickness:
            self._planeSlideValue = 0
            self.sliceThickness.thicknessSpin.setValue(self.scene.imagedata.GetSpacing()[0])#(getting X spacing) :/
        self.defaultThicknessSpin = self.scene.imagedata.GetSpacing()[0]
        self.scene.activateText = True
        
    def createActions(self):
        logging.debug("In SliceViewPlane::createActions()")
        self.connect( self.planeSlide, QtCore.SIGNAL("valueChanged(int)"), self.slotPlaneSlideChanged )
        self.connect( self.planeSlide, QtCore.SIGNAL( "sliderReleased()" ), self.slotPlaneSlideReleased )
        self.connect( self.sliceThickness.thicknessSpin, QtCore.SIGNAL("valueChanged ( double)"), self.slotChangeThickness )
        self.connect( self.actionThickness, QtCore.SIGNAL("triggered()"), self.slotActionThickness )
        self.connect( self.slabThickness.thicknessSlider, QtCore.SIGNAL("valueChanged(int)"), self.slotChangeSlabThickness )
        self.connect( self.slabThickness.qualitySlider, QtCore.SIGNAL("valueChanged(int)"), self.slotChangeSlabQuality )
        self.connect( self.actionSlabThickness, QtCore.SIGNAL("triggered()"), self.slotActionSlabThickness )

    def slotPlaneSlideChanged(self, value, render=True):
        logging.debug("In SliceViewPlane::slotPlaneSlideChanged()")
        logging.debug("+ value: {0}".format(value))
        self.scene.slicePositionMin = self.planeSlide.minimum()
        self.scene.slicePositionMax = self.planeSlide.maximum()
        self.scene.sliceCurrentPosition = self.planeSlide.value()
        self.scene.slicePosition = value
        self.scene.topLeftTextActor.GetMapper().SetInput( QtGui.QApplication.translate("SingleSlicePlane", "Slice : {0}", None, QtGui.QApplication.UnicodeUTF8).format(value+1) )
        self.scene.renderer.ResetCameraClippingRange()
        self._planeSlideValue = value
        if render:
            self.scene.window.Render()
        if not self.planeSlide.isSliderDown():
            self.scene.updatePlaneCutter()
            self.notifySliderReleasedListeners()

    def slotPlaneSlideReleased( self ):
        logging.debug("In SliceViewPlane::slotPlaneSlideReleased()")
        self.notifySliderReleasedListeners()
        self.scene.updatePlaneCutter()

    def slotChangeThickness(self, value):

        logging.debug("In SliceViewPlane::slotChangeThickness()")
        self.scene.sliceThickness = value
        slicer = self.scene.getSlideSize()
        self._planeSlideValue = slicer/2
        self.planeSlide.setRange(0, slicer)
        self.planeSlide.setValue(slicer/2.0)
        self.planeSlide.setVisible(True)

    def slotActionThickness(self):

        logging.debug("In SliceViewPlane::slotActionThickness()")
        self.sliceThickness.move( QtGui.QCursor.pos() - QtCore.QPoint(0, self.sliceThickness.height()) )
        self.sliceThickness.show()

    def slotChangeSlabThickness(self, value):

        logging.debug("In SliceViewPlane::slotChangeThickness()")
        self.scene.slabThickness = value
        self.slabThickness.thicknessLabel.setText("{0}mm".format(float(self.scene.slabThickness)))
        self.scene.updatePlane()
        self.scene.window.Render()

    def slotChangeSlabQuality(self, value):
        logging.debug("In SliceViewPlane::slotChangeThickness()")
        spacin = self.scene.slabSpacing
        spacin[2] = 1 - value * .1
        self.scene.updatePlane()
        self.scene.window.Render()

    def slotActionSlabThickness(self):
        logging.debug("In SliceViewPlane::slotActionThickness()")
        zspacin = self.scene.slabSpacing[2]
        self.slabThickness.qualitySlider.setValue(int(round(10 - 10 * zspacin)))
        self.slabThickness.thicknessSlider.setValue(self.scene.slabThickness)
        self.slabThickness.thicknessLabel.setText("{0}mm".format(float(self.scene.slabThickness)))
        self.slabThickness.move( QtGui.QCursor.pos() - QtCore.QPoint(0, self.slabThickness.height()) )
        self.slabThickness.show()

    @property
    def planeSlideValue(self):
        logging.debug("In SingleSlicePlane::planeSlideValue.getter()")
        return self._planeSlideValue
        
    def updateWidgets(self):
        logging.debug("In SliceViewPlane::updateWidgets()")
        self.planeSlide.setVisible(False)
        self.setWindowTitle(self.title)
        
    def reset(self):
        logging.debug("In SliceViewPlane::reset()")
        self.sliceThickness.thicknessSpin.setValue(self.sliceThickness.defaultThicknessSpin)
        self.splitter.setSizes([1,0])
        self.resizeAction()
        self.scene.reset()
    
    @property
    def mscreenParent(self):
        logging.debug("In SliceViewPlane::mscreenParent.getter()")
        return self._mscreenParent
    
    @mscreenParent.setter
    def mscreenParent(self, mscreenParent):
        logging.debug("In SliceViewPlane::mscreenParent.setter()")
        self._mscreenParent = mscreenParent
             
    @property
    def id(self):
        logging.debug("In SliceViewPlane::id.getter()")
        return self._id
    
    def setSceneId(self, id):
        self.scene.id = id
    
    @property
    def planeOrientation(self):
        logging.debug("In SliceViewPlane::planeOrientation.getter()")
        return self._planeOrientation
    @property
    def mainImageData(self):
        return self._mscreenParent.mainImageData
        
    def getScreen(self):
        return self._mscreenParent

    def load( self, data):
        if data.has_key("id"):
            self.setSceneId(data["id"])
        if data.has_key("sliceThickness"):
            self.sliceThickness.thicknessSpin.setValue(data["sliceThickness"])
            self.defaultThicknessSpin = data["sliceThickness"]
        if data.has_key("slabSpacing"):
            self.scene.slabSpacing = data["slabSpacing"]
        if data.has_key("slabThickness"):
            self.scene.slabThickness = data["slabThickness"]
            self.scene.updatePlane()
        if data.has_key("slicePosition"):
            self.slotPlaneSlideChanged(data["slicePosition"])
        if data.has_key("cameraPosition"):
            self.scene.camera.SetViewUp(data["cameraViewUp"])
            self.scene.camera.SetPosition(data["cameraPosition"])
            self.scene.camera.SetFocalPoint(data["cameraFocal"])
            self.scene.camera.SetParallelScale(data["cameraZoom"])

    def notifyCloseListeners( self ):

        listeners = [ x for x in self.__closeListeners ]
        for listener in listeners:
            listener( self )

    def addCloseListener( self, listener ):

        if listener not in self.__closeListeners:
            self.__closeListeners.append( listener )

    def removeCloseListener( self, listener ):

        if listener in self.__closeListeners:
            self.__closeListeners.remove( listener )

    def notifySliderReleasedListeners( self ):

        listeners = [ x for x in self.__sliderReleasedListeners ]
        for listener in listeners:
            listener( self )

    def addSliderReleasedListeners( self, listener ):

        if listener not in self.__sliderReleasedListeners:
            self.__sliderReleasedListeners.append( listener )

    def removeSliderReleasedListeners( self, listener ):

        if listener in self.__sliderReleasedListeners:
            self.__sliderReleasedListeners.remove( listener )