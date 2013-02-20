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

from . import constant
from .strUtils import hashStr, normalizePath
from ..bloodstone.utils.data import load_vtis_from_yaml_file, persist_yaml_file, reader_vti
from ..bloodstone.importer.database.serie import Serie
import os
import shutil
import vtk

VERSION = "0.3"

def convertPatient(patient):
    idHash = hashStr(patient.uid)
    oldPatientDic = patient.directory
    basePath = os.path.join(constant.INSTALL_DIR, "data/")
    newPatientDic = os.path.join(basePath, idHash)
    if newPatientDic != oldPatientDic:
        #renaming folder of patient
        if os.path.exists(oldPatientDic):
            os.rename(oldPatientDic, newPatientDic)
        #saving in db
        patient.directory = newPatientDic
        
def convertSerieTo021(serie):
    patient = serie.study.patient
    convertPatient(patient)
    basePath = patient.directory
    oldYamlFile = serie.file
    newYamlFile = os.path.join("{0}{1}".format(hashStr(serie.uid), hashStr(serie.description)), "{0}.yaml".format(hashStr(serie.uid))) 
    print "oldYamlFile:", oldYamlFile, " newYamlFile:", newYamlFile 
    if  newYamlFile != oldYamlFile:
        oldFilePath = serie.file.replace("\\", "/")
        oldSeriePath = oldFilePath.split("/")
        oldSerieAbsoluteFolder = os.path.join(basePath, oldSeriePath[0])
        
        oldYamlPath = os.path.join(basePath, oldYamlFile)
        print "---------", oldSeriePath
        seriesYaml = load_vtis_from_yaml_file(oldYamlPath)
        if seriesYaml:
            for serieYaml in seriesYaml:
                vtiPath = serieYaml["vti"].replace("\\", " ")
                vtiSDir = vtiPath.split("/")
                print "setting vti path from:", vtiPath, " to:", os.path.join(hashStr(serie.uid), os.path.join(vtiSDir[1], vtiSDir[2]))
                serieYaml["vti"] = os.path.join("{0}{1}".format(hashStr(serie.uid), hashStr(serie.description)), os.path.join(vtiSDir[1], vtiSDir[2]))
            #change vti path of all series in yaml file
            persist_yaml_file(oldYamlPath, seriesYaml)
            
        newYamlPath = os.path.join(oldSerieAbsoluteFolder, "{0}{1}".format(hashStr(serie.uid), ".yaml"))
        #renaming yaml file
        print "renaming yaml file from:", oldYamlPath, " to ", newYamlPath
        if os.path.exists(oldYamlPath) :
            os.rename(oldYamlPath, newYamlPath)
        else:
            print "yaml file already moved or not exist"
        
        parts = oldSeriePath[1].rsplit(".", 1)
        oldStudyYamlPath = os.path.join(oldSerieAbsoluteFolder, "{0}.plugin.yaml".format(parts[0]))
        newStudyYamlPath = os.path.join(oldSerieAbsoluteFolder, "{0}{1}".format(hashStr(serie.uid), ".plugin.yaml"))
        #renaming plugin yaml file
        print "renaming plugin yaml file from:", oldStudyYamlPath, " to ", newStudyYamlPath
        if os.path.exists(oldStudyYamlPath):
            os.rename(oldStudyYamlPath, newStudyYamlPath)
        else:
            print "plugin yaml file already moved or not exist"
        
        newSerieAbsoluteFolder = os.path.join(basePath, "{0}{1}".format(hashStr(serie.uid), hashStr(serie.description)))
        #Renaming serie folder
        print "renaming serie folder from ", oldSerieAbsoluteFolder, " to ", newSerieAbsoluteFolder 
        if os.path.exists(oldSerieAbsoluteFolder):
            os.rename(oldSerieAbsoluteFolder, newSerieAbsoluteFolder)
        else :
            print "serie folder already moved or not exist"
            
        oldImagePath = os.path.join(basePath, normalizePath(serie.uid))
        newImagePath = os.path.join(basePath, hashStr(serie.uid))
        #Renaming serie image folder
        print "renaming serie image folder from ", oldImagePath, " to ", newImagePath 
        if os.path.exists(oldImagePath):
            os.rename(oldImagePath, newImagePath)
        else :
            print "serie image folder already moved or not exist"    

        serie.file = newYamlFile
                
    
    #1.2.840.113619.2.176.3596.oldYamlPath.7099.1261648507.302Sag  T2/1.2.840.113619.2.176.3596.6689168.7099.1261648507.302.yaml

def convertSerieTo03(serie):
    yamlFile = serie.file
    patient = serie.study.patient
    basePath = patient.directory
    yamlPath = os.path.join(basePath, yamlFile)
    yaml = load_vtis_from_yaml_file(yamlPath)
    if type(yaml) != list:
        return
    newYaml = {}
    mainScreen = yaml[0]
    for screen in yaml:
        if screen.has_key("main"):
            mainScreen = screen
            break
    newYaml["vti"] = mainScreen["vti"]
    mScreens = []
    newYaml["mScreens"] = mScreens
    for screen in yaml:
        newScreen = {}
        if screen.has_key("lastChildId"):
            newScreen["lastChildId"] = screen["lastChildId"]
        if screen.has_key("name"):
            newScreen["name"] = screen["name"]
        if screen.has_key("main"):
            newScreen["main"] = screen["main"]
        if screen.has_key("scenes"):
            newScreen["scenes"] = screen["scenes"]
        resliceMatrix = None
        if screen.has_key("resliceMatrix"):
            resliceMatrix = screen["resliceMatrix"]
        vtiPath = os.path.abspath(os.path.join(basePath, screen["vti"].replace("/", os.path.sep)))
        if len(yaml) > 1 and not (screen.has_key("main") and screen["main"]):
            corners = getCubeCornersFromImageData(vtiPath, resliceMatrix)
            newScreen["cubeCorners"] = corners
        else:
            if screen.has_key("matrix"):
                matrix = screen["matrix"]
                corners = getCubeCornersFromImageData(vtiPath, matrix)
                newScreen["cubeCorners"] = corners
            
        mScreens.append(newScreen)
    persist_yaml_file(yamlPath, newYaml)
    if len(yaml) > 1:
        for screen in yaml:
            if not (screen.has_key("main") and screen["main"]):
                vtiPath = os.path.join(basePath, screen["vti"])
                vtiDir = os.path.dirname(vtiPath)
                shutil.rmtree(vtiDir)
                
                
def createTransform(matrix):
    transform = None
    if matrix:
        vtkMatrix = vtk.vtkMatrix4x4()
        for i in range(4):
            for j in range(4):
                vtkMatrix.SetElement(i, j, matrix[i][j])
        transform = vtk.vtkTransform()
        transform.SetMatrix(vtkMatrix)
    return transform            
                
def getCubeCornersFromImageData(vtiPath, resliceMatrix):
    imageData = reader_vti(vtiPath)
    bounds = getImageDataBounds(imageData)
    imageData.ReleaseData()
    corners = []
    corners.append([bounds[0],bounds[2],bounds[4]])
    corners.append([bounds[0],bounds[2],bounds[5]])
    corners.append([bounds[0],bounds[3],bounds[4]])
    corners.append([bounds[0],bounds[3],bounds[5]])
    corners.append([bounds[1],bounds[2],bounds[4]])
    corners.append([bounds[1],bounds[2],bounds[5]])
    corners.append([bounds[1],bounds[3],bounds[4]])
    corners.append([bounds[1],bounds[3],bounds[5]])
    
    transform = createTransform(resliceMatrix)
    if transform:
        for i in range(len(corners)):
            corners[i] = list(transform.TransformPoint(corners[i]))
    return corners

def getImageDataBounds(imageData):
    spacing = imageData.GetSpacing()
    origin = imageData.GetOrigin()
    extent = imageData.GetWholeExtent()
    bounds = [origin[0] + spacing[0]*extent[0], # xmin
              origin[0] + spacing[0]*extent[1], # xmax
              origin[1] + spacing[1]*extent[2], # ymin
              origin[1] + spacing[1]*extent[3], # ymax
              origin[2] + spacing[2]*extent[4], # zmin
              origin[2] + spacing[2]*extent[5]] # zmax
    return bounds

def convertToActualVersion():
    filePath = os.path.join(constant.USER_CONFIG_DIR, "version.yaml")
    yFile = load_vtis_from_yaml_file(filePath)
    if yFile:
        installVersion = yFile["version"]
    else:
        installVersion = "0.2.0"
    if installVersion < "0.2.1":
        series = Serie.findContaining()
        if series:
            for serie in series:
                print "------------------------------------------------------------------------\nconverting ", serie , " to 0.2.1\n"
                convertSerieTo021(serie)
        yFile = {}
        yFile["version"] = "0.2.1"
        persist_yaml_file(os.path.join(constant.USER_CONFIG_DIR, "version.yaml"), yFile)
        
    if installVersion < "0.3":
        series = Serie.findContaining()
        if series:
            for serie in series:
                print "------------------------------------------------------------------------\nconverting ", serie , " to 0.3\n"
                convertSerieTo03(serie)
        yFile = {}
        yFile["version"] = VERSION
        persist_yaml_file(os.path.join(constant.USER_CONFIG_DIR, "version.yaml"), yFile)
    return


