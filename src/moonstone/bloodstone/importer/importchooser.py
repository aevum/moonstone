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
from PySide import QtCore, QtGui

from widget.importchooser_ui import Ui_ImportChooser
from importitemdelegate import ImportItemDelegate
from importer import Importer
from rename import Rename

class ImportChooser(QtGui.QDialog, Ui_ImportChooser):

    def __init__(self, parent=None, updater=None, availableStudies=0):
        logging.debug("In ImportChooser::__init__()")
        super(ImportChooser, self).__init__(parent)
        self.setupUi(self)
        self.stopButton.setDisabled(True)
        self.importButton.setDisabled(True)
        self.availableStudiesLabel.setText(self.availableStudiesLabel.text().format(availableStudies))
        self._availableStudies = availableStudies
        if availableStudies == -1:
            self.availableStudiesLabel.setVisible(False)
        self.createActions()
        self.createSignals()
        self._singleShotTime = 500
        self.updateWidgets()
        self._importer = Importer()
        self._updater = updater
        self._warning = False
        self._msg = ""
        self._firstImport = False
        self.rename = Rename(self)
        self.rename.label.setText(QtGui.QApplication.translate("ImportChooser", 
                                                     "Serie's Description:", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8))
        
    def createSignals(self):
        logging.debug("In ImportChooser::createSignals()")
    
    def createActions(self):
        logging.debug("In ImportChooser::createActions()")
        self.connect(self.cancelButton, QtCore.SIGNAL("clicked()"),
                     self.slotActionCancel)
        self.connect(self.stopButton, QtCore.SIGNAL("clicked()"),
                     self.slotActionStop)
        self.connect(self.importButton, QtCore.SIGNAL("clicked()"),
                     self.slotActionImport)
        self.connect(self.addButton, QtCore.SIGNAL("clicked()"),
                     self.slotActionAdd)
        self.connect(self.tableView, QtCore.SIGNAL("clicked(QModelIndex)"),
                     self.slotActionItemClicked)
        self.connect(self.tableView, QtCore.SIGNAL("doubleClicked(QModelIndex)"),
                     self.slotActionItemDoubleClicked)
        
    
    def slotActionStop(self):
        if self._importer.finished == 0:
            self._msg = QtGui.QApplication.translate("ImportChooser", 
                                                     "Stopping", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8)
            self.stopButton.setDisabled(True)
            self._importer.stop()
    
    def slotActionItemClicked(self, modelIndex):
        if modelIndex.column() == 1:
            uid =  self.itemModel.data(self.itemModel.index(modelIndex.row(), 6))
            if modelIndex.data(QtCore.Qt.CheckStateRole) == QtCore.Qt.Checked:
                self._importer.series[uid]["checked"] = False
                self.itemModel.setData(modelIndex, QtCore.Qt.Unchecked, QtCore.Qt.CheckStateRole)
            else:
                self.itemModel.setData(modelIndex, QtCore.Qt.Checked, QtCore.Qt.CheckStateRole) 
                self._importer.series[uid]["checked"] = True
    
    def slotActionItemDoubleClicked(self, modelIndex):
        self.rename.renameSerie(self._importer.
                                series[self.itemModel.
                                       data(
                                            self.itemModel.index(
                                                    modelIndex.row(), 6))]
                                , self.fillTable)
    
    def slotActionCancel(self):
        self._msg = QtGui.QApplication.translate("ImportChooser", 
                                                     "Cancelling", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8)
        if self._importer.finished == 0 and  self._firstImport:
            self.cancelButton.setDisabled(True)
            self._importer.cancel()
        else:
            self.close()
    
    def slotActionAdd(self):
        settings = QtCore.QSettings("Moonstone", "Medical")
        lastdir = settings.value("ImportChooser-last-dir")
        
        caption = QtGui.QApplication.translate("ImportChooser", 
                                                     "Select the directory of DICOMs", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8)
        options = QtGui.QFileDialog.ShowDirsOnly

        dialog = QtGui.QFileDialog.getExistingDirectory(
            self, caption, lastdir, options)
        if dialog:
            #while QtCore.QCoreApplication.hasPendingEvents():
            #    QtCore.QCoreApplication.processEvents()
            self.loadDirectory(dialog)
            settings.setValue("ImportChooser-last-dir", dialog)
            
        
    def slotActionImport(self):
        logging.debug("In ImportChooser::slotActionImport()")
        self._firstImport = True
        self._msg =  QtGui.QApplication.translate("ImportChooser", 
                                                     "Importing series...", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8)
        series = []
        for i in range(self.itemModel.rowCount()):   
            if self.itemModel.data(self.itemModel.index(i, 1), QtCore.Qt.CheckStateRole) == QtCore.Qt.Checked:
                series.append(self.itemModel.data(self.itemModel.index(i, 6)))
                self._importer.series[self.itemModel.data(self.itemModel.index(i, 6))]["error"] == False
        if len(series) == 0:
            QtGui.QMessageBox.information(self, QtGui.QApplication.translate("ImportChooser", 
                                                     "Warning", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8), 
                                                     QtGui.QApplication.translate("ImportChooser", 
                                                     "There is no serie selected!", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8))
        elif len(series) <= self._availableStudies or self._availableStudies == -1:
            self.cancelButton.setDisabled(False)
            self._importer.makeImport(series)
            self.addButton.setDisabled(True)
            self.importButton.setDisabled(True)
            self.stopButton.setEnabled(True)
            self.recursiveCheck.setDisabled(True)
            self.tableView.setEnabled(False)
            self.progressLabel.show()
            self.updateProgress()
        else:
            QtGui.QMessageBox.critical(self, QtGui.QApplication.translate("ImportChooser", 
                                                     "Error", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8), 
                                                     QtGui.QApplication.translate("ImportChooser", 
                                                     "You do not have sufficient series available. Please uncheck the excess!", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8))
            
        
        
    def updateWidgets(self):
        logging.debug("In ImportChooser::updateWidgets()")
        self.itemModel = QtGui.QStandardItemModel()
        self.itemModel.setHorizontalHeaderLabels(
                    [" " , 
                     " ",
                     QtGui.QApplication.translate("ImportChooser", 
                                                     "Progress", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8), 
                     QtGui.QApplication.translate("ImportChooser", 
                                                     "Patient", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8), 
                     QtGui.QApplication.translate("ImportChooser", 
                                                     "Description", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8), 
                     QtGui.QApplication.translate("ImportChooser", 
                                                     "Images", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8), 
                     QtGui.QApplication.translate("ImportChooser", 
                                                     "UID", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8)])
        self.tableView.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tableView.setModel(self.itemModel)
        self.tableView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tableView.setItemDelegate(ImportItemDelegate())
        self.tableView.setSortingEnabled(True)
        self.tableView.setColumnWidth(0, 20)
        self.tableView.setColumnWidth(1, 30)
        self.tableView.setColumnWidth(2, 80)
        self.tableView.setColumnWidth(3, 260)
        self.tableView.setColumnWidth(4, 190)
        self.tableView.setColumnWidth(5, 60)
        self.tableView.setColumnHidden(6, True)
        
    def updateProgress(self):
        logging.debug("In ImportChooser::updateProgress()")
        self._importer.updateSeries()
        if not self._importer.finished:
            self.statusLabel.setText(self._msg)
            QtCore.QTimer.singleShot(self._singleShotTime, self.updateProgress)
        else:
            self.stopButton.setDisabled(True)
            self.cancelButton.setDisabled(False)
            self.statusLabel.setText(QtGui.QApplication.translate("ImportChooser", 
                                                     "Complete", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8))
            self.progressLabel.hide()
            self.addButton.setDisabled(False)
            self.importButton.setDisabled(False)
            self.recursiveCheck.setDisabled(False)
            self.tableView.setEnabled(True)
            if self._importer.finished == 1 and self._warning:
                QtGui.QMessageBox.warning(self, QtGui.QApplication.translate("ImportChooser", 
                                                     "Warning", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8), 
                                                     QtGui.QApplication.translate("ImportChooser", 
                                                     "There are series you want to import" +
                                                       " that already are in database. These series will" + 
                                                       " automaticaly be unchecked, if you want to" +
                                                       " import any of them, check is manualy.", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8))
            elif self._importer.finished == 2:
                values = self._importer.series.values()
                error = False
                seriesImported = 0
                for serie in values:
                    if serie["error"]:
                        error = True
                    else:
                        if serie["checked"]:
                            seriesImported = seriesImported + 1
                if not error:
                    QtGui.QMessageBox.information(self, QtGui.QApplication.translate("ImportChooser", 
                                                     "Success", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8), 
                                                     QtGui.QApplication.translate("ImportChooser", 
                                                     "All series were imported with success!", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8))
                    self.close()
                else: 
                    QtGui.QMessageBox.critical(self, QtGui.QApplication.translate("ImportChooser", 
                                                     "Error", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8), 
                                                     QtGui.QApplication.translate("ImportChooser", 
                                                     "Error founded during importation!", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8))
                if self._updater:
                    self._updater(seriesImported)
        self.fillTable(self._importer.series)
    
    def loadDirectory(self, directory):
        logging.debug("In ImportChooser::loadDirectory()")
        self._importer.loadDirectory(directory, self.recursiveCheck.isChecked())
        self._msg = QtGui.QApplication.translate("ImportChooser", 
                                                 "Loading directory...", 
                                                 None, 
                                                 QtGui.QApplication.UnicodeUTF8)
        if not self.progressLabel.movie():
            movie = QtGui.QMovie()
            movie.setFileName(":/static/default/ajax-loader.gif")
            self.progressLabel.setMovie(movie)
            QtCore.QObject.connect(movie, QtCore.SIGNAL("frameChanged(int)"), lambda i: movie.jumpToFrame(i))
            self.progressLabel.movie().start()
        self.addButton.setDisabled(True)
        self.importButton.setDisabled(True)
        if self.recursiveCheck.isChecked:
            self.stopButton.setDisabled(False)
        else:
            self.stopButton.setDisabled(True)
        self.cancelButton.setDisabled(True)
        self.recursiveCheck.setDisabled(True)
        self.tableView.setEnabled(False)
        self.progressLabel.show()
        self.updateProgress()
                
    
    def fillTable(self, series=None):
        logging.debug("In ImportChooser::fillTable()")
        if not series:
            series = self._importer.series
        self.itemModel.setRowCount(len(series))
        values = series.values()
        self._warning = False
        for i, serie in enumerate(values):
            if (self._importer.finished == 2 and serie["error"]) or self._importer.finished != 2:
                if serie["checked"]:
                    checked = QtCore.Qt.Checked
                else:
                    checked = QtCore.Qt.Unchecked
                icon = QtGui.QIcon()
                if serie["error"]:
                    icon.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/dialog-error.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                    self.itemModel.setData(self.itemModel.index(i, 0), 
                                           QtGui.QApplication.translate("ImportChooser", 
                                                     "There was a error importing this serie", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8), 
                                           QtCore.Qt.ToolTipRole)
                    self.itemModel.setData(self.itemModel.index(i, 0), icon, QtCore.Qt.DecorationRole)
                elif serie["exists"]:
                    self._warning = True
                    icon.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/dialog-warning.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                    self.itemModel.setData(self.itemModel.index(i, 0), 
                                           QtGui.QApplication.translate("ImportChooser", 
                                                     "This serie already exists in database.\nIf you import all data will be lost.\nRename the serie to import it  separately", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8), 
                                           QtCore.Qt.ToolTipRole)
                    self.itemModel.setData(self.itemModel.index(i, 0), icon, QtCore.Qt.DecorationRole)
                else:
                    icon.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/dialog-ok-apply.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                    self.itemModel.setData(self.itemModel.index(i, 0), 
                                           QtGui.QApplication.translate("ImportChooser", 
                                                     "This serie is ready to be importer", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8), 
                                           QtCore.Qt.ToolTipRole)
                    self.itemModel.setData(self.itemModel.index(i, 0), icon, QtCore.Qt.DecorationRole)
                self.itemModel.setData(self.itemModel.index(i, 1),  checked, QtCore.Qt.CheckStateRole)
                self.itemModel.setData(self.itemModel.index(i, 2), serie["progress"])
                self.itemModel.setData(self.itemModel.index(i, 3), serie["patientName"])
                self.itemModel.setData(self.itemModel.index(i, 4), serie["serieDescription"])
                self.itemModel.setData(self.itemModel.index(i, 5), len(serie["files"]))
                self.itemModel.setData(self.itemModel.index(i, 6), serie["uid"])
                self.tableView.repaint()


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    win = ImportChooser()
    win.show()
    sys.exit(app.exec_())