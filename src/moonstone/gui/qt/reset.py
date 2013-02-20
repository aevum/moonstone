import logging
import os
import shutil

from PySide import QtCore, QtGui

from .widget.loading_ui import Ui_Loading
from ...bloodstone.utils.data import persist_yaml_file
from ...utils import constant
from ...bloodstone.importer.database.study import Study
from ...bloodstone.importer.database.serie import Serie
from ...utils.strUtils import hashStr

class Reset(QtGui.QDialog, Ui_Loading):

    def __init__(self, parent=None, path=None):
        logging.debug("In Delete::__init__()")
        super(Reset, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(constant.TITLE_PROGRAM)
        self._start = False
        self.path = path
        self.create()
        self.createActions()
        self.updateWidgets()

    def create(self):
        logging.debug("In Delete::create()")
        self.progress = 0
        self.maximum = 0
        self.cancelProgress = False
        self.stopProgress = False
        
    def normalizeSizeWidget(self):
        logging.debug("In Delete::normalizeSizeWidget()")
        parentSize = self.parentWidget().size()
        sizeFixed = (290, 130)
        centerWidget = (abs(parentSize.width() - sizeFixed[0]) / 2.0,
                        abs(parentSize.height() - sizeFixed[1]) / 2.0)
        self.setMaximumSize(sizeFixed[0], sizeFixed[1])
        self.setMinimumSize(sizeFixed[0], sizeFixed[1])
        self.setGeometry(centerWidget[0], centerWidget[1],
                         sizeFixed[0], sizeFixed[1])
        self.updateGeometry()

    def createActions(self):
        logging.debug("In Delete::createActions()")
        
    def updateWidgets(self):
        logging.debug("In Delete::updateWidgets()")
        QtCore.QCoreApplication.processEvents()
    
    def setProgress(self, progress, message):
        self.progressBar.setValue(progress)
        self.repaint()
        self.update()
        self.loadingText.setText(message)
        self.repaint()
        self.update()
        self.loadingText.repaint()
        self.loadingText.update()
        self.progressBar.repaint()
        self.progressBar.update()
        self.repaint()
        self.update()
        QtCore.QCoreApplication.processEvents()
        self.repaint()
        self.update()
        QtCore.QCoreApplication.processEvents()
        self.repaint()
        self.update()
        QtCore.QCoreApplication.processEvents()
    
    def processReset(self, serie):
        logging.debug("In Reset::processReset()")
        self.setProgress(10, QtGui.QApplication.translate("Reset", 
                                                     "Reseting serie {0}", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8).format(serie.description))
        QtCore.QCoreApplication.processEvents()
        study = serie.study
        patient = study.patient
        yaml = os.path.join(patient.directory, serie.file)
        (path, tail) = os.path.split(yaml)
        for filepath in os.listdir(path):
            if filepath != "main":
                filepath = os.path.join(path, filepath)
                if os.path.isdir(filepath):
                    shutil.rmtree(filepath)
                else:
                    os.remove(filepath)
        
               
        idDesc = "{0}{1}".format(hashStr(serie.uid), hashStr(serie.description))
        mScreens = [] 
        save = {"vti": "{0}/main/main.vti".format(idDesc),
                "mScreens" : mScreens}
        mScreens.append({"name": QtGui.QApplication.translate("Importer", 
                                                         "Main", 
                                                         None, 
                                                         QtGui.QApplication.UnicodeUTF8)})
        
        persist_yaml_file(os.path.join(patient.directory, os.path.join(idDesc,"{0}{1}".format(hashStr(serie.uid), ".yaml"))), save)
        
        self.setProgress(100, QtGui.QApplication.translate("Reset", 
                                                     "Finished.", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8))
        self.close()
