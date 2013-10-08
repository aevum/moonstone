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
import zipfile
import shutil
import os
import tempfile
import logging
from multiprocessing import Process, Value, Pipe, Lock
from PySide import QtCore, QtGui
from .database.patient import Patient
from .database.serie import Serie
from .database.study import Study
from .database.dbutils import DBUtils
from ..utils import compact
from ...gui.qt.widget.genericload import GenericProgressBar
from ..utils.data import remove_file, load_vtis_from_yaml_file, load_yaml_file, persist_yaml_file
from ...utils.strUtils import hashStr
from ...utils import constant

class SerieImporter(QtCore.QObject):
    
    def __init__(self, parent, inputFile, onComplete = None):
        logging.debug("In SerieImporter::__init__()")
        super(SerieImporter, self).__init__(parent)
        self._parentWindow = parent
        self._inputFile = inputFile
        self._text = "Importing"
        self._progress = 0
        self._loaderBar = GenericProgressBar(self._parentWindow, stopButton = True, cancelButton = False, stopButtonAction= self.stop, progressFunction=self.getProgress)
        self._messageCount = Value("i", 0)
        self._statusShared = Value("c", "r")
        self._lock  = Lock()
        self.onComplete = onComplete
        self._ignoredSeries = []
        self._importedSeries = []
        self._errorSeries = []

    def start(self):
        logging.debug("In SerieImporter::start()")
        p_conn, c_conn = Pipe()
        self._parentConn = p_conn
        self.process = Process(target=makeImport, args = (c_conn, self._messageCount, self._lock, self._statusShared, self._inputFile, compact.Zipper.key))
        self.process.start()
#        makeImport(c_conn, self._messageCount, self._lock, self._statusShared, self._inputFile)
        QtCore.QTimer.singleShot(500, self.verifyUpdate)
        
    def getProgress(self):
        logging.debug("In SerieImporter::getProgress()")
        return self._progress, self._text
    
    @staticmethod
    def readMessage(conn, messageCount, lock):
        logging.debug("In SerieImporter::readMessage()")
        result = None
        lock.acquire()
        try :
            if messageCount.value > 0:
                messageCount.value = messageCount.value - 1
                result =  conn.recv()
        finally:
            lock.release()
        return result
    
        
    def verifyUpdate(self):
        logging.debug("In SerieImporter::verifyUpdate()")
        run = True
        while self._messageCount.value > 0:
            (status, text, importedSeries, ignoredSeries, errorSeries, errorMessage) = SerieImporter.readMessage(self._parentConn, self._messageCount, self._lock)
            self._text = text
            self._loaderBar.updateValue()
            if status != "running":
                self._loaderBar.stopProcess()
                message = ""
                if ignoredSeries:
                    message = QtGui.QApplication.translate("SerieImporter", 
                                                     "Series already existing:", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8)
                    for serie in ignoredSeries:
                        message = "{0}\n{1}".format(message,serie)
                
                if errorSeries:
                    message = "{0}\n{1}".format(message, QtGui.QApplication.translate("SerieImporter", 
                                                     "Error importing series:", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8))
                    for serie in errorSeries:
                        message = "{0}\n{1}".format(message,serie) 
                if errorSeries or ignoredSeries: 
                    QtGui.QMessageBox.warning(self._parentWindow, QtGui.QApplication.translate("SerieImporter", 
                                                     "Warning", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8), message)
                if status == "error":
                    QtGui.QMessageBox.critical(self._parentWindow, QtGui.QApplication.translate("SerieImporter", 
                                                     "Error", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8), errorMessage)
                else:
                    self.onComplete()
                run = False
        if run and self.process.is_alive():
            QtCore.QTimer.singleShot(500, self.verifyUpdate)
        else:    
            self._loaderBar.stopProcess()
            
    def onComplete(self):
        logging.debug("In SerieImporter::onComplete()")
                            
    def stop(self):
        logging.debug("In SerieImporter::stop()")
        self._status = "canceled"
        self._statusShared.value = "c"
        
def makeImport(conn, messageCount, lock, statusShared, inputFile, key):
    logging.debug("In SerieImporter::makeImport()")
    Importer(conn, messageCount, lock, statusShared, inputFile, key)
    
class Importer():
    def __init__(self, conn, messageCount, lock, sharedStatus, inputFile, key):
        self.importSeries(conn, messageCount, lock, sharedStatus, inputFile, key)
        
    @staticmethod
    def sendMessage(conn, messageCount, lock, message):
        lock.acquire()
        try :
            conn.send(message)
            messageCount.value = messageCount.value+1
        finally:
            lock.release()
    @staticmethod    
    def createstructure(file, dir):
        Importer.makedirs(Importer.listdirs(file), dir)
        
    @staticmethod    
    def makedirs(directories, basedir):
        for dir in directories:
            curdir = os.path.join(basedir, dir)
            if not os.path.exists(curdir):
                os.makedirs(curdir)
    @staticmethod
    def listdirs(file):
        zf = zipfile.ZipFile(file)
        dirs = []
        for name in zf.namelist():
            (head,tail)=os.path.split(name)
            dirs.append(head)
        return dirs
    
    def importSeries(self, conn, messageCount, lock, sharedStatus, inputFile, key):
        try :
            errorMessage = None
            text = ""
            importedSeries = []
            ignoredSeries = []
            errorSeries = []
            status = "running"
            errorMessage = None
            rootFile = None
            inputFile = str(inputFile)
            if not zipfile.is_zipfile(inputFile):
                errorMessage = "The file format is not valid!"
                status = "error"
                Importer.sendMessage(conn, messageCount, lock, (status, text, importedSeries, ignoredSeries, errorSeries, errorMessage))
                return
#            inputZip = zipfile.ZipFile(inputFile)
#            basePath = os.path.join(constant.INSTALL_DIR, "data")
#            rootFile = tempfile.mkdtemp()
#            Importer.createstructure(inputFile, rootFile)
#            for myFile in inputZip.namelist():
#                if not os.path.isdir(myFile):
#                    text = "Unpacking {0}".format(myFile)
#                #Importer.sendMessage(conn, messageCount, lock, (status, text, importedSeries, ignoredSeries, errorSeries, errorMessage))
#                p = os.path.normpath(os.path.join(rootFile, myFile))
#                inputZip.extract(myFile, p)
            try :
                inputZip = zipfile.ZipFile(inputFile)
                basePath = os.path.join(constant.INSTALL_DIR, "data")
                rootFile = tempfile.mkdtemp()
                Importer.createstructure(inputFile, rootFile)
                for myFile in inputZip.namelist():
                    if not os.path.isdir(myFile):
                        text = "Unpacking {0}".format(myFile)
                        Importer.sendMessage(conn, messageCount, lock, (status, text, importedSeries, ignoredSeries, errorSeries, errorMessage))
                        p = os.path.join(rootFile, myFile)
                        outfile = file(p, "wb")
                        outfile.write(inputZip.read(myFile))
                        outfile.flush()
                        outfile.close()
            except Exception as ex:
                errorMessage = "Error opening project!"
                status = "error"
                Importer.sendMessage(conn, messageCount, lock, (status, text, importedSeries, ignoredSeries, errorSeries, errorMessage))
                return
            seriesInfoPath = os.path.join(rootFile, "seriesInfo")
            seriesInfoFilename = compact.decryptFile(seriesInfoPath, key)
            seriesInfo = load_vtis_from_yaml_file(seriesInfoFilename)
            
            if not seriesInfo:
                errorMessage = "This is not valid project!"
                status = "error"
                Importer.sendMessage(conn, messageCount, lock, (status, text, importedSeries, ignoredSeries, errorSeries, errorMessage))
                return
            
            database = DBUtils()
            database.createConnection()
            for serie in seriesInfo:
                if status == "running" and sharedStatus.value == "r":
                    try :
                        serieYaml = None
                        serieDbPath = os.path.join(os.path.join(rootFile, serie["serieFolder"]), "export.db")
                        serieDb = load_vtis_from_yaml_file(serieDbPath)
                        serieYaml = serieDb["serie"]
                        text = "{0}{1}".format(serieYaml["uid"], serieYaml["description"]) 
                        Importer.sendMessage(conn, messageCount, lock, (status, text, importedSeries, ignoredSeries, errorSeries, errorMessage))
                        remove_file(serieDbPath)
                        
                        patientYaml = serieDb["patient"]
                        patientList = list(Patient.selectBy(uid=patientYaml["uid"]))
                        if not patientList:
                            patient = Patient(uid = patientYaml["uid"],
                                              name = patientYaml["name"],
                                              birthdate = patientYaml["birthdate"],
                                              sex =patientYaml["sex"],
                                              directory = os.path.join(basePath, hashStr(patientYaml["uid"])))
                        else :
                            patient = patientList[0]
                        
                        studyYaml = serieDb["study"]
                        studyList = list(Study.selectBy(uid=studyYaml["uid"]))
                        if not studyList:
                            study = Study(uid = studyYaml["uid"],
                                          modality = studyYaml["modality"],
                                          description = studyYaml["description"],
                                          institution = studyYaml["institution"],
                                          patient = patient)
                        else :
                            study = studyList[0]
                        
                        serieList = list(Serie.selectBy(uid=serieYaml["uid"]))
                        if not serieList:
                            serieDb = Serie(uid = serieYaml["uid"],
                                            dicomImages = serieYaml["dicomImages"],
                                            file = os.path.join("{0}{1}".format(hashStr(serieYaml["uid"]),hashStr(serieYaml["description"])),"{0}.yaml".format(hashStr(serieYaml["uid"]))), 
                                            description = serieYaml["description"],
                                            thickness = serieYaml["thickness"],
                                            size = serieYaml["size"],
                                            zSpacing = serieYaml["zSpacing"],
                                            study = study)
                            
                            oldPath = os.path.join(rootFile, serie["serieDicomFolder"])
                            newPath = os.path.join(patient.directory, serie["serieDicomFolder"])
                            shutil.copytree(oldPath, newPath)
                            
                            oldPath = os.path.join(rootFile, serie["serieFolder"])
                            newPath = os.path.join(patient.directory, serie["serieFolder"])
                            shutil.copytree(oldPath, newPath)
                            serieDesc = "{0}{1}".format(serieYaml["uid"], serieYaml["description"])
                            importedSeries.append(serieDesc)
                        else :
                            exist = False
                            for inSerie in serieList:
                                if inSerie.description == serieYaml["description"]:
                                    exist = True 
                            
                            if exist:
                                serieDesc = "{0}{1}".format(serieYaml["uid"], serieYaml["description"])
                                ignoredSeries.append(serieDesc)
                            else :
                                serieDb = Serie(uid = serieYaml["uid"],
                                            dicomImages = serieYaml["dicomImages"],
                                            file = os.path.join("{0}{1}".format(hashStr(serieYaml["uid"]),hashStr(serieYaml["description"])),"{0}.yaml".format(hashStr(serieYaml["uid"]))),
                                            description = serieYaml["description"],
                                            thickness = serieYaml["thickness"],
                                            size = serieYaml["size"],
                                            zSpacing = serieYaml["zSpacing"],
                                            study = study)
                                
                                oldPath = os.path.join(rootFile, serie["serieFolder"])
                                newPath = os.path.join(patient.directory, serie["serieFolder"])
                                shutil.copytree(oldPath, newPath)
                                
                                oldPath = os.path.join(os.path.join(rootFile, serie["serieDicomFolder"]), "images")
                                newPath = os.path.join(os.path.join(patient.directory, serie["serieDicomFolder"]), "images")
                                
                                for f in os.listdir(oldPath):
                                    if not os.path.exists(os.path.join(newPath, f)):
                                        shutil.copy2(os.path.join(oldPath, f), os.path.join(newPath, f))
                                
                                serieDesc = "{0}{1}".format(serieYaml["uid"], serieYaml["description"])
                                importedSeries.append(serieDesc)
                            
                    except Exception as ex:
                        print type(ex)
                        print ex.args
                        print ex
                        if serieYaml:
                            serie = "{0}{1}".format(serieYaml["uid"], serieYaml["description"])
                            errorSeries.append(serie)
                            
            if status == "running":
                status = "completed"
            Importer.sendMessage(conn, messageCount, lock, (status, text, importedSeries, ignoredSeries, errorSeries, errorMessage))
        finally:
            if rootFile:
                shutil.rmtree(rootFile, True)


def importSeries(inputFile, key=compact.Zipper.key, serieDescription=None):
    try :
        importedSeries = []
        ignoredSeries = []
        errorSeries = []
        status = "running"
        rootFile = None
        inputFile = str(inputFile)
        if not zipfile.is_zipfile(inputFile):
            print "1"
            return False
        try :
            inputZip = zipfile.ZipFile(inputFile)
            basePath = os.path.join(constant.INSTALL_DIR, "data")
            rootFile = tempfile.mkdtemp()
            Importer.createstructure(inputFile, rootFile)
            for myFile in inputZip.namelist():
                if not os.path.isdir(myFile):
                    p = os.path.join(rootFile, myFile)
                    outfile = file(p, "wb")
                    outfile.write(inputZip.read(myFile))
                    outfile.flush()
                    outfile.close()
        except Exception as ex:
            print 2, ex
            return False
        seriesInfoPath = os.path.join(rootFile, "seriesInfo")
        seriesInfoFilename = compact.decryptFile(seriesInfoPath, key)
        seriesInfo = load_vtis_from_yaml_file(seriesInfoFilename)
        if not seriesInfo:
            print 3
            return False
        
        database = DBUtils()
        database.createConnection()
        for serie in seriesInfo:
                try :   
                    serieYaml = None
                    serieDbPath = os.path.join(os.path.join(rootFile, serie["serieFolder"]), "export.db")
                    serieDb = load_vtis_from_yaml_file(serieDbPath)
                    serieYaml = serieDb["serie"]
                    if serieDescription:
                        serieYaml["description"] = serieDescription     
                    remove_file(serieDbPath)
                    
                    patientYaml = serieDb["patient"]
                    patientList = list(Patient.selectBy(uid=patientYaml["uid"]))
                    if not patientList:
                        patient = Patient(uid = patientYaml["uid"],
                                          name = patientYaml["name"],
                                          birthdate = patientYaml["birthdate"],
                                          sex =patientYaml["sex"],
                                          directory = os.path.join(basePath, hashStr(patientYaml["uid"])))
                    else :
                        patient = patientList[0]
                    
                    studyYaml = serieDb["study"]
                    studyList = list(Study.selectBy(uid=studyYaml["uid"]))
                    if not studyList:
                        study = Study(uid = studyYaml["uid"],
                                      modality = studyYaml["modality"],
                                      description = studyYaml["description"],
                                      institution = studyYaml["institution"],
                                      patient = patient)
                    else :
                        study = studyList[0]
                    
                    serieList = list(Serie.selectBy(uid=serieYaml["uid"], description=serieYaml["description"]))
                    if not serieList:
                        serieDb = Serie(uid = serieYaml["uid"],
                                        dicomImages = serieYaml["dicomImages"],
                                        file = os.path.join("{0}{1}".format(hashStr(serieYaml["uid"]),hashStr(serieYaml["description"])),"{0}.yaml".format(hashStr(serieYaml["uid"]))), 
                                        description = serieYaml["description"],
                                        thickness = serieYaml["thickness"],
                                        size = serieYaml["size"],
                                        zSpacing = serieYaml["zSpacing"],
                                        study = study)
                        oldPath = os.path.join(rootFile, serie["serieDicomFolder"])
                        if serieDescription:
                            newPath =  os.path.join(patient.directory, hashStr(serieYaml["uid"]))

                        else:      
                            newPath = os.path.join(patient.directory, serie["serieDicomFolder"])
                        if not os.path.exists(newPath):
                            shutil.copytree(oldPath, newPath)
                        
                        oldPath = os.path.join(rootFile, serie["serieFolder"])
                        if serieDescription:
                            newPath = os.path.join(patient.directory, "{0}{1}".format(hashStr(serieYaml["uid"]), hashStr(serieYaml["description"])))
                        else:
                            newPath = os.path.join(patient.directory, serie["serieFolder"])
                        shutil.copytree(oldPath, newPath)
                        if serieDescription:
                            yamlFilepath = os.path.join(
                                                    patient.directory, 
                                                    "{0}{1}".format(hashStr(serieYaml["uid"]), hashStr(serieYaml["description"])), 
                                                    "{0}.yaml".format(hashStr(serieYaml["uid"]))
                                                    )
                            newYamlData = load_yaml_file(yamlFilepath)
                            newYamlData["vti"] = os.path.join("{0}{1}".format(hashStr(serieYaml["uid"]),hashStr(serieYaml["description"])), "main", "main.vti")
                            persist_yaml_file(yamlFilepath, newYamlData) 
                        serieDesc = "{0}{1}".format(serieYaml["uid"], serieYaml["description"])

                        importedSeries.append(serieDesc)
                        
                except Exception as ex:
                    print type(ex)
                    print ex.args
                    print ex
                    if serieYaml:
                        serie = "{0}{1}".format(serieYaml["uid"], serieYaml["description"])
                        errorSeries.append(serie)
                    return False
                        
        if status == "running":
            status = "completed"
    except Exception as ex:
        return False
    finally:
        if rootFile:
            shutil.rmtree(rootFile, True)
        return True