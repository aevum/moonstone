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
from viewplane2d import VolumeView2D

class AxialPlane(VolumeView2D):

    def __init__(self, mscreenParent, resliceTransform=None, parent=None):
        logging.debug("In AxialPlane::__init__()")
        super(AxialPlane, self).__init__(mscreenParent, VtkImagePlane.PLANE_ORIENTATION_AXIAL, resliceTransform, parent)
        self.updateWidgets()
    
    def updateWidgets(self):
        logging.debug("In AxialPlane::updateWidgets()")
        super(AxialPlane, self).updateWidgets()
        self.setWindowTitle("Axial")
                        
    def createActor(self, vtkImageData):
        logging.debug("In AxialPlane::__init__()")
        super(AxialPlane, self).createActor(vtkImageData)