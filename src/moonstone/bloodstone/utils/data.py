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
import yaml

def dicom_to_png(imagedata, dir):
    logging.debug("In data.dicom_to_png()")
    shiftScale = vtk.vtkImageShiftScale()
    shiftScale.SetOutputScalarTypeToUnsignedShort()
    shiftScale.SetInput(imagedata)
    inp = shiftScale.GetInput()
    minv,maxv = inp.GetScalarRange()
    shiftScale.SetShift(-minv)
    shiftScale.SetScale(65535 / (maxv - minv))
    w = vtk.vtkPNGWriter()
    w.SetFileDimensionality(3)
    w.SetInput(shiftScale.GetOutput())
    w.SetFilePattern("%s%d.png")
    if not os.path.exists(dir):
        os.mkdir(dir)
    w.SetFilePrefix(dir)
    w.Write()

def dicom_to_vti(imagedata, filename):
    logging.debug("In data.dicom_to_vti()")
    extent = imagedata.GetWholeExtent()
    spacing = imagedata.GetSpacing()
    origin = imagedata.GetOrigin()

    center = (
        origin[0] + spacing[0] * 0.5 * (extent[0] + extent[1]),
        origin[1] + spacing[1] * 0.5 * (extent[2] + extent[3]),
        origin[2] + spacing[2] * 0.5 * (extent[4] + extent[5])
    )
    
    resliceAxes = vtk.vtkMatrix4x4()
    vtkMatrix = (
        1, 0, 0, 0,
        0, -1, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1
    )
    resliceAxes.DeepCopy(vtkMatrix)
    resliceAxes.SetElement(0, 3, center[0])
    resliceAxes.SetElement(1, 3, center[1])
    resliceAxes.SetElement(2, 3, center[2])
    
    reslice = vtk.vtkImageReslice()
    reslice.SetInput(imagedata)
    reslice.SetInformationInput(imagedata)
    reslice.SetResliceAxes(resliceAxes)
    reslice.SetOutputDimensionality(3)
    reslice.Update()
    
    imagedata = reslice.GetOutput()
    writer = vtk.vtkXMLImageDataWriter()
    writer.SetInput(imagedata)
    writer.SetFileName(filename)
    writer.Write()
    
def dicom_to_vti2(imagedata, filename):
    logging.debug("In data.dicom_to_vti()")
    writer = vtk.vtkXMLImageDataWriter()
    writer.SetInput(imagedata)
    writer.SetFileName(filename)
    writer.Write()

def reader_vti(filename):
    logging.debug("In data.reader_vti()")
    append = vtk.vtkImageAppend()
    append.ReleaseDataFlagOn()
    append.SetAppendAxis(2)
    reader = vtk.vtkXMLImageDataReader()
    reader.ReleaseDataFlagOn()
    if os.path.exists(filename):
        reader.SetFileName(filename)
        #reader.GetOutput().Register(reader)
        reader.Update()
        return vtk.vtkImageData.SafeDownCast(reader.GetOutput())
    else:
        i = 0
        paths = []
        while True:
            partName = filename.replace(".vti", "{0}.vti".format(i)) 
#            print partName
            if os.path.exists(partName):
                paths.append(partName)
            else:
                break
            i = i+1
        #paths.reverse()
        for i, partName in enumerate(paths):
            reader = vtk.vtkXMLImageDataReader()
            reader.ReleaseDataFlagOn()
            reader.SetFileName(partName)
            #reader.GetOutput().Register(reader)
            reader.Update()
            append.SetInput(i, reader.GetOutput() )
    append.Update()
    output = append.GetOutput()
    for i in range(append.GetNumberOfInputs()):
        append.GetInput(i).ReleaseData()
    return output


def reader_to_imagedata(reader):
    logging.debug("In data.reader_to_imagedata()")
    return vtk.vtkImageData.SafeDownCast(reader.GetOutput())

def magnify_multiply_imagedata(reader, zSpacing=1.0):
    logging.debug("In data.magnify_multiply_imagedata()")
    imagedata = reader.GetOutput()
    imagedata.UpdateInformation()
    spacing = imagedata.GetSpacing()
    #dimensions = imagedata.GetDimensions()
    #if dimensions[0] > 256 and dimensions[1] > 256:
    #    spacing = [x/0.5 for x in spacing]
    
    change = vtk.vtkImageChangeInformation()
    change.SetInput(imagedata)
    change.SetOutputOrigin(imagedata.GetOrigin())
    change.SetOutputSpacing(spacing[0], spacing[1], zSpacing)
    change.Update()
    
    return vtk.vtkImageData.SafeDownCast(change.GetOutput())

def insert_vti_in_yaml_file(outputFile, vtiPath, name, matrix = None):
    if not matrix:
        matrix = [[1, 0, 0, 0],
                  [0, 1, 0, 0],
                  [0, 0, 1, 0],
                  [0, 0, 0, 1]]
    save = {"vti": vtiPath, "name": name, "matrix": matrix}
    if os.path.exists(outputFile):
        f = file(outputFile, "r")
        all_vtis = yaml.load(f)
        for vti in all_vtis:
            if vti["vti"] == vtiPath:
                all_vtis.remove(vti)
        f.close()
    else:
        all_vtis = []
    
    all_vtis.append(save)
    
    f = file(outputFile, "w")
    yaml.dump(all_vtis, f)   
    f.close()
    
def cleanYamlFile(outputFile):
    persist_yaml_file(outputFile, [])
    
def add_plugin_in_yaml_file(all_plugins, pluginId, sceneId, params):
    savedPlugin = None
    for plugin in all_plugins:
        if plugin["id"] == pluginId:
            savedPlugin = plugin
            break
    if not savedPlugin:
        savedPlugin = {"id" : pluginId, "sceneId" : [], "params": params}
        all_plugins.append(savedPlugin)
    if sceneId not in savedPlugin["sceneId"] :
        savedPlugin["sceneId"].append(sceneId)

def persist_yaml_file(outputFile, yamlFile):
    f = file(outputFile, "w")
    yaml.dump(yamlFile, f)   
    f.close() 
    
def remove_file(file):
    if os.path.exists(file):
        os.remove(file)

def load_yaml_file(path):
    all_vtis = None
    if os.path.exists(path):
        f = file(path, "r")
        all_vtis = yaml.load(f)
        f.close()
    return all_vtis

def load_vtis_from_yaml_file(path):
    return load_yaml_file(path)

def get_imagedata_hash(imagedata):
    origin = imagedata.GetOrigin()
    extent = imagedata.GetWholeExtent()
    spacing = imagedata.GetSpacing()
    return hash("{0}-{1}-{2}".format(origin, spacing, extent))

def magnify_single_imagedata(reader, zSpacing=1.0):
    logging.debug("In data.magnify_imagedata()")
    imagedata = reader.GetOutput()
    imagedata.UpdateInformation()
    
    spacing = imagedata.GetSpacing()
    
    xAxis = [1.0, 0.0, 0.0]
    yAxis = [0.0, 1.0, 0.0]
    zAxis = [0.0, 0.0, 1.0]
    
    logging.debug(":: Spacing [{0}, {1}, {2}]".format(spacing[0], 
                                                      spacing[1], spacing[2]))
    logging.debug(":: ZSpacing Computer: {0}".format(zSpacing))
    
    magnify = vtk.vtkImageReslice()
    magnify.SetInputConnection(reader.GetOutputPort())
    magnify.SetInformationInput(reader.GetOutput())
    magnify.SetOutputSpacing(spacing[0], spacing[1], zSpacing)
    magnify.SetInterpolationModeToCubic()
    magnify.SetOutputDimensionality(3)
    magnify.SetResliceAxesDirectionCosines(xAxis, yAxis, zAxis)
    magnify.SetResliceAxesOrigin(imagedata.GetOrigin())
    
    return vtk.vtkImageData.SafeDownCast(magnify.GetOutput())
