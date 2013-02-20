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
from PySide import QtCore, QtGui
from .genericprogressbardialog_ui import Ui_GenericProgressBarDialog

class GenericProgressBar(QtGui.QDialog, Ui_GenericProgressBarDialog):
    def __init__(self, parent, stopButton=True, cancelButton=False, progressBar=False, stopButtonAction=None, cancelButtonAction=None, progressFunction=None):
        super(GenericProgressBar, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Popup)
        qRect = QtCore.QRect(QtGui.QApplication.desktop().screenGeometry())
        x = qRect.width()/2-self.width()/2
        y = qRect.height()/2-self.height()/2
        self.move(x, y)
        movie = QtGui.QMovie()
        movie.setFileName(":/static/default/ajax-loader.gif")
        self.loadingLabel.setMovie(movie)
        QtCore.QObject.connect(movie, QtCore.SIGNAL("frameChanged(int)"), lambda i: movie.jumpToFrame(i))
        movie.start()
        
        #busyCursor = QtGui.QCursor(QtCore.Qt.BusyCursor)
        #QtGui.QApplication.setOverrideCursor(busyCursor)
        
        self.progressBar.setVisible(progressBar)
        self.stopButton.setVisible(stopButton)
        self.cancelButton.setVisible(cancelButton)
        if progressFunction:
            self.progressFunction = progressFunction
        self.createActions(stopButtonAction, cancelButtonAction)
        self.setVisible(True)
        self.updateWidgets()
     
    def centralize(self):
        self.setWindowFlags(QtCore.Qt.Popup)
        qRect = QtCore.QRect(QtGui.QApplication.desktop().screenGeometry())
        x = qRect.width()/2-self.width()/2
        y = qRect.height()/2-self.height()/2
        self.move(x, y);
        
    def progressFunction(self):
        return 0, QtGui.QApplication.translate(
                    "GenericProgressBar", "Loading...", None,
                    QtGui.QApplication.UnicodeUTF8)
    
    def createActions(self, stopButtonAction, cancelButtonAction):
        logging.debug("In QDicomProcess::createActions()")
        if stopButtonAction:
            self.connect(self.stopButton, QtCore.SIGNAL("released()"),
                         stopButtonAction)
        if cancelButtonAction:
            self.connect(self.cancelButton, QtCore.SIGNAL("released()"),
                         cancelButtonAction)

    def updateWidgets(self):
        logging.debug("In QDicomProcess::updateWidgets()")
        self.progressBar.reset()
        self.loadingText.setText(QtGui.QApplication.translate(
                    "GenericProgressBar", "Loading...", None,
                    QtGui.QApplication.UnicodeUTF8))
        QtCore.QCoreApplication.processEvents()

    def normalizeSizeWidget(self):
        parentSize = self.parentWidget().size()
        sizeFixed = (290, 130)
        centerWidget = (abs(parentSize.width() - sizeFixed[0]) / 2.0,
                        abs(parentSize.height() - sizeFixed[1]) / 2.0)
        self.setMaximumSize(sizeFixed[0], sizeFixed[1])
        self.setMinimumSize(sizeFixed[0], sizeFixed[1])
        self.setGeometry(centerWidget[0], centerWidget[1], sizeFixed[0], sizeFixed[1])
        self.updateGeometry()

    def stopProcess(self):
        QtGui.QApplication.restoreOverrideCursor()
        QtCore.QCoreApplication.processEvents()
        self.close()
        
    def closeEvent(self, event):
        QtGui.QApplication.restoreOverrideCursor()
        QtCore.QCoreApplication.processEvents()
        super(GenericProgressBar, self).closeEvent(event)
        
    def updateValue(self):
        progress = None
        message = None
        if self.progressFunction:
            (progress, message) = self.progressFunction()
        self.updateProgress(progress, message)
    

    def updateProgress(self, progress=None, message=None):
        logging.debug("In GenericProgressBar::updateProgress()")
        if progress:
            self.progressBar.setValue(progress)
        if message:
            self.loadingText.setText(message)
        QtCore.QCoreApplication.processEvents()
        