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

from ...bloodstone.scenes.imageplane import VtkImagePlane
from ...bloodstone.scenes.multisliceimageplane import VtkMultiSliceImagePlane
from ...bloodstone.scenes.gui.qt.component.qvtkwidget import QVtkWidget
from volumeview import VolumeView
from PySide import QtGui, QtCore

from sliceview import SliceView

class MultiSliceView(SliceView):

    def __init__(self, mscreenParent, slices, parent=None, title = None, planeNumber = 1):
        logging.debug("In MultiSlicePlane::__init__()")
        self._referencedPlanes = []
        #if not title:
        #    title = QtGui.QApplication.translate("MultiSliceView", 
        #                                                 "Panoramic", 
        #                                                 None, 
        #                                                 QtGui.QApplication.UnicodeUTF8)
        super(MultiSliceView, self).__init__(mscreenParent, VtkImagePlane.PLANE_ORIENTATION_PANORAMIC, slices, parent, title, planeNumber=planeNumber)
        #self.updateWidgets()

    def activateAllPlanes(self):
        planes = [ pl for pl in self._mscreenParent._planes \
                   if not isinstance(pl, VolumeView) \
                          and not pl == self and pl.title.split()[0] != self.title.split()[0] \
                          and pl.title.split()[0] != "Coronal" \
                and pl.title.split()[0] != "Sagittal"]
        for plane in planes:
            if not plane in self._referencedPlanes:
                plane.addSliderReleasedListeners( self.onReferedPlanesChange )
                plane.addCloseListener( self.onReferedPlaneClose )
                self.addReferencedPlane(plane)
                self.scene.addLineWidgetFromScene( plane.scene )

    def desactivateAllPlanes(self):
        planes = [pl for pl in self._mscreenParent._planes \
                   if not isinstance(pl, VolumeView) \
                          and not pl == self and pl.title.split()[0] != self.title.split()[0] \
                          and pl.title.split()[0] != "Coronal" \
                and pl.title.split()[0] != "Sagittal"]
        for plane in planes:
            if plane in self._referencedPlanes:
                plane.removeSliderReleasedListeners( self.onReferedPlanesChange )
                plane.removeCloseListener( self.onReferedPlaneClose )
                self.removeReferencedPlane(plane)
                self.scene.remLineWidgetFromScene( plane.scene )

    def createScene(self):

        logging.debug("In SliceViewPlane::createScene()")
        self.scene = VtkMultiSliceImagePlane(QVtkWidget(self.plane), self)

    def createWidgets(self):

        logging.debug("In MultiSliceView::createWidgets()")

        super( MultiSliceView, self ).createWidgets()
        self.actionImagePlaneWidget = QtGui.QAction( self )
        icon1 = QtGui.QIcon()
        icon1.addPixmap( QtGui.QPixmap( ':/static/default/icon/48x48/office-chart-polar.png' ), QtGui.QIcon.Normal, QtGui.QIcon.Off )
        self.actionImagePlaneWidget.setIcon( icon1 )
        self.actionImagePlaneWidget.setObjectName( 'actionSlicePlaneWidgetPresets' )
        if self.title != "Transversal":
            self.toolbar.addAction( self.actionImagePlaneWidget )

    def createActions(self):

        logging.debug("In MultiSliceView::createActions()")

        super( MultiSliceView, self ).createActions()
        self.connect( self.actionImagePlaneWidget, QtCore.SIGNAL( 'triggered()' ), self.slotActionImagePlaneWidget )

    def slotActionImagePlaneWidget( self ):

        logging.debug("In MultiSliceView::slotActionImagePlaneWidget()")
        self.menu = QtGui.QMenu()
        fplanes = [ pl for pl in self._mscreenParent._planes\
                    if not isinstance(pl, VolumeView)\
                       and not pl == self and pl.title.split()[0] != self.title.split()[0]\
                       and pl.title.split()[0] != "Coronal"\
        and pl.title.split()[0] != "Sagittal" ]

        for plane in fplanes:
            action = QtGui.QWidgetAction( self )
            action.setCheckable( True )
            action.setText( plane.title )
            action.setData( plane )
            action.setChecked( plane in self._referencedPlanes )
            self.menu.addAction( action )

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

        logging.debug( 'In MultiSliceView::slot3DPresetChanged()' )
        plane = action.data()
        if action.isChecked():
            #plane.scene.addSliceChangeListener( self.onReferedPlanesChange )
            plane.addSliderReleasedListeners( self.onReferedPlanesChange )
            plane.addCloseListener( self.onReferedPlaneClose )
            self.addReferencedPlane(plane)

            self.scene.addLineWidgetFromScene( plane.scene )

        else:
            #plane.scene.removeSliceChangeListener( self.onReferedPlanesChange )
            plane.removeSliderReleasedListeners( self.onReferedPlanesChange )
            plane.addCloseListener( self.onReferedPlaneClose )
            self.removeReferencedPlane(plane)

            self.scene.remLineWidgetFromScene( plane.scene )

    def onReferedPlaneClose( self, plane ):

        plane.removeSliderReleasedListeners( self.onReferedPlanesChange )
        plane.removeCloseListener( self.onReferedPlaneClose )
        self.removeReferencedPlane(plane)

    def onReferedPlanesChange( self, plane=None ):
        self.scene.window.Render()
                            
    def planeWidget( self ):
        return self.scene._texturePlaneWidgetActor
     
    def slotSliderReleased(self):
        self.scene.updatePlaneCutter()
        
    def updateSlices(self, slices):
        self.scene.updateSlices(slices)
        self.slotChangeThickness(self.scene.sliceThickness)

    def load(self, data):

        super( MultiSliceView, self ).load(data)

        if data.has_key("sliceWidgets") and ( data.has_key("id") and data["id"] == self.scene._id ):

            lst = [ plane for plane in self._mscreenParent._planes if plane.scene._id in data["sliceWidgets"] ]
            for plane in lst:

                plane.addSliderReleasedListeners( self.onReferedPlanesChange )
                plane.addCloseListener( self.onReferedPlaneClose )
                self.addReferencedPlane(plane)

                self.scene.addLineWidgetFromScene( plane.scene )
        self.scene.renderer.ResetCameraClippingRange()