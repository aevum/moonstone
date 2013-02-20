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
import os

import vtk
import vtkgdcm
from PySide import QtCore, QtGui

from ....utils import constant
from ....bloodstone.scenes.gui.qt.component.qvtkwidget import QVtkWidget


class VTKImageView(QVtkWidget):

    def __init__(self, parent=None):
        logging.debug("In VTKImageView::__init__()")
        super(VTKImageView, self).__init__(parent)
        self.setWindowTitle(constant.TITLE_PROGRAM)

        self.actor = vtk.vtkImageActor()
        self.textActors = []

        self.render = vtk.vtkRenderer()
        self.render.AddActor(self.actor)

        self.interactorStyle = vtk.vtkInteractorStyleImage()
        self.SetInteractorStyle(self.interactorStyle)

        self.window = self.GetRenderWindow()
        self.window.AddRenderer(self.render)



    def getInteractorStyle(self):
        return self.interactorStyle


    def setScaleOn(self):
        try:
            self.render.removeActor(self.vtkLegendScaleActor)
        except:
            pass
        self.vtkLegendScaleActor = vtk.vtkLegendScaleActor()
        self.render.AddActor(self.vtkLegendScaleActor)



    def addText(self, text, x=0.03, y=0.97, size=12, orientation="left"):
        property = vtk.vtkTextProperty()
        property.SetFontSize(size)
        property.SetFontFamilyToArial()
        property.BoldOff()
        property.ItalicOff()
        #property.ShadowOn()
        if orientation == "left":
            property.SetJustificationToLeft()
        elif orientation == "right":
            property.SetJustificationToRight()
        elif orientation == "center":
            property.SetJustificationToCenter()

        property.SetVerticalJustificationToTop()
        property.SetColor(1,1,1)

        mapper = vtk.vtkTextMapper()
        mapper.SetTextProperty(property)
        mapper.SetInput(str(text))

        textActor = vtk.vtkActor2D()
        self.textActors.append(textActor)
        textActor.SetMapper(mapper)
        textActor.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
        textActor.GetPositionCoordinate().SetValue(x,y)
        textActor.VisibilityOn()

        self.render.AddActor(textActor)
        self.Render()


    def removeText(self, id):
        try:
            self.render.RemoveActor(self.textActors[id])
            self.textActors.remove(self.textActors[id])
            return True
        except:
            return False

    def removeAllTexts(self):
        for id in range(0,len(self.textActors)):
            toRemove = len(self.textActors)-1
            self.render.RemoveActor(self.textActors[toRemove])
            self.textActors.remove(self.textActors[toRemove])


    def setImage(self, dicomfile):
        logging.debug("In VTKImageView::setImage()")
        if dicomfile:
            if os.path.exists(dicomfile):
                self.reader = vtkgdcm.vtkGDCMImageReader()
                self.reader.SetFileName(dicomfile)
                self.reader.Update()
                
                vtkImageData = self.reader.GetOutput()
                vtkImageData.UpdateInformation()
                srange = vtkImageData.GetScalarRange()
                
                cast = vtk.vtkImageCast()
                cast.SetInput(vtkImageData)
                cast.SetOutputScalarType(4)
                cast.Update()
                cast.GetOutput().SetUpdateExtentToWholeExtent()
                
                table = vtk.vtkLookupTable()
                table.SetNumberOfColors(256)
                table.SetHueRange(0.0, 0.0)
                table.SetSaturationRange(0.0, 0.0)
                table.SetValueRange(0.0, 1.0)
                table.SetAlphaRange(1.0, 1.0)
                table.SetRange(srange)
                table.SetRampToLinear()
                table.Build()
                
                color = vtk.vtkImageMapToColors()
                color.SetLookupTable(table)
                color.SetInputConnection(cast.GetOutputPort())
                color.Update()
        
                self.cast = vtk.vtkImageMapToWindowLevelColors()
                self.cast.SetOutputFormatToLuminance()
                self.cast.SetInputConnection(color.GetOutputPort())
                self.cast.SetWindow(255.0)
                self.cast.SetLevel(127.0) 
                self.cast.Update()
                self.cast.UpdateWholeExtent()
        
                self.render.RemoveActor(self.actor)
                self.actor = vtk.vtkImageActor()
                self.actor.SetInput(self.cast.GetOutput())
                self.render.AddActor(self.actor)
                self.render.ResetCamera()
                self.Render()
            else:
                self.render.RemoveActor(self.actor) 
                self.Render()
        else:
            self.render.RemoveActor(self.actor) 
            self.Render()

    def removeActor(self):
        logging.debug("In VTKImageView::removeActor()")
        self.render.RemoveActor(self.actor)
        self.actor = vtk.vtkImageActor()
        self.render.AddActor(self.actor)
        self.render.ResetCamera()
        self.Render()

