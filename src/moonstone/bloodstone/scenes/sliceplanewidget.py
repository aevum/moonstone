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

    def __init__( self, color, plane, reslice, range ):
        
        self._color = color
    
        self._source = plane
                
        self._mapper = vtk.vtkPolyDataMapper()
        self._mapper.SetInput( self._source.GetOutput() )
        self.SetMapper( self._mapper )

        self._lut = vtk.vtkWindowLevelLookupTable()
        self._lut.SetNumberOfColors( 256 )
        self._lut.SetTableRange( range[0], range[1] )
        self._lut.SetHueRange( 0.0, 0.0 )
        self._lut.SetSaturationRange( 0.0, 0.0 )
        self._lut.SetValueRange( 0.0, 1.0 )
        self._lut.SetAlphaRange( 0.0, 1.0 )
        self._lut.Build()

        self._colormap = vtk.vtkImageMapToColors()
        self._colormap.SetInputConnection( reslice.GetOutputPort() )
        self._colormap.SetLookupTable( self._lut )
        self._colormap.SetOutputFormatToRGBA()
        self._colormap.PassAlphaToOutputOn()

        self._texture = vtk.vtkTexture()
        self._texture.SetInterpolate( True )
        self._texture.SetQualityTo32Bit()
        self._texture.MapColorScalarsThroughLookupTableOff()
        self._texture.RepeatOff()
        self._texture.SetInput( self._colormap.GetOutput() )
        self._texture.SetLookupTable( self._lut )
        self.SetTexture( self._texture )

        self._property = vtk.vtkProperty()
        self._property.SetOpacity( 0.9 )
        self._property.EdgeVisibilityOn()
        self._property.SetEdgeColor( self._color[0], self._color[1], self._color[2] )
        self.SetProperty( self._property )

    def plane( self, plane ):
    
        self._source = plane
        
        self._mapper.SetInput( self._source.GetOutput() )
                        
    def position( self, x, y, z ):
        
        self._source.SetCenter( x, y, z )
        
    def normal( self, x, y, z ):
        
        self._source.SetNormal( x, y, z )
