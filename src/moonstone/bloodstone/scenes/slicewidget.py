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

import vtk

class SlicePlaneWidget( vtk.vtkActor ):

    def __init__( self, owner, referent, color=(1, 0, 0) ):

        self._owner = owner
        self._referent = referent
        self._color = color
    
        self._source = vtk.vtkLineSource()
        self._source.SetPoint1( self._referent._planeSource.GetPoint1()[0], 0, 0 )
        self._source.SetPoint2( self._referent._planeSource.GetPoint2()[0], 0, 0 )
        
        self._mapper = vtk.vtkPolyDataMapper()
        self._mapper.SetInput( self._source.GetOutput() )
        
        self.SetMapper( self._mapper )
        self.GetProperty().SetColor( self._color )

    def onSliceChange( self, owner ):

        # t = (sl - si) / (sf - si)
        bounds = self._owner.getBounds()

        tz = ( self._owner._planeSource.GetPoint1()[2] - bounds[4]) / ( bounds[5] - bounds[4] )
        ypos = self._referent._planeSource.GetPoint1()[1] + tz * (self._referent._planeSource.GetPoint2()[1] - self._referent._planeSource.GetPoint1()[1])

        self._source.SetPoint1( self._referent._planeSource.GetPoint1()[0], ypos, 0 )
        self._source.SetPoint2( self._referent._planeSource.GetPoint2()[0], ypos, 0 )

class TransversalSlicePlaneWidget( vtk.vtkActor ):

    def __init__( self, owner, referent, color=(1, 0, 0) ):

        self._owner = owner
        self._referent = referent
        self._color = color

        self._source = vtk.vtkLineSource()
        self._source.SetPoint1( 0, self._referent._planeSource.GetPoint1()[1], 0 )
        self._source.SetPoint2( 0, self._referent._planeSource.GetPoint1()[1], 0 )

        self._mapper = vtk.vtkPolyDataMapper()
        self._mapper.SetInput( self._source.GetOutput() )

        self.SetMapper( self._mapper )
        self.GetProperty().SetColor( self._color )

        self.onSliceChange( None )

    def onSliceChange( self, owner ):

        t = float(self._owner.sliceCurrentPosition) / (self._owner.slicePositionMax - self._owner.slicePositionMin)
        tx = t * (self._referent._planeSource.GetPoint1()[0] - self._referent._planeSource.GetOrigin()[0])
        xpos = self._referent._planeSource.GetOrigin()[0] + tx

        self._source.SetPoint1( xpos, self._referent._planeSource.GetPoint1()[1], 0 )
        self._source.SetPoint2( xpos, self._referent._planeSource.GetPoint2()[1], 0 )