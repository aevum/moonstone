#!/usr/bin/env python
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

def transformPosition( position ):

    """
    1  0 0
    0 -1 1
    0  0 1

    xl = (x * 1.0) + (y *  0.0) + 0.0
    yl = (x * 0.0) + (y * -1.0) + 1.0
    """

    return QtCore.QPointF( (position.x() * 1.0) + (position.y() *  0.0), (position.x() * 0.0) + (position.y() * -1.0) + 1.0 )

class ControlPoint( QtGui.QGraphicsEllipseItem ):

    default_size = 10

    def __init__( self, x, y, transferFunction=None, color=QtGui.QColor.fromRgbF(0.0, 0.0, 0.0, 1.0), size=default_size ):

        super( ControlPoint, self ).__init__( 0, 0, size, size )

        self.setParentItem( transferFunction )

        self.__size = size
        self.__color = color
        self.__position = transformPosition( QtCore.QPointF( x, y ) )

        self.__pen = QtGui.QPen( QtGui.QColor.fromRgbF( 0.0, 0.0, 0.0, 1.0 ) )
        self.__pen.setWidth( 2 )
        self.__pen.setColor( QtCore.Qt.gray )
        self.setPen( self.__pen )

        self.setBrush( self.__color )

        self.__leftNeighbor = None
        self.__rightNeighbor = None
        
        self.__updateGraphics()
        
        self.__updateToolTip()
        
    def setPosition( self, position ):
    
        self.__position = position
        
        if self.__position.x() <= 0.0: self.__position.setX( 0.0 )
            
        if self.__position.x() >= 1.0: self.__position.setX( 1.0 )
        
        if self.__position.y() <= 0.0: self.__position.setY( 0.0 )
            
        if self.__position.y() >= 1.0: self.__position.setY( 1.0 )

        if self.__leftNeighbor != None:

            if position.x() <= self.__leftNeighbor.getPosition().x() + (self.getSize() / self.scene().sceneRect().width()):

                self.__position.setX( self.__leftNeighbor.getPosition().x() + (self.getSize() / self.scene().sceneRect().width()) )

        if self.__rightNeighbor != None:

            if position.x() >= self.__rightNeighbor.getPosition().x() - (self.getSize() / self.scene().sceneRect().width()):

                self.__position.setX( self.__rightNeighbor.getPosition().x() - (self.getSize() / self.scene().sceneRect().width()) )
             
        self.__updateToolTip()
        
        self.__updateGraphics()

        self.notifyControlPointChange()

    def setLeftNeighbor( self, controlPoint ):

        self.__leftNeighbor = controlPoint

    def setRightNeighbor( self, controlPoint ):

        self.__rightNeighbor = controlPoint
        
    def getPosition( self ):
    
        return self.__position

    def getTransformedPosition( self ):

        return transformPosition( self.__position )
        
    def setSize( self, size ):
    
        self.__size = size
        
        self.__updateGraphics()
        
    def getSize( self ):
    
        return self.__size
        
    def setColor( self, color ):

        self.__color = color
        self.setBrush( self.__color )
        
        self.__updateGraphics()

        self.notifyControlPointColorChange()

    def getColor( self ):

        return self.__color
        
    def onChangeColor( self ):

        logging.debug( "ControlPoint::onChangeColor" )

        color = QtGui.QColorDialog.getColor( self.__color, None, "Choose control point color" )
        if color.isValid():
            self.setColor( color )
        
    def onRemoveControlPoint( self ):

        logging.debug( "ControlPoint::onRemoveControlPoint" )

        if self.parentItem() != None:
    
            self.parentItem().onRemoveControlPoint( self )
            
    def onControlPointMove( self, dx, dy ):

        logging.debug( "ControlPoint::onControlPointMove" )

        self.setPosition( self.getPosition() + QtCore.QPointF( dx / self.scene().width(), dy / self.scene().height() ) )

    def onSceneChange( self, event ):

        logging.debug( "ControlPoint::onSceneChange" )
        
        self.__updateGraphics()
        
    def notifyControlPointChange( self ):

        if self.parentItem() != None:

            self.parentItem().onControlPointChange( self )

    def notifyControlPointDragStart( self ):

        if self.parentItem() != None:

            self.parentItem().onControlPointDragStart( self )

    def notifyControlPointDrop( self ):

        if self.parentItem() != None:

            self.parentItem().onControlPointDrop( self )

    def notifyControlPointColorChange( self ):

        if self.parentItem() != None:

            self.parentItem().onControlPointColorChange( self )
            
    def __updateToolTip( self ):

        position = transformPosition( self.__position )
        self.setToolTip( "Value: {0}\nAlpha: {1}".format( position.x(), position.y() ) )
        
    def __updateGraphics( self ):
    
        if self.scene() != None:
        
            x = (self.getPosition().x() * self.scene().width()) - (self.__size / 2)
            y = (self.getPosition().y() * self.scene().height()) - (self.__size / 2)

            self.setRect( x, y, self.__size, self.__size )
            
        self.notifyControlPointChange()
        
    def mousePressEvent( self, event ):

        if event.button() == QtCore.Qt.MouseButton.LeftButton:

            self.__px = event.pos().x()
            self.__py = event.pos().y()

            self.__dragging = True

            self.notifyControlPointDragStart()

        elif event.button() == QtCore.Qt.MouseButton.RightButton:

            self.onChangeColor()
            
        elif event.button() == QtCore.Qt.MouseButton.MiddleButton:

            self.onRemoveControlPoint()

        event.accept()

    def mouseMoveEvent( self, event ):

        if self.__dragging:

            dx = event.pos().x() - self.__px
            dy = event.pos().y() - self.__py

            self.__px = event.pos().x()
            self.__py = event.pos().y()

            self.onControlPointMove( dx, dy )

    def mouseReleaseEvent( self, event ):

        if event.button() == QtCore.Qt.MouseButton.LeftButton:

            self.__dragging = False

            self.notifyControlPointDrop()

class TransferFunction( QtGui.QGraphicsPathItem ):

    def __init__( self, scene ):

        logging.debug( "TransferFunction::TransferFunction" )

        super( TransferFunction, self ).__init__()
        self.setOpacity( 0.8 )
        scene.addTransferFunction( self )

        pen = QtGui.QPen()
        pen.setColor( QtCore.Qt.gray )
        pen.setWidth( 3 )
        self.setPen( pen )

        self.__points = []

        self.__listeners = []

    @staticmethod
    def createFromPoints( scene, points ):

        tf = TransferFunction( scene )

        for point in points:

            x, y = point["x"], point["y"]
            color = QtGui.QColor.fromRgbF( point["r"], point["g"], point["b"])
            tf.addControlPoint( ControlPoint( x, y, tf, color ) )

        return tf
        
    def addControlPoint( self, controlPoint ):

        logging.debug( "TransferFunction::addControlPoint" )

        self.scene().sceneRectChanged.connect( controlPoint.onSceneChange )

        # insert anywhere as the list is empty
        if len(self.__points) == 0:

            self.__points.append( controlPoint )

        elif len(self.__points) == 1:

            #insert left or right depending on control point xposition
            if controlPoint.getPosition().x() < self.__points[0].getPosition().x():
                self.__points = [controlPoint] + self.__points
            else:
                self.__points = self.__points + [controlPoint]

        else:

            # insert as the leftmost point
            if controlPoint.getPosition().x() <= self.__points[0].getPosition().x():

                self.__points = [controlPoint] + self.__points[0:len(self.__points)]

            # insert as the rightmost point
            elif controlPoint.getPosition().x() >= self.__points[len(self.__points) - 1].getPosition().x():

                self.__points.append( controlPoint )

            else:

                # insert in between the two clicked points
                lindex = self.__getLeftPointIndex( controlPoint.getPosition() )
                rindex = self.__getRightPointIndex( controlPoint.getPosition() )

                # insert new control point between the lef and right point
                self.__points = self.__points[0:lindex + 1] + [controlPoint] + self.__points[rindex:len(self.__points)]

        self.__updateGraphics()
        self.__updateNeighbors()

        self.notifyControlPointInserted( controlPoint )
        
    def remControlPoint( self, controlPoint ):

        logging.debug( "TransferFunction::remControlPoint" )
        
        if len(self.__points) > 2 and controlPoint in self.__points:

            controlPoint.setParentItem( None )
            self.scene().sceneRectChanged.disconnect( controlPoint.onSceneChange )
            self.__points.remove( controlPoint )

            self.__updateGraphics()
            self.__updateNeighbors()

            self.notifyControlPointRemoved( controlPoint )
        
    def onControlPointChange( self, controlPoint ):

        logging.debug( "TransferFunction::onControlPointChange" )

        self.__updateGraphics()

        self.notifyControlPointChange( controlPoint )

    def onControlPointColorChange( self, controlPoint ):

        logging.debug( "TransferFunction::onControlPointColorChange" )

        self.__updateGraphics()

        self.notifyControlPointColorChange( controlPoint )
        
    def onSceneChange( self, sceneRect ):

        logging.debug( "TransferFunction::onSceneChange" )

        self.__updateGraphics()
        
    def onRemoveControlPoint( self, controlPoint ):

        logging.debug( "TransferFunction::onRemoveControlPoint" )
        
        self.remControlPoint( controlPoint )

    def onControlPointDragStart( self, controlPoint ):

        self.notifyControlPointDragStart( controlPoint )

    def onControlPointDrop( self, controlPoint ):

        self.notifyControlPointDrop( controlPoint )

    def clear( self ):

        """ Remove all function control points"""

        for point in [point for point in self.__points]:

            point.setParentItem( None )
            self.scene().sceneRectChanged.disconnect( point.onSceneChange )
            self.__points.remove( point )

            self.__updateGraphics()
            self.__updateNeighbors()

    def __sort( self ):

        """ Sort function points by x-position """

        lst = [point for point in self.__points]

        self.__points = sorted( lst, key=lambda obj: obj.getPosition().x() )

    def load( self, functionData ):

        self.clear()

        points = zip( functionData["opacity_points"], functionData["color_points"][0] )

        for point in points:

            x, y = point[0]["x"], point[0]["y"]
            color = QtGui.QColor.fromRgbF(point[1]["r"], point[1]["g"], point[1]["b"])

            self.addControlPoint( ControlPoint(x, y, self, color) )

    def getColorPoints( self ):

        pointList = []
        for point in self.__points:
            x = point.getTransformedPosition().x()
            r = point.getColor().redF()
            g = point.getColor().greenF()
            b = point.getColor().blueF()

            pointList.append( { u'x': x, u'r': r, u'g': g, u'b': b, u'midpoint': 0.5, u'sharpness': 0.0 } )

        result = pointList

        return result

    def getOpacityPoints( self ):

        pointList = []
        for point in self.__points:
            x = point.getTransformedPosition().x()
            y = point.getTransformedPosition().y()

            pointList.append( {u'x': x, u'y': y, u'midpoint': 0.5, u'sharpness': 0.0} )

        return pointList
        
    def __updateGraphics( self ):

        self.__sort()

        stops = []
        poly = QtGui.QPolygon()

        lst = [point for point in self.__points]

        if len(lst) >= 1:
            poly.append( QtCore.QPoint( lst[0].getPosition().x() * self.scene().sceneRect().width(), self.scene().sceneRect().height() ) )

        for cpoint in lst:

            poly.append( QtCore.QPoint( cpoint.getPosition().x() * self.scene().sceneRect().width(), cpoint.getPosition().y() * self.scene().sceneRect().height() ) )
            stops.append( (cpoint.getPosition().x(), cpoint.getColor()) )

        if len(lst) > 1:
            poly.append( QtCore.QPoint( cpoint.getPosition().x() * self.scene().sceneRect().width(), self.scene().sceneRect().height() ) )

        path = QtGui.QPainterPath()
        path.addPolygon( poly )
        self.setPath( path )
        
        gradient = QtGui.QLinearGradient( QtCore.QPointF(0, 0), QtCore.QPointF(self.scene().sceneRect().width(), 0) )
        gradient.setStops( stops )
        
        self.setBrush( QtGui.QBrush( gradient ) )

    def __updateNeighbors( self ):

        lst = [ point for point in self.__points ]

        if len(lst) == 1:

            lst[0].setLeftNeighbor( None )
            lst[0].setRightNeighbor( None )

        elif len(lst) == 2:

            lst[0].setLeftNeighbor( None )
            lst[0].setRightNeighbor( lst[1] )

            lst[1].setLeftNeighbor( lst[0] )
            lst[1].setRightNeighbor( None )

        elif len(lst) > 2:

            lst[0].setLeftNeighbor( None )
            lst[0].setRightNeighbor( lst[1] )

            for i in range( 1, len(lst) - 1 ):

                lst[i].setLeftNeighbor( lst[i-1] )
                lst[i].setRightNeighbor( lst[i+1] )

            lst[len(lst) - 1].setLeftNeighbor( lst[len(lst) - 2] )
            lst[len(lst) - 1].setRightNeighbor( None )

    def notifyControlPointInserted( self, point ):

        lst = [ listener for listener in self.__listeners ]

        for listener in lst:

            listener.onTransferFunctionPointInserted( point )

    def notifyControlPointRemoved( self, point ):

        lst = [ listener for listener in self.__listeners ]

        for listener in lst:

            listener.onTransferFunctionPointRemoved( point )

    def notifyControlPointChange( self, point ):

        lst = [ listener for listener in self.__listeners ]

        for listener in lst:

            listener.onTransferFunctionPointChanged( point )

    def notifyListeners( self ):

        lst = [listener for listener in self.__listeners]

        for listener in lst:

            listener.onTransferFunctionChange( self )

    def notifyControlPointDragStart( self, controlPoint ):

        lst = [listener for listener in self.__listeners]

        for listener in lst:

            listener.onTransferFunctionPointDragStart( controlPoint )

    def notifyControlPointDrop( self, controlPoint ):

        lst = [listener for listener in self.__listeners]

        for listener in lst:

            listener.onTransferFunctionPointDragStop( controlPoint )

    def notifyControlPointColorChange( self, controlPoint ):

        lst = [listener for listener in self.__listeners]

        for listener in lst:

            listener.onTransferFunctionPointColorChange( controlPoint )

    def addTransferFunctionChangeListener( self, listener ):

        if listener not in self.__listeners:

            self.__listeners.append( listener )

    def remTransferFunctionChangeListener( self, listener ):

        if listener in self.__listeners:

            self.__listeners.remove( listener )

    def mousePressEvent( self, event ):

        if event.button() == QtCore.Qt.MouseButton.RightButton:

            position = transformPosition( QtCore.QPointF( event.pos().x() / self.scene().width(), event.pos().y() / self.scene().height() ) )
            self.addControlPoint( ControlPoint( position.x(), position.y(), self ) )

        elif event.button() == QtCore.Qt.MouseButton.MiddleButton:

            self.clear()

            self.notifyTransferFucntionDeletion()

        elif event.button() == QtCore.Qt.MouseButton.LeftButton:

            self.scene().setFunctionToForeground( self )

    def notifyTransferFucntionDeletion( self ):

        lst = [ listener for listener in self.__listeners ]

        for listener in lst:

            listener.onTransferFunctionDeletion( self )

    def __getLeftPointIndex( self, position ):

        index = -1
        lst = [point for point in self.__points]
        for i, point in enumerate(lst):
            if point.getPosition().x() < position.x():
                index  = i
        return index

    def __getRightPointIndex( self, position ):

        index = -1
        lst = [point for point in self.__points]
        for i, point in enumerate(lst):
            if point.getPosition().x() > position.x():
                index = i
                break
        return index
        
class TransferFunctionScene( QtGui.QGraphicsScene ):

    def __init__( self, x, y, w, h ):

        super( TransferFunctionScene, self ).__init__( x, y, w, h )
        self.setBackgroundBrush( QtGui.QBrush(QtCore.Qt.black) )

        self.__functions = []

    def addTransferFunction( self, function ):

        if function not in self.__functions:

            self.__functions.append( function )
            self.sceneRectChanged.connect( function.onSceneChange )
            self.addItem( function )

    def remTransferFunction( self, function ):

        if function in self.__functions:

            self.__functions.remove( function )
            self.sceneRectChanged.disconnect( function.onSceneChange )
            self.removeItem( function )

    def getFunctions( self ):

        return self.__functions

    def stepForegroundFunction( self ):

        lst = [ function for function in self.__functions ]

        aux = lst[0].zValue()
        for i in range( 0, len(lst) - 1 ):

            lst[i].setZValue( lst[i+1].zValue() )

        lst[len(lst) - 1].setZValue( aux )

    def setFunctionToForeground( self, targetFunction ):

        lst = [ function for function in self.__functions ]

        map( lambda obj: obj.setZValue(0), lst )

        for item in lst:

            if item == targetFunction:

                item.setZValue( 1 )
        
class TransferFunctionView( QtGui.QGraphicsView ):

    def __init__( self ):

        super( TransferFunctionView, self ).__init__()

        self.setScene( TransferFunctionScene( 0, 0, self.size().width(), self.size().height() ) )
        self.setRenderHints( QtGui.QPainter.Antialiasing )

        self.__listeners = []

    def getOpacityPoints( self ):

        opacityPoints = []

        lst = [ function for function in self.scene().getFunctions() ]
        for function in lst:
            for point in function.getOpacityPoints():
                opacityPoints.append( point )

        return opacityPoints

    def getColorPoints( self ):

        colorPoints = []

        lst = [ function for function in self.scene().getFunctions() ]
        for function in lst:
            colorPoints.append( function.getColorPoints() )

        return colorPoints

    def addTransferFunction( self, function ):

        self.scene().addTransferFunction( function )
        function.addTransferFunctionChangeListener( self )

    def remTransferFunction( self, function ):

        self.scene().remTransferFunction( function )
        function.remTransferFunctionChangeListener( self )

    def resizeEvent( self, event ):

        self.scene().setSceneRect( 0, 0, event.size().width(), event.size().height() )

    def addTransferViewListener( self, listener ):

        if listener not in self.__listeners:

            self.__listeners.append( listener )

    def remTransferViewListener( self, listener ):

        if listener in self.__listeners:

            self.__listeners.remove( listener )

    def notifyFunctionPointInserted( self ):

        lst = [ listener for listener in self.__listeners ]

        for listener in lst:

            if hasattr( listener, "onTransferFunctionPointInserted"):

                listener.onTransferFunctionPointInserted()

    def notifyFunctionPointRemoved( self ):

        lst = [ listener for listener in self.__listeners ]

        for listener in lst:

            if hasattr( listener, "onTransferFunctionPointRemoved" ):

                listener.onTransferFunctionPointRemoved()

    def notifyFunctionPointChanged( self ):

        lst = [ listener for listener in self.__listeners ]

        for listener in lst:

            if hasattr( listener, "onTransferFunctionPointChanged" ):

                listener.onTransferFunctionPointChanged()

    def notifyFunctionPointDragStart( self ):

        lst = [ listener for listener in self.__listeners ]

        for listener in lst:

            if hasattr( listener, "onTransferFunctionPointDragStart"):

                listener.onTransferFunctionPointDragStart()

    def notifyFunctionPointDragStop( self ):

        lst = [ listener for listener in self.__listeners ]

        for listener in lst:

            if hasattr( listener, "onTransferFunctionPointDragStop"):

                listener.onTransferFunctionPointDragStop()

    def notifyFunctionPointColorChanged( self ):

        lst = [ listener for listener in self.__listeners ]

        for listener in lst:

            if hasattr( listener, "onTransferFunctionPointColorChange" ):

                listener.onTransferFunctionPointColorChange()

    def onTransferFunctionPointInserted( self, controlPoint ):

        self.notifyFunctionPointInserted()

    def onTransferFunctionPointRemoved( self, controlPoint ):

        self.notifyFunctionPointRemoved()

    def onTransferFunctionPointChanged( self, controlPoint ):

        self.notifyFunctionPointChanged()

    def onTransferFunctionPointDragStart( self, controlPoint ):

        self.notifyFunctionPointDragStart()

    def onTransferFunctionPointDragStop( self, controlPoint ):

        self.notifyFunctionPointDragStop()

    def onTransferFunctionPointColorChange( self, controlPoint ):

        self.notifyFunctionPointColorChanged()

    def onTransferFunctionDeletion( self, transferFunction ):

        self.remTransferFunction( transferFunction )

        self.notifyTransferFunctionDeletion()

    def notifyTransferFunctionCreation( self ):

        lst = [ listener for listener in self.__listeners ]

        for listener in lst:

            listener.onTransferFunctionCreated()

    def notifyTransferFunctionDeletion( self ):

        lst = [ listener for listener in self.__listeners]

        for listener in lst:

            listener.onTransferFunctionDeletion()

    def clear( self ):

        """ Remove all functions """

        lst = [ function for function in self.scene().getFunctions() ]
        for function in lst:
            function.clear()
            self.remTransferFunction( function )

    def loadHounsfieldScale( self, scale ):

        self.clear()

        colors = scale["color_points"]
        opacity = scale["opacity_points"]

        pos = 0
        functions = {}
        for i in range(0, len(colors)):
            # colors[i], opacity[pos : pos + len(colors[i])]
            functions[i] = []
            for j, k in zip( colors[i], opacity[pos : pos + len(colors[i])] ):
                #print dict( j.items() + k.items() )
                functions[i].append( dict( j.items() + k.items() ) )
            pos += len(colors[i])

        for i in range( 0, len(functions) ):
            #print functions[i]
            self.addTransferFunction( TransferFunction.createFromPoints( self.scene(), functions[i] ) )

    def mousePressEvent( self, event ):

        super( TransferFunctionView, self ).mousePressEvent( event )

        if event.button() == QtCore.Qt.MouseButton.RightButton:

            if not event.isAccepted():

                tf = TransferFunction( self.scene() )
                nposition = transformPosition( QtCore.QPointF( event.pos().x() / self.scene().sceneRect().width(), event.pos().y() / self.scene().sceneRect().height() ) )
                cp = ControlPoint( nposition.x(), nposition.y(), tf )
                tf.addControlPoint( cp )

                self.addTransferFunction( tf )

                self.notifyTransferFunctionCreation()

if __name__ == "__main__":

    class TFListener:

        def onTransferFunctionPointInserted( self ):

            print "TFListener::onTransferFunctionPointInserted"

        def onTransferFunctionPointRemoved( self ):

            print "TFListener::onTransferFunctionPointRemoved"

        def onTransferFunctionPointChanged( self ):

            #print "TFListener::onTransferFunctionPointChanged"
            pass

        def onTransferFunctionPointDragStart( self ):

            print "TFListener::onTransferFunctionPointStartDrag"

        def onTransferFunctionPointDragStop( self ):

            print "TFListener::onTransferFunctionPointStopDrag"

        def onTransferFunctionPointColorChange( self ):

            print "TFListener::onTransferFunctionPointColorChange"

        def onTransferFunctionCreated( self ):

            print "TFListener::onTransferFunctionCreated"

        def onTransferFunctionDeletion( self ):

            print "TFListener::onTransferFunctionDeletion"

    listener = TFListener()

    import sys
    app = QtGui.QApplication( sys.argv )

    win = QtGui.QWidget()

    layout =  QtGui.QVBoxLayout()
    
    tfw = TransferFunctionView()
    tfw.addTransferViewListener( listener )
    layout.addWidget( tfw )

    scale = {u'default_window': 4095.0, u'default_level': 1047.5, u'name': u'teste', u'mapper_properties': {u'blend_mode_to_maximum_intensity': True}, u'volume_properties': {u'shade': False}, u'color_points': [[{u'b': 0.0, u'g': 0.0, u'midpoint': 0.5, u'sharpness': 0.0, u'r': 0.0, u'x': 0.0}, {u'b': 1.0, u'g': 1.0, u'midpoint': 0.5, u'sharpness': 0.0, u'r': 1.0, u'x': 0.52}], [{u'b': 0.0, u'g': 0.0, u'midpoint': 0.5, u'sharpness': 0.0, u'r': 0.0, u'x': 1.0}]], u'opacity_points': [{u'y': 0.0, u'midpoint': 0.5, u'sharpness': 0.0, u'x': 0.0}, {u'y': 0.2, u'midpoint': 0.5, u'sharpness': 0.0, u'x': 0.2}, {u'y': 0.3, u'midpoint': 0.5, u'sharpness': 0.0, u'x': 0.3}]}
    tfw.loadHounsfieldScale( scale )

    tfw.loadHounsfieldScale( scale )

    tfw.loadHounsfieldScale( scale )

    win.setLayout( layout )
    win.show()

    sys.exit( app.exec_() )
