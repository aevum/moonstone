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
import sys
import shutil
import os

def copy_libs(path, libList):
    for lib in libList:
        shutil.copy2(os.path.join(path, lib), 
                        os.path.join(os.getcwd(), 
                                     "resources",
                                     "packaging",
                                     "windows",
                                     "missing-libs"
                                     ))

def get_vtk_libs(path):
    libList = ["libvtkHybrid.dll", 
                "libvtkGenericFiltering.dll",
                "libvtkexoIIc.dll",
                "libvtkpng.dll"]
    copy_libs(path, libList)
    
def get_gdcm_libs(path):
    libList = ["libgdcmopenjpeg.dll"]
    copy_libs(path, libList)



if __name__ ==  "__main__":
    args = sys.argv
    if len(args) == 3:
        get_vtk_libs(args[1])
        get_gdcm_libs(args[2])
    else:
        print "Wrong usage:"
        print "python vtk_build_package.py [vktPath] [gdcmPath]"        
