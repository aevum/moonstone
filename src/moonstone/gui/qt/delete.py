import logging
import os
import shutil

from PySide import QtCore, QtGui

from .widget.loading_ui import Ui_Loading
from ...utils import constant
from ...bloodstone.importer.database.study import Study
from ...bloodstone.importer.database.serie import Serie

class Delete(QtGui.QDialog, Ui_Loading):

    def __init__(self, parent=None, path=None):
        logging.debug("In Delete::__init__()")
        super(Delete, self).__init__(parent)
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
        self.connect(self,  QtCore.SIGNAL("processDelete()"), self.processDelete)
        
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
    
    def processDelete(self, series):
        logging.debug("In Delete::processDelete()")
        size = len(series)
        slice = 100.0 / size
        for i, serie in enumerate(series):
            self.setProgress(i*slice, "Deleting serie {0}".format(serie.description))
            QtCore.QCoreApplication.processEvents()
            study = serie.study
            patient = study.patient
            toRemove = serie.delete()
            for i, dirPath in enumerate(toRemove):
                self.setProgress(70+i*30/len(toRemove), "Deleting dir: {0}".format(i+1))
                if os.path.exists(dirPath):
                    shutil.rmtree(dirPath)
            serieList = list(Serie.selectBy(uid = serie.uid))
            if not serieList:    
                imagePath = os.path.join(patient.directory, serie.uid)
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
        
        self.setProgress(100, "Finished.")
        self.close()
        
        self.emit(QtCore.SIGNAL("deleteFinished()"))
