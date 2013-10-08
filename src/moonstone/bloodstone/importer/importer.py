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
import os
import logging
import yaml
import time
import shutil
from multiprocessing import Process, Value, Pipe, Lock, Queue
import traceback
import sys

import vtk
import gdcm
import vtkgdcm
from PySide import QtGui
try:
    from moonstone.bloodstone.importer.database import dbutils
    from moonstone.bloodstone.importer.database.patient import Patient
    from moonstone.bloodstone.importer.database.serie import Serie
    from moonstone.bloodstone.importer.database.study import Study
    from moonstone.utils.strUtils import hashStr
    from moonstone.utils import constant
except:
    from database import dbutils
    from database.patient import Patient
    from database.serie import Serie
    from database.study import Study
    from utils.strUtils import hashStr
    from utils import constant
from importitemdelegate import ImportItemDelegate

dbutils.DBUtils().createConnection()

class Importer(object):

    def __init__(self):
        logging.debug("In Importer::__init__()")
        self._directories = []
        self.series = {}
        self.changed = 0
        self.queue = Queue()
        self.stopCancelQueue = Queue()
        self._parentConn = None
        self.finished = 0
    
    def clearData(self):
        logging.debug("In Importer::clearData()")
    
    def loadDirectory(self, directory, recursive):
        logging.debug("In Importer::loadDirectory()")
        self.finished = 0
        prov = []        
        while not self.stopCancelQueue.empty():
            self.stopCancelQueue.get()
        self.process = Process( target=scanDirectory, 
                               args = (directory, recursive, 
                                       self.series,  
                                       self.queue, self.stopCancelQueue))
        self.process.start()
        if not directory in self._directories:
            prov.append(directory)
        self._directories = self._directories+prov
    
    def stop(self):
        self.stopCancelQueue.put("stop")
    
    def cancel(self):
        self.stopCancelQueue.put("cancel")
    
    def updateSeries(self):
        logging.debug("In Importer::updateSeries()")
        if not self.queue.empty():
            key, value = self.queue.get()
            if key == "finished-1":
                self.finished = 1
            elif key == "finished-2":
                self.finished = 2
            else:
                self.series.update(value)
    
    def makeImport(self, indexes):
        logging.debug("In Importer::makeImport()")
        self.finished = 0
        while not self.queue.empty():
            self.queue.get()
        while not self.stopCancelQueue.empty():
            self.stopCancelQueue.get()
        self.process = Process(target=processImport, 
                               args = (indexes, 
                                       self.series,  
                                       self.queue, self.stopCancelQueue))
        self.process.start()
                
    
def processImport(indexes, series, queue, stopCancelQueue):
    for index in indexes:
        try:
            serie = series[index]
            serie["progress"] = 5
            queue.put(["series", series])

            if not stopCancelQueue.empty():
                break
            sortSerie(serie)

            serie["progress"] = 25
            queue.put(["series", series])

            if not stopCancelQueue.empty():
                break
            copyFiles(serie)

            serie["progress"] = 50
            queue.put(["series", series])
            if not stopCancelQueue.empty():
                break
            createVTI(serie)

            serie["progress"] = 90
            queue.put(["series", series])
            if not stopCancelQueue.empty():
                break
            createYAMLFile(serie)
            serie["progress"] = 95
            queue.put(["series", series])
            if not stopCancelQueue.empty():
                break
            updateDatabase(serie)
            serie["progress"] = 100
            queue.put(["series", series])
            if not stopCancelQueue.empty():
                break
            serie["error"] = False
        except:
            serie["error"] = True
            rollback(serie)

    if not stopCancelQueue.empty():
        msg = stopCancelQueue.get()
        if msg == "stop":
            rollback(series[index])
            series[index]["error"] = True
            series[index]["progress"] = 0
            queue.put(["series", series])
        elif msg == "cancel":
            for index in indexes:
                rollback(series[index])
                series[index]["error"] = True
            series[index]["progress"] = 0
            queue.put(["series", series])
    queue.put(["finished-2", True])

def rollback(serie):
    if os.path.exists(serie["path"]):
        shutil.rmtree(serie["path"])
    seriesDB = list(Serie.selectBy(uid=serie["uid"], description=serie["serieDescription"]))
    if seriesDB:
        serieDB = list(seriesDB)[0]
        study = serieDB.study
        patient = study.patient
        toRemove = serieDB.delete()
        serieList = list(Serie.selectBy(uid = serieDB.uid))
        if not serieList:    
            imagePath = os.path.join(patient.directory, serieDB.uid)
            if os.path.exists(imagePath):
                shutil.rmtree(imagePath)
            serieList = list(Serie.selectBy(study=study))
            if not serieList:
                toRemove = study.delete()
                for remove in toRemove:
                    if os.path.exists(remove):
                        shutil.rmtree(remove)
                
                studyList = list(Study.selectBy(patient=patient))
                if not studyList:
                    toRemove =patient.delete()
                    for remove in toRemove:
                        if os.path.exists(remove):
                            shutil.rmtree(remove)

def createYAMLFile(serie):
    logging.debug("In Importer::createYAMLFile()")
    outputFile = os.path.join(serie["path"], "{0}{1}".format(hashStr(serie["uid"]), ".yaml"))
    serie["yaml"] = os.path.join(
                        "{0}{1}".format(hashStr(serie["uid"]), hashStr(serie["serieDescription"])), 
                        "{0}{1}".format(hashStr(serie["uid"]),".yaml"))
    vtiPath  = "{0}{1}/main/main.vti".format(hashStr(serie["uid"]),hashStr(serie["serieDescription"]))
    matrix = [[1, 0, 0, 0],
              [0, 1, 0, 0],
              [0, 0, 1, 0],
              [0, 0, 0, 1]]
    mScreens = [] 
    save = {"vti": vtiPath,
            "mScreens" : mScreens}
    mScreens.append({"name": QtGui.QApplication.translate("Importer", 
                                                     "Main", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8)})

    f = file(outputFile, "w")
    yaml.dump(save, f)   
    f.close()
        
def sortSerie(serie):
    logging.debug("In Importer::sortSerie()")
    sorter = gdcm.IPPSorter()
    sorter.SetComputeZSpacing(True)
    sorter.SetZSpacingTolerance(1e-3)
    result = sorter.Sort(serie["files"])
    serie["zspacing"] = sorter.GetZSpacing() if result else 1.0
    if sorter.GetFilenames():
        serie["files"] = sorter.GetFilenames()
    
def copyFiles(serie):
    logging.debug("In Importer::copyFiles()")
    basePath = os.path.join(constant.INSTALL_DIR, "data")
    patientPath = os.path.join(basePath, hashStr(serie["patientUID"]))
    seriePath = os.path.join(patientPath,"{0}{1}".format(hashStr(serie["uid"]), hashStr(serie["serieDescription"])))
    imagePath = os.path.join(patientPath,hashStr(serie["uid"]), "images/")
    serie["path"] = seriePath
    serie["patientPath"] = patientPath
    if not os.path.exists(imagePath):
        os.makedirs(imagePath)
    for i, dicomPath in enumerate(serie["files"]):
        filePath = os.path.join(imagePath, "{0}.dcm".format(i))
        shutil.copy(dicomPath, filePath)
    
def createVTI(serie):        
    logging.debug("In Importer::createVTI()")
    size = 100
    numberOfParts = int(len(serie["files"])/size) +1
    reader = vtkgdcm.vtkGDCMImageReader()
    reader.ReleaseDataFlagOn()
    reslice = vtk.vtkImageReslice()
    change = vtk.vtkImageChangeInformation()
    change.ReleaseDataFlagOn()
    reslice.ReleaseDataFlagOn()
    writer = vtk.vtkXMLImageDataWriter()
    writer.ReleaseDataFlagOn()
    
    for i in range(numberOfParts):
        filenames = vtk.vtkStringArray()
        limit = (i+1)*size
        if limit > len(serie["files"]):
            limit = len(serie["files"])
        for filename in serie["files"][i*size:limit]:
            filenames.InsertNextValue(filename)
            
        reader.SetFileNames(filenames)
        reader.Update()
        spacing = reader.GetOutput().GetSpacing()     
        change.SetInputConnection(reader.GetOutputPort())
        #change.SetOutputOrigin(reader.GetOutput().GetSpacing())
        change.SetOutputSpacing(spacing[0], spacing[1], serie["zspacing"])
        change.Update()
        imagedata = change.GetOutput()
        change.GetInput().ReleaseData()
        path = os.path.join(serie["path"],"main")
        if not os.path.exists(path):
            os.makedirs(path) 
        
        extent = imagedata.GetExtent()
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
        
        
        reslice.SetInput(imagedata)
        reslice.SetInformationInput(imagedata)
        reslice.SetResliceAxes(resliceAxes)
        reslice.SetOutputDimensionality(3)
        reslice.Update()
        filename = os.path.join(path, "main{0}.vti".format(i))
        imagedata = reslice.GetOutput()
        reslice.GetInput().ReleaseData()
    
        writer.SetInput(imagedata)
        writer.SetFileName(filename)
        writer.Write()
    
def updateDatabase(serie):
    logging.debug("In Importer::updateDatabase()")
    patient = list(Patient.selectBy(uid=serie["patientUID"]))
    if not patient:      
        patient = Patient(uid=serie["patientUID"], 
                          name=serie["patientName"],
                          birthdate=serie["patientBirthdate"],
                          sex=serie["patientSex"],
                          tmp = False,
                          directory=serie["patientPath"])
    else:
        patient = patient[0]
    
    study = list(Study.selectBy(uid=serie["studyUID"]))
    if not study:
        study = Study(uid = serie["studyUID"], 
                  modality=serie["studyModality"],
                  description=serie["studyDescription"],
                  institution=serie["studyInstitution"],
                  tmp=False,
                  patient=patient)
    else:
        study = study[0]
    serieDB = list(Serie.selectBy(uid=serie["uid"], description=serie["serieDescription"]))      
    if serieDB:
        serieDB = serieDB[0]
        serieDB.file = serie["yaml"]
        serieDB.description = serie["serieDescription"] 
        serieDB.thickness = serie["serieThickness"]
        serieDB.size = serie["serieSize"]
        serieDB.zSpacing = serie["zspacing"]
        serieDB.dicomImages = len(serie["files"])
    else:         
        Serie(uid=serie["uid"], 
              file=serie["yaml"],
              description=serie["serieDescription"],
              thickness=serie["serieThickness"], 
              size=serie["serieSize"],   
              zSpacing=serie["zspacing"],
              tmp = False,
              dicomImages = len(serie["files"]),
              study=study)
            

def scanDirectory(directory, recursive, series, queue, stopCancelQueue):
    logging.debug("In Importer::scanDirectory()")  
    while not queue.empty():
        queue.get()
    if recursive:
        for path, folders, files in os.walk(directory):
            if not stopCancelQueue.empty() : 
                msg = stopCancelQueue.get()
                if msg == "stop":
                    break
                    
            if files:
                series = {}
                scanFiles(files, path, series)
                queue.put(["series", series])
    else:
        files = os.listdir(directory)
        scanFiles(files, directory, series)
        queue.put(["series", series])
    queue.put(["finished-1", True])
  
    
def scanFiles(files, path, series):
    logging.debug("In Importer::scanFiles()")    
    for filepath in files:
        try:
            reader = gdcm.ImageReader()
            
            inputFilepath = normalizeString(os.path.abspath(os.path.join(path, filepath)))
            reader.SetFileName(inputFilepath)
            if reader.Read():
                dataset = reader.GetFile().GetDataSet()
                serieUID = retrieveDicomTag(0x0020, 0x000E, dataset)
                if not series.has_key(serieUID):
                    serieDict = {}
                    serieDict["serieDescription"] = retrieveDicomTag(0x0008, 0x103E, dataset)
                    serieDict["serieThickness"] = retrieveDicomTag(0x0018, 0x0050, dataset)
                    if not serieDict["serieThickness"]:
                        serieDict["serieThickness"] = "0.0"
                    serieDict["serieSize"] = retrieveDicomTag(0x0070, 0x0020, dataset)
                    serieDict["studyUID"] = retrieveDicomTag(0x0020, 0x000D, dataset)
                    serieDict["studyModality"] = retrieveDicomTag(0x0040, 0x0060, dataset)
                    serieDict["studyDescription"] = retrieveDicomTag(0x0008, 0x1030, dataset)
                    serieDict["studyInstitution"] = retrieveDicomTag(0x0008, 0x0080, dataset)
                    serieDict["patientSex"] = retrieveDicomTag(0x0010, 0x0040, dataset)
                    serieDict["patientName"] = retrieveDicomTag(0x0010, 0x0010, dataset)
                    serieDict["patientUID"] = retrieveDicomTag(0x0010, 0x0020, dataset)
                    serieDict["progress"] = 0
                    serieDict["patientBirthdate"] = retrieveDicomTag(0x0010, 0x0030, dataset)
                    serieDict["patientBirthdate"] = serieDict["patientBirthdate"].replace(" ", "")
                    serieDict["error"] = False
                    serieDict["path"] = ""
                    if serieDict["patientBirthdate"]:
                        serieDict["patientBirthdate"]  = "{0}-{1}-{2}".format(
                                                    serieDict["patientBirthdate"][:4],
                                                    serieDict["patientBirthdate"][4:6],
                                                    serieDict["patientBirthdate"][6:8])
                    else:
                        serieDict["patientBirthdate"] = None
                    serieDict["files"] = [inputFilepath]   
                    serieDict["uid"] = serieUID
                    serieDict["exists"] = serieExists(serieUID, serieDict["serieDescription"])
                    if serieDict["exists"]:
                        serieDict["checked"] = False
                    else:
                        serieDict["checked"] = True
                    series[serieUID] = serieDict
                    
                else:
                    serieDict["files"] = serieDict["files"] + [inputFilepath] 
            else:
                logging.debug("Could not file as DICOM2: {0}".format(filepath))
        except:
            traceback.print_exc(file=sys.stdout)
            logging.debug("Error loading file: {0}".format(filepath))
    
def serieExists(serieID, description):
    if list(Serie.select("uid='{0}' AND description='{1}'".format(serieID, description))):
        return True
    return False

def retrieveDicomTag(a, b, dataset):
    logging.debug("In Importer::retrieveDicomTag()")
    tag = gdcm.Tag(a, b)
    if dataset.FindDataElement(tag):
        data = dataset.GetDataElement(tag).GetValue()
        if data:
            return str(data)
    return ''

def normalizeString(inputPath):
    if (sys.platform == 'win32'):
        if type(inputPath) == unicode:
            return inputPath.encode('latin-1')
    else:
        return str(inputPath)
