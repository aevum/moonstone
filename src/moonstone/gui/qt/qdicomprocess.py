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
import traceback
import logging

from PySide import QtCore, QtGui
import yaml

from .widget.progressbardialog_ui import Ui_ProgressBarDialog
from ...utils import constant
from ...bloodstone.utils.data import reader_vti, reader_to_imagedata

class QDicomProcess(QtGui.QDialog, Ui_ProgressBarDialog):

    def __init__(self, parent, series, quality, generate3D):
        logging.debug("In QDicomProcess::__init__()")
        super(QDicomProcess, self).__init__(parent)
        self.setupUi(self)
        self.stopButton.setVisible(False)
        self.cancelButton.setVisible(False)
        self.setWindowTitle(constant.TITLE_PROGRAM)
        self._series = series
        self._quality = quality
        self._generate3D = generate3D
        self._readers = []
        self._indicator = 0
        self.createActions()
        self.createSignals()
        self.updateWidgets()
        self.setWindowFlags(QtCore.Qt.Popup)
        qRect = QtCore.QRect(QtGui.QApplication.desktop().screenGeometry())
        x = qRect.width()/2-self.width()/2
        y = qRect.height()/2-self.height()/2
        self.move(x, y)

    def createActions(self):
        logging.debug("In QDicomProcess::createActions()")

    def createSignals(self):
        logging.debug("In QDicomProcess::createSignals()")
        self.signalProcessDicomFinished = \
            QtCore.SIGNAL("processDicomFinished(PyObject, PyObject, PyObject, PyObject)")

    def updateWidgets(self):
        logging.debug("In QDicomProcess::updateWidgets()")
        self.progressBar.reset()
        self.loadingText.setText(QtGui.QApplication.translate("QDicomProcess", 
                                                     "Loading...", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8))
        QtCore.QCoreApplication.processEvents()

    def normalizeSizeWidget(self):
        parentSize = self.parentWidget().size()
        sizeFixed = (290, 130)
        centerWidget = (abs(parentSize.width() - sizeFixed[0]) / 2.0,
                        abs(parentSize.height() - sizeFixed[1]) / 2.0)
        self.setMaximumSize(sizeFixed[0], sizeFixed[1])
        self.setMinimumSize(sizeFixed[0], sizeFixed[1])
        self.setGeometry(centerWidget[0], centerWidget[1],
                         sizeFixed[0], sizeFixed[1])
        self.updateGeometry()

    def startProcess(self):
        logging.debug("In QDicomProcess::startProcess()")
        self.slotProcess()

    def slotProcess(self):
        logging.debug("In QDicomProcess::slotProcess()")
        try:
            while self._indicator < len(self._series):
                self.progressBar.setValue(self._indicator)
                self.loadingText.setText(
                        QtGui.QApplication.translate("QDicomProcess", 
                                                     "Processing DICOM series ({0}/{1})", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8)
                                    .format(self._indicator,
                                            self.progressBar.maximum()))
                self.progressBar.repaint()
                self.progressBar.update()
                QtCore.QCoreApplication.processEvents()
                serie = self._series[self._indicator]
                flname = os.path.abspath(os.path.join(serie.study.patient.directory, 
                                                      serie.file))
                f = file(flname, "r")
                allVtis = yaml.load(f)
                f.close()
                logging.debug(":: Processing DICOM serie: {0}".format(flname))
    
                self.progressBar.setValue(self._indicator*40/len(self._series)+10)
                self.loadingText.setText(
                        QtGui.QApplication.translate("QDicomProcess", 
                                                     "Processing DICOM series ({0}/{1})", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8)
                                    .format(self._indicator,
                                            len(self._series)))
                self.progressBar.repaint()
                self.progressBar.update()
                QtCore.QCoreApplication.processEvents()
                vtiFlname = os.path.abspath(os.path.join(serie.study.patient.directory, 
                                                  allVtis["vti"].replace("/", os.path.sep)))
                import time
                a = time.time()
                allVtis["imagedata"] = reader_vti(vtiFlname)
                allVtis["yaml"] = flname
                allVtis["pluginYaml"] = flname.replace(".yaml", ".plugin.yaml", -1)
                self._readers.append(allVtis)
    
                self._indicator += 1
    
            logging.debug(":: Processing DICOM reader")
            self.progressBar.setValue(50)
            self.loadingText.setText(QtGui.QApplication.translate("QDicomProcess", 
                                                     "Processing DICOM reader", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8))
            self.progressBar.repaint()
            self.progressBar.update()
    
            logging.debug(":: Processing DICOM viewer")
            self.loadingText.setText(QtGui.QApplication.translate("QDicomProcess", 
                                                     "Processing DICOM viewer", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8))
            self.progressBar.repaint()
            self.progressBar.update()
    
            self.emit(self.signalProcessDicomFinished, self._readers, self._series, self._generate3D, self)
            self._readers = None
        except Exception as ex:
            import sys
            traceback.print_exc(file=sys.stdout)
            self.close()
            QtGui.QMessageBox.critical(self, QtGui.QApplication.translate("ImportChooser", 
                                                     "Error", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8), 
                                                 QtGui.QApplication.translate("QDicomProcess", 
                                                 "Error founded during loading!", 
                                                 None, 
                                                 QtGui.QApplication.UnicodeUTF8))
    
    
    def setProgress(self, progress, message):
        logging.debug("In QDicomProcess::setProgress()")
        self.progressBar.setValue(progress)
        self.loadingText.setText(message)
        self.repaint()
        self.update()
        QtCore.QCoreApplication.processEvents()