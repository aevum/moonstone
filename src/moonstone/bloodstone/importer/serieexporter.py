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
import sys
import tempfile
from PySide import QtCore
from ..utils.compact import Zipper
from ..utils import compact
from ...gui.qt.widget.genericload import GenericProgressBar
from ..utils.data import persist_yaml_file, remove_file
from ..utils import multiprocessutils
from ...utils.strUtils import hashStr
from multiprocessing import Process, Value, Pipe, Lock

class SerieExporter(QtCore.QObject):
    def __init__(self, parent, outputFile, series, dicomImages):
        super(SerieExporter, self).__init__(parent)
        self._parentWindow = parent
        self._outputFile = outputFile
        self._series = self.parseSeries(series)
        self._dicomImages = dicomImages
        self._zipper = Zipper()
        self._messageCount = Value("i", 0)
        self._statusShared = Value("c", "r")
        self._lock  = Lock()
        self._text = "Exporting"
        self._progress = 0
        self._loaderBar = GenericProgressBar(self._parentWindow, stopButton = False, cancelButton = True, cancelButtonAction= self.cancel, progressFunction=self.getProgress)
        self._canceled = False

        QtCore.QTimer.singleShot(500, self.updateValue)
        self.status = "running"
    
    def parseSeries(self, series):
        result = []
        for serie in series:
            serieDb = {}
            serieDb["uid"] = serie.uid
            serieDb["dicomImages"] = serie.dicomImages
            serieDb["description"] = serie.description
            serieDb["thickness"] = serie.thickness
            serieDb["size"] = serie.size
            serieDb["zSpacing"] = serie.zSpacing
            
            study = serie.study
            serieDb["study"] = study.uid
            studyDb = {}
            studyDb["uid"] = study.uid
            studyDb["modality"] = study.modality
            studyDb["description"] = study.description
            studyDb["institution"] = study.institution
            
            patient = study.patient
            studyDb["patient"] = patient.uid
            patientDb = {}
            patientDb["uid"] = patient.uid
            patientDb["name"] = patient.name
            patientDb["birthdate"] = str(patient.birthdate)
            patientDb["sex"] = patient.sex
            patientDb["directory"] = patient.directory
            
            serieDb = {"serie": serieDb, "study" : studyDb, "patient" : patientDb}
            result.append(serieDb)
        return result
    
    def updateValue(self):
        run = True
        msg = multiprocessutils.readMessage(self._parentConn, self._messageCount, self._lock)
        if msg:
            (txt, st) = msg
            self._text = txt
            self.status = st
            self._loaderBar.updateValue()
            if self.status != "running":
                run = False
        if run and self._statusShared.value == "r" and self.process.is_alive():
            QtCore.QTimer.singleShot(500, self.updateValue)
        else:
            self._loaderBar.stopProcess()
            
        
    def start(self):
#        DBUtils().createConnection()
#        print self._series[0].study
#        print self._series[0].study.patient  
        p_conn, c_conn = Pipe()
        self._parentConn = p_conn
        self.process = Process(target=makeExport, args = (c_conn, self._messageCount, self._lock, self._statusShared, self._outputFile, self._series, self._dicomImages, Zipper.key))
        self.process.start()
        QtCore.QTimer.singleShot(500, self.updateValue)
        
        
    def getProgress(self):
        return self._progress, self._text
    
    def cancel(self):
        self._canceled = True
        self._loaderBar.stopProcess()
        self._zipper.cancel()
        self._text = "Canceled"
        
def makeExport(conn, messageCount, lock, statusShared, outputFile, series, dicomImages, key):
    ExporterProcess(conn, messageCount, lock, statusShared, outputFile, series, dicomImages, key)  
         
class ExporterProcess():
    def __init__(self, conn, messageCount, lock, sharedStatus, outputFile, series, dicomImages, key):
        self._zipper = Zipper()
        self._outputFile = outputFile
        self._series = series
        self._dicomImages = dicomImages
        self._conn = conn
        self._messageCount = messageCount
        self._lock = lock
        self._sharedStatus = sharedStatus
        self._text = "Exporting"
        self._status = "running"
        self._key = key
        self.export()
        
    def updateStatus(self):
        multiprocessutils.sendMessage(self._conn, self._messageCount, self._lock, (self._text, self._status))
        
    
    def export(self):
        try:
            seriesDicom = []
            
            self._zipper.start(self._outputFile)
            seriesInfo = []
            
            for serieDict in self._series:
                if self._sharedStatus.value == "r":
                    serie = serieDict["serie"]
                    self._text = "Exporting {0}".format(serie["description"])
                    self.updateStatus()
                    patient = serieDict["patient"]
                    serieDicomFolder = "{0}{1}{2}".format(patient["directory"], os.path.sep, hashStr(serie["uid"]))
                    serieFolder = "{0}{1}".format(serieDicomFolder, hashStr(serie["description"]))
                    serieDbPath = "{0}{1}{2}".format(serieFolder,os.path.sep, "export.db")
                    persist_yaml_file(serieDbPath, serieDict)
                    self._zipper.recursive_zip(serieFolder)
                    remove_file(serieDbPath)
                    
                    if seriesDicom.count(serie["uid"]) == 0:
                        if self._dicomImages:
                            self._zipper.recursive_zip(serieDicomFolder)
                        else:
                            folderImagePath = "{0}{1}{2}".format(serieDicomFolder, os.path.sep, "images")
                            files = os.listdir(folderImagePath)
                            files = sorted(files)
                            file = files[len(files)/2]
                            filePath = "{0}{1}{2}".format(folderImagePath, os.path.sep, file)
                            root = "{0}{1}{2}{3}{4}".format(hashStr(serie["uid"]), os.path.sep, "images", os.path.sep, file)
                            self._zipper.recursive_zip(filePath, root)
                        seriesDicom.append(serie["uid"])
                    serieDicomOutFolder = hashStr(serie["uid"])
                    serieOutFolder = "{0}{1}".format(serieDicomOutFolder, hashStr(serie["description"]))
                    seriesInfo.append({"serieFolder" :serieOutFolder, "serieDicomFolder" : serieDicomOutFolder})
            if self._sharedStatus.value == "r":
                seriesInfoFile = tempfile.NamedTemporaryFile(delete=False)
                persist_yaml_file(seriesInfoFile.name, seriesInfo)
                seriesInfoFilename = compact.encryptFile(seriesInfoFile.name, self._key)
                self._zipper.recursive_zip(seriesInfoFilename, "seriesInfo")
                self._zipper.finish()
        finally:
            self._status = "finish"
            self._sharedStatus.value = "f"
            self.updateStatus()

def exportSerie(serie, outputFile):
    seriesDicom = []
    zipper = Zipper()  
    zipper.start(outputFile)
    seriesInfo = []
    study = serie.study
    patient = study.patient
    serieDicomFolder = "{0}{1}{2}".format(patient.directory, os.path.sep, hashStr(serie.uid))
    serieFolder = "{0}{1}".format(serieDicomFolder, hashStr(serie.description))
    serieDbPath = "{0}{1}{2}".format(serieFolder,os.path.sep, "export.db")
    
    serieDb = {}
    serieDb["uid"] = serie.uid
    serieDb["dicomImages"] = serie.dicomImages
    serieDb["description"] = serie.description
    serieDb["thickness"] = serie.thickness
    serieDb["size"] = serie.size
    serieDb["zSpacing"] = serie.zSpacing
    
    serieDb["study"] = study.uid
    studyDb = {}
    studyDb["uid"] = study.uid
    studyDb["modality"] = study.modality
    studyDb["description"] = study.description
    studyDb["institution"] = study.institution
    studyDb["patient"] = patient.uid
    
    patientDb = {}
    patientDb["uid"] = patient.uid
    patientDb["name"] = patient.name
    patientDb["birthdate"] = str(patient.birthdate)
    patientDb["sex"] = patient.sex
    patientDb["directory"] = patient.directory
            
    serieDict = {"serie": serieDb, "study" : studyDb, "patient" : patientDb}
    persist_yaml_file(serieDbPath, serieDict)
    zipper.recursive_zip(serieFolder)
    remove_file(serieDbPath)
    
    if seriesDicom.count(serie.uid) == 0:
        zipper.recursive_zip(serieDicomFolder)
        seriesDicom.append(serie.uid)
    serieDicomOutFolder = hashStr(serie.uid)
    serieOutFolder = "{0}{1}".format(serieDicomOutFolder, hashStr(serie.description))
    seriesInfo.append({"serieFolder" :serieOutFolder, "serieDicomFolder" : serieDicomOutFolder})
    seriesInfoFile = tempfile.NamedTemporaryFile(delete=False)
    persist_yaml_file(seriesInfoFile.name, seriesInfo)
    seriesInfoFilename = compact.encryptFile(seriesInfoFile.name, zipper.key)
    zipper.recursive_zip(seriesInfoFilename, "seriesInfo")
    zipper.finish()

    
    