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

import sys
import vtk
import math

from PySide import QtCore, QtGui

from ...bloodstone.scenes.gui.qt.component.qvtkwidget import QVtkWidget
from ...bloodstone.scenes.sliceimageplane import VtkSliceImagePlane
from volumeview import VolumeView
from multisliceview import MultiSliceView

from sliceview import SliceView

class SingleSliceView(SliceView):

    def __init__(self, mscreenParent, slice, planeOrientation, parent=None, title = None, slicePath = None, planeNumber=1):
        logging.debug("In SingleSlicePlane::__init__()")
        self._referencedPlanes = []
        super(SingleSliceView, self).__init__(mscreenParent, planeOrientation, slice, parent, title, slicePath, planeNumber)
        #self.updateWidgets()

    def activateAllPlanes(self):
        logging.debug("In SingleSlicePlane::activateAllPlanes()")
        if not "Transversal" in self.title :
            flambda = lambda pl: not isinstance( pl, VolumeView ) \
                                     and not isinstance( pl, MultiSliceView ) \
                                     and not pl == self and pl.title != self.title \
                                     and pl.title != "Transversal" \
                and self.title.split()[0] not in pl.title.split()[0]
            for plane in filter(flambda, self._mscreenParent._planes):
                if not plane in self._referencedPlanes:
                    plane.addSliderReleasedListeners( self.onReferedPlanesChange )
                    plane.addCloseListener( self.onReferedPlaneClose )
                    self.addReferencedPlane(plane)
                    self.scene.addLinePlaneWidget( plane.lineWidget() )

    def desactivateAllPlanes(self):
        logging.debug("In SingleSlicePlane::desactivateAllPlanes()")
        if self.title != "Transversal":
            flambda = lambda pl: not isinstance(pl, VolumeView ) \
                                     and not isinstance( pl, MultiSliceView ) \
                                     and not pl == self and pl.title != self.title \
                                     and pl.title != "Transversal" \
                and self.title.split()[0] not in pl.title.split()[0]
            for plane in filter(flambda, self._mscreenParent._planes):
                if plane in self._referencedPlanes:
                    plane.removeSliderReleasedListeners(self.onReferedPlanesChange)
                    plane.removeCloseListener(self.onReferedPlaneClose)
                    self.removeReferencedPlane(plane)
                    self.scene.removeLinePlaneWidget(plane.lineWidget())

    def updateWidgets(self):
        logging.debug("In SingleSlicePlane::updateWidgets()")
        super(SingleSliceView, self).updateWidgets()

    def createWidgets(self):
        logging.debug("In SingleSlicePlane::createWidgets()")
        super(SingleSliceView, self).createWidgets()

        self.actionImagePlaneWidget = QtGui.QAction( self )
        icon1 = QtGui.QIcon()
        icon1.addPixmap( QtGui.QPixmap( ':/static/default/icon/48x48/office-chart-polar.png' ), QtGui.QIcon.Normal, QtGui.QIcon.Off )
        self.actionImagePlaneWidget.setIcon( icon1 )
        self.actionImagePlaneWidget.setObjectName( 'actionSlicePlaneWidgetPresets' )
        if self.title != "Transversal":
            self.toolbar.addAction( self.actionImagePlaneWidget )

    def createScene(self):
        logging.debug("In SliceViewPlane::createScene()")
        self.scene = VtkSliceImagePlane(QVtkWidget(self.plane), self, self._planeOrientation)

    def createActor(self, vtkImageData):

        logging.debug("In SingleSlicePlane::createActor()")
        super( SingleSliceView, self ).createActor( vtkImageData )

    def createActions(self):

        logging.debug("In SingleSlicePlane::createActions()")
        super(SingleSliceView, self).createActions()
        self.connect( self.actionImagePlaneWidget, QtCore.SIGNAL( 'triggered()' ), self.slotActionImagePlaneWidget )

    def slotActionImagePlaneWidget( self ):

        logging.debug("In SingleSlicePlane::slotActionImagePlaneWidget()")
        self.menu = QtGui.QMenu()
        flambda = lambda pl: not isinstance( pl, VolumeView ) \
                                 and not isinstance( pl, MultiSliceView ) \
                                 and not pl == self and pl.title != self.title \
                                 and pl.title != "Transversal" \
            and self.title.split()[0] not in pl.title.split()[0]
        for plane in filter( flambda, self._mscreenParent._planes ):
            action = QtGui.QWidgetAction(self)
            action.setCheckable(True)
            action.setText(plane.title)
            action.setData(plane)
            action.setChecked(plane in self._referencedPlanes)
            self.menu.addAction(action)

        self.connect( self.menu, QtCore.SIGNAL('triggered(QAction*)'), self.slotActionImagePlaneChoose )
        pos = QtGui.QCursor.pos()
        self.menu.exec_( pos )

    def addReferencedPlane( self, plane ):
        if  plane not in self._referencedPlanes:
            self._referencedPlanes.append( plane )

    def removeReferencedPlane( self, plane ):
        if  plane in self._referencedPlanes:
            self._referencedPlanes.remove( plane )

    def slotActionImagePlaneChoose( self, action ):

        logging.debug( 'In SingleSliceView::slotActionImagePlaneChoose()' )
        plane = action.data()
        if action.isChecked():
            plane.addSliderReleasedListeners( self.onReferedPlanesChange )
            plane.addCloseListener( self.onReferedPlaneClose )
            self.addReferencedPlane(plane)
            self.scene.addLinePlaneWidget( plane.lineWidget() )
        else:
            plane.removeSliderReleasedListeners( self.onReferedPlanesChange )
            plane.removeCloseListener( self.onReferedPlaneClose )
            self.removeReferencedPlane(plane)
            self.scene.removeLinePlaneWidget( plane.lineWidget() )

    def onReferedPlaneClose( self, plane ):

        self.scene.removeLinePlaneWidget( plane.lineWidget() )
        plane.scene.removeSliceChangeListener( self.onReferedPlanesChange )
        plane.removeCloseListener( self.onReferedPlaneClose )
        if plane in self._referencedPlanes:
            self._referencedPlanes.remove( plane )

    def onReferedPlanesChange( self, plane=None ):
        self.scene.window.Render()

    def planeWidget( self ):

        return self.scene._texturePlaneWidgetActor

    def lineWidget( self ):

        return self.scene._textureLineWidgetActor

    def slotActionThickness(self):

        logging.debug("In SingleSlicePlane::slotActionThickness()")
        super( SingleSliceView, self ).slotActionThickness()

    def slotActionSlabThickness(self):

        logging.debug("In SingleSlicePlane::slotActionThickness()")
        super( SingleSliceView, self ).slotActionSlabThickness()

    def slotChangeSlabThickness(self, value):

        logging.debug("In SingleSlicePlane::slotChangeThickness()")
        super( SingleSliceView, self ).slotChangeSlabThickness( value )

    def slotChangeSlabQuality(self, value):

        logging.debug("In SingleSlicePlane::slotChangeThickness()")
        super( SingleSliceView, self ).slotChangeSlabQuality( value )

    def certerSlidePosition(self):
        slicer = self.scene.getSlideSize()
        self._planeSlideValue = slicer/2
        self.planeSlide.setRange(0, slicer)
        self.planeSlide.setValue(slicer/2.0)

    def updateSliceAndPath(self, slice, slicePath):
        self.slice = slice
        self.slicePath = slicePath
        self.scene.updateSliceAndPath(self.slice, self.slicePath)
        self.slotChangeThickness(self.scene.sliceThickness)
        self.slotPlaneSlideChanged(self.planeSlide.value(), False)
        #        self.scene.updateCamera()

    def load(self, data):

        super(SingleSliceView, self).load(data)

        if data.has_key("sliceWidgets") and ( data.has_key("id") and data["id"] == self.scene._id ):

            lst = [ plane for plane in self._mscreenParent._planes if plane.scene._id in data["sliceWidgets"] ]
            for plane in lst:

                plane.addSliderReleasedListeners( self.onReferedPlanesChange )
                plane.addCloseListener( self.onReferedPlaneClose )
                self.addReferencedPlane(plane)
                self.scene.addLinePlaneWidget( plane.lineWidget() )

    def setSliceToPosition(self, point):
        mindist = sys.maxint
        mindistReal = sys.maxint
        pos = 0
        posReal = -1
        p1 = self.slicePath[0]
        for i, p2 in enumerate(self.slicePath[1:]):
            dist = vtk.vtkLine.DistanceToLine(point, p1, p2)

            d1 = vtk.vtkMath.Distance2BetweenPoints(p1, point)
            d2 = vtk.vtkMath.Distance2BetweenPoints([pp1+(pp2-pp1)/10000.0 for pp1, pp2 in zip(p1,p2)], point)
            d3 = vtk.vtkMath.Distance2BetweenPoints(p2, point)
            d4 = vtk.vtkMath.Distance2BetweenPoints([pp2+(pp1-pp2)/10000.0 for pp1, pp2 in zip(p1,p2)], point)

            if d2 <= d1 and d4 <= d3:
                if dist < mindistReal:
                    posReal = i
                    mindistReal = dist

            if d1 < mindist:
                pos = i
                mindist = d1

            p1 = p2

        if posReal >= 0:
            pos = posReal
            mindist = mindistReal

        hip2 = vtk.vtkMath.Distance2BetweenPoints(self.slicePath[pos], point)

        distFromClosestPoint = math.sqrt(hip2 - mindist)

        anterior = self.slicePath[0]
        sum = 0
        for point in self.slicePath[1:pos+1]:
            actual = point
            dist = math.sqrt(vtk.vtkMath.Distance2BetweenPoints(anterior, actual))
            sum = sum + dist
            anterior = point
        self.planeSlide.setValue((distFromClosestPoint + sum) / self.scene.sliceThickness)