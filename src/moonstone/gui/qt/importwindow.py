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
import yaml
import sys
import datetime

from ...utils import profile as profile

from PySide import QtCore, QtGui

from .widget.importwindow_ui import Ui_ImportWindow
from ...utils import constant
from ...utils import utils
from ...utils.strUtils import hashStr
from ...bloodstone.importer.database.patient import Patient
from ...bloodstone.importer.database.serie import Serie
from ...bloodstone.importer.database.study import Study
from ...bloodstone.importer.serieexporter import SerieExporter
from ...bloodstone.utils.data import reader_vti, reader_to_imagedata
from component.vtkimageview import VTKImageView
from importsearch import ImportSearch
from delete import Delete
from reset import Reset
from rename import Rename
import shutil


class ImportWindow(QtGui.QWidget, Ui_ImportWindow):

    def __init__(self, parent=None):
        logging.debug("In ImportWindow::__init__()")
        super(ImportWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(constant.TITLE_PROGRAM)
        self.createComponents()
        self.createSignals()
        self.importSearch = ImportSearch()
        self.createActions()
        self.filters = []
        self.createPreviews()
        self.updateTree()
        self.series = []
        self._contextMenuProviders = []
        
    def createComponents(self):
        logging.debug("In ImportWindow::createComponents()")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/dialog-close.png"))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/document-export.png"))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/clear.png"))
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/im-status-message-edit.png"))
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/edit-paste.png"))
        self.deleteAction = QtGui.QAction(self)
        self.deleteAction.setText(QtGui.QApplication.translate(
                    "ImportWindow", "Delete",
                    None, QtGui.QApplication.UnicodeUTF8))
        self.deleteAction.setIconVisibleInMenu(True)
        self.deleteAction.setObjectName("deleteAction")
        self.deleteAction.setIcon(icon1)
        self.exportAction = QtGui.QAction(self)
        self.exportAction.setText(QtGui.QApplication.translate(
                    "ImportWindow", "Export",
                    None, QtGui.QApplication.UnicodeUTF8))
        self.exportAction.setIconVisibleInMenu(True)
        self.exportAction.setObjectName("exportAction")
        self.exportAction.setIcon(icon2)
        self.resetAction = QtGui.QAction(self)
        self.resetAction.setText(QtGui.QApplication.translate(
                    "ImportWindow", "Reset",
                    None, QtGui.QApplication.UnicodeUTF8))
        self.resetAction.setIconVisibleInMenu(True)
        self.resetAction.setObjectName("resetAction")
        self.resetAction.setIcon(icon3)
        self.duplicateSerieAction = QtGui.QAction(self)
        self.duplicateSerieAction.setText(QtGui.QApplication.translate(
                    "ImportWindow", "Duplicate",
                    None, QtGui.QApplication.UnicodeUTF8))
        self.duplicateSerieAction.setIconVisibleInMenu(True)
        self.duplicateSerieAction.setObjectName("resetAction")
        self.duplicateSerieAction.setIcon(icon5)
        self.renameSerieAction = QtGui.QAction(self)
        self.renameSerieAction.setText(QtGui.QApplication.translate(
                    "ImportWindow", "Rename",
                    None, QtGui.QApplication.UnicodeUTF8))
        self.renameSerieAction.setIconVisibleInMenu(True)
        self.renameSerieAction.setObjectName("resetAction")
        self.renameSerieAction.setIcon(icon4)
        self.treeMenu = QtGui.QMenu(self.treeWidget)
        
        self.rename = Rename(self)
        
#        self.treeMenu.addAction(self.deleteAction)
#        self.treeMenu.addAction(self.exportAction)
#        self.treeMenu.addAction(self.resetAction)
        self.treeMenu.setIcon(icon1)
        
    def createActions(self):
        logging.debug("In ImportWindow::createActions()")
        self.treeWidget.contextMenuEvent = self.treeContextEvent
        self.connect(self.treeWidget,
                     QtCore.SIGNAL("itemClicked(QTreeWidgetItem*, int)"),
                     self.slotTreeWidgetClicked)
        self.connect(self.treeWidget,
                     QtCore.SIGNAL("itemEntered (QTreeWidgetItem*, int)"),
                     self.slotTreeWidgetClicked)
        self.connect(self.splitter,
                     QtCore.SIGNAL("splitterMoved(int, int)"),
                     self.slotHSplit)
        self.connect(self.horizontalSlider,
                     QtCore.SIGNAL("valueChanged(int)"),
                     self.slotSliderMoved)
        self.connect(self.spinBox,
                     QtCore.SIGNAL("valueChanged(int)"),
                     self.slotSpinChanged)
        self.connect(self.importButton, QtCore.SIGNAL("clicked()"),
                     self.slotImportClicked)
        self.connect(self.treeWidget,
                     QtCore.SIGNAL("itemExpanded(QTreeWidgetItem*)"),
                     self.slotTreeWidgetExpanded)
        self.connect(self.treeWidget,
                     QtCore.SIGNAL("itemCollapsed(QTreeWidgetItem*)"),
                     self.slotTreeWidgetExpanded)
        self.connect(self.searchButton, QtCore.SIGNAL("clicked()"),
                     self.slotSearchButtonClicked)
        self.connect(self.searchText, QtCore.SIGNAL(
                      "textChanged ( QString)"),
                      self.slotSearchTextChanged)
        self.connect(self.importSearch.searchButton, QtCore.SIGNAL("clicked()"),
                     self.slotImportSearchButtonClicked)
        self.connect(self.importSearch.cancelButton, QtCore.SIGNAL("clicked()"),
                     self.slotImportCancelButtonClicked)
        self.connect(self.resetButton, QtCore.SIGNAL("clicked()"),
                     self.slotResetButtonClicked)
        self.connect(self.rename.Ok, QtCore.SIGNAL("clicked()"),
                     self.slotRenameOkButtonClicked)
        self.connect(self.rename.Cancel, QtCore.SIGNAL("clicked()"),
                     self.slotRenameCancelButtonClicked)
    
    def slotRenameOkButtonClicked(self):
        description =  utils.decode_string(self.rename.newName.text())
        id = self.rename.serie.uid
        if list(Serie.select("uid='{0}' AND description='{1}'".format(id, description))):
            QtGui.QMessageBox.critical(self.rename, "Error", 
                        QtGui.QApplication.translate(
                                    "ImportWindow", 
                                    "This serie is already registered in database with this name. \nTry another one.",
                    None, QtGui.QApplication.UnicodeUTF8))
        else:
            if self.rename.action == self.renameSerieAction:
                print hashStr(self.rename.serie.study.patient.uid)
                basePath = os.path.join(constant.INSTALL_DIR, "data")
                patientPath = os.path.join(basePath, hashStr(self.rename.serie.study.patient.uid))
                oldSeriePath = os.path.join(patientPath,"{0}{1}".format(hashStr(self.rename.serie.uid), hashStr(self.rename.serie.description)))
                filePath = file(os.path.join(oldSeriePath
                                    , "{0}{1}".format(hashStr(self.rename.serie.uid),".yaml")), 'r')
                vti = yaml.load(filePath)
                vti["vti"] = vti["vti"].replace("{0}{1}".format(hashStr(self.rename.serie.uid), hashStr(self.rename.serie.description)), 
                                                "{0}{1}".format(hashStr(self.rename.serie.uid), hashStr(description)))
                
                filePath.close()
                filePath = file(os.path.join(oldSeriePath
                                    , "{0}{1}".format(hashStr(self.rename.serie.uid),".yaml")), 'w')
                yaml.dump(vti, filePath)
                filePath.close()
                self.rename.serie.description = description.encode("utf-8")
                self.rename.serie.file = os.path.join("{0}{1}".format(hashStr(self.rename.serie.uid), hashStr(description))
                                    , "{0}{1}".format(hashStr(self.rename.serie.uid),".yaml"))
                newSeriePath = os.path.join(patientPath,"{0}{1}".format(hashStr(self.rename.serie.uid), hashStr(description)))
                if os.path.exists(newSeriePath):
                    shutil.rmtree(newSeriePath)  
                shutil.move(oldSeriePath, newSeriePath)
                self.rename.hide()
                self.updateTree()
            else:
                #copy files to new directory
                basePath = os.path.join(constant.INSTALL_DIR, "data")
                patientPath = os.path.join(basePath, hashStr(self.rename.serie.study.patient.uid))
                oldSeriePath = os.path.join(patientPath,"{0}{1}".format(hashStr(self.rename.serie.uid), hashStr(self.rename.serie.description)))
                newSeriePath = os.path.join(patientPath,"{0}{1}".format(hashStr(self.rename.serie.uid), hashStr(description)))
                if os.path.exists(newSeriePath):
                    shutil.rmtree(newSeriePath)  
                shutil.copytree(oldSeriePath, newSeriePath)
                yamlFile = os.path.join("{0}{1}".format(hashStr(self.rename.serie.uid), hashStr(description))
                                    , "{0}{1}".format(hashStr(self.rename.serie.uid),".yaml"))
                
                filePath = file(os.path.join(newSeriePath
                                    , "{0}{1}".format(hashStr(self.rename.serie.uid),".yaml")), 'r')
                vti = yaml.load(filePath)
                vti["vti"] = vti["vti"].replace("{0}{1}".format(hashStr(self.rename.serie.uid), hashStr(self.rename.serie.description)), 
                                                "{0}{1}".format(hashStr(self.rename.serie.uid), hashStr(description)))
                
                filePath.close()
                filePath = file(os.path.join(newSeriePath
                                    , "{0}{1}".format(hashStr(self.rename.serie.uid),".yaml")), 'w')
                yaml.dump(vti, filePath)
                filePath.close()
                #create new serie
                Serie(uid=self.rename.serie.uid, 
                      file=yamlFile,
                      description=description,
                      thickness=self.rename.serie.thickness, 
                      size=self.rename.serie.size,   
                      zSpacing=self.rename.serie.zSpacing,
                      tmp = False,
                      dicomImages=self.rename.serie.dicomImages,
                      study=self.rename.serie.study)
                self.rename.hide()
                self.updateTree()
    
    def slotRenameCancelButtonClicked(self):
        self.rename.hide()

    def createSignals(self):
        logging.debug("In ImportWindow::createSignals()")
        self.confirmImportSignal = QtCore.SIGNAL(
                            "importConfirmed(PyObject, PyObject, PyObject)")

    def createPreviews(self):
        logging.debug("In ImportWindow::createPreviews()")
        imageLayout = QtGui.QGridLayout(self.imageViewWidget)
        self.image = VTKImageView(self.imageViewWidget)
        self.selectedNumber = -1
        imageLayout.addWidget(self.image)
        self.previewWidgets = []
        self.previewWidgetsMap = {}
         
    def imageClicked(self,obj, evt):
        logging.debug("In ImportWindow::imageClicked()")
        self.preview(self.previewWidgetsMap[obj])

    def preview(self, preview):
        logging.debug("In ImportWindow::preview()")
        backgroundColor = self.palette().color(self.palette().Highlight)
        color = self.palette().color(self.palette().HighlightedText)
        preview.setStyleSheet(
              " background-color : rgb(" + str(backgroundColor.red()) + ","
              + str(backgroundColor.green()) + "," + str(backgroundColor.blue())
              + ");" + "color : rgb(" + str(color.red()) + ","
              + str(color.green()) + "," + str(color.blue()) + ");")

        dicomPath = preview.getImagePath()
        self.imageTabWidget.setTabText(0,QtGui.QApplication.translate(
                    "ImportWindow", "image ",
                    None, QtGui.QApplication.UnicodeUTF8)+preview.getText())
        self.image.setImagePath(dicomPath)
        for i,currentPreview in enumerate(self.previewWidgets):
            if currentPreview == preview:
                self.selectedNumber = i
                continue
            currentPreview.setStyleSheet("")
        self.horizontalSlider.setSliderPosition(self.selectedNumber)
    

    def setSliderRange(self, minRange, maxRange):
        logging.debug("In ImportWindow::setSliderRange()")
        self.horizontalSlider.setRange(minRange, maxRange)

    def removeAllItems(self):
        logging.debug("In ImportWindow::removeAllItems()")
        self.treeWidget.clear()

    def updateTree(self, qtd=0):
        logging.debug("In ImportWindow::updateTree()")
        self.seriesDictionary = {}
        patients = Patient.findContaining(self.importSearch.patientName.text())
        self.removeAllItems()
        for patient in patients:
            item = QtGui.QTreeWidgetItem(self.treeWidget)
            if patient.sex:
                item.setText(1, patient.sex)
            if patient.birthdate:
                age = (datetime.datetime.now().toordinal() -patient.birthdate.toordinal()) / 365
                item.setText(2, "{0}".format(age))
                item.setText(6, patient.birthdate.isoformat())
            self.seriesDictionary[item] = patient                   
            studies = Study.findContaining(patient=patient,
                                           description=self.importSearch.studyDescription.text(),
                                           modality=self.importSearch.modality.text(),
                                           institution= self.importSearch.institution.text())
            item.setText(0, QtGui.QApplication.translate(
                    "ImportWindow", "Patient: {0} ({1} studies)",
                    None, QtGui.QApplication.UnicodeUTF8).format(patient.name, len(studies)))
            totalPatientImages = 0 
            for study in studies:
                studyItem = QtGui.QTreeWidgetItem(item)
                if study.modality:
                    studyItem.setText(3, study.modality)
                if study.institution:
                    studyItem.setText(5, study.institution)
                
                self.seriesDictionary[studyItem] = study    
                series = Serie.findContaining(study=study, description=self.importSearch.serieDescription.text())
                
                if not series:
                    item.removeChild(studyItem)
                    self.seriesDictionary.pop(studyItem)
                if study.description:
                    studyItem.setText(0, QtGui.QApplication.translate(
                    "ImportWindow", "Study: {0}  ({1} series)",
                    None, QtGui.QApplication.UnicodeUTF8).format(study.description, len(series)))
                else:
                    studyItem.setText(0, QtGui.QApplication.translate(
                    "ImportWindow", "Study: ({0} series)",
                    None, QtGui.QApplication.UnicodeUTF8).format(len(series)))
                
                totalStudyImages = 0
                for serie in series:
                    serieItem = QtGui.QTreeWidgetItem(studyItem)
                    serieItem.setText(0,QtGui.QApplication.translate(
                                         "ImportWindow", "Serie: {0}({1} images)",
                                         None, 
                                         QtGui.QApplication.UnicodeUTF8).format(
                                                            serie.description, serie.dicomImages))
                    serieItem.setText(4,"{0}".format(serie.dicomImages))
                    self.seriesDictionary[serieItem] = serie
                    totalStudyImages = totalStudyImages + serie.dicomImages
                studyItem.setText(4,"{0}".format(totalStudyImages))
                totalPatientImages = totalPatientImages + totalStudyImages
            
            item.setText(4,"{0}".format(totalPatientImages))
                    
            if item.childCount() == 0:
                self.treeWidget.takeTopLevelItem(self.treeWidget.topLevelItemCount()-1)
                self.seriesDictionary.pop(item)
        self.resizeTreeColumns()
        
    def slotHSplit(self, pos, index):
        logging.debug("In ImportWindow::slotHSplit()")
        self.organizePreviews()
        
    def createItemFromSerie(self, serie, parent):
        logging.debug("In ImportWindow::createItemFromSerie()")
        item = QtGui.QTreeWidgetItem(parent)
        item.setText(0, serie.firstDicom.seriesDescription+"("+
                     serie.getSerieLengthString()+")")
        for subSerie in serie.getSubSeries().values():
            self.createItemFromSerie(subSerie, item)

        self.seriesDictionary[item] = serie
        return item

    def normalizeSizeWidget(self):
        logging.debug("In ImportWindow::normalizeSizeWidget()")        
        self.splitter.setSizes([6000,4000])

    def slotCancel(self):
        logging.debug("In ImportWindow::slotCancel()")
        self.series = []
        self.seriesDictionary = {}
        self.close()
        self.parentWidget().close()

    def slotTreeWidgetClicked(self, item, column):
        logging.debug("In ImportWindow::slotTreeWidgetClicked()")
        try:
            self.series = []
            if isinstance(self.seriesDictionary[item], Patient) :
                for study in self.seriesDictionary[item].studies:
                    for serie in study.series:
                        self.series.append(serie)
            elif isinstance(self.seriesDictionary[item], Study) :
                for serie in self.seriesDictionary[item].series:
                    self.series.append(serie)
            elif isinstance(self.seriesDictionary[item], Serie) :
                self.series.append(self.seriesDictionary[item])     
            self.showPreview()
        except Exception as e:
            print e
            print self.seriesDictionary
            print item
            print Patient
            print self.seriesDictionary[item]
            print isinstance(self.seriesDictionary[item], Patient)
            
    def deleteActionExec(self, window, item):
        msg = QtGui.QMessageBox()
        msg.setText(QtGui.QApplication.translate("ImportWindow",
                                 "Are you sure you want to delete selected item?",
                                 None, 
                                 QtGui.QApplication.UnicodeUTF8))
        msg.setStandardButtons(msg.No | msg.Yes)
        msg.setDefaultButton(msg.No)
        msg.show()
        msgResult = msg.exec_()
        if msgResult == msg.Yes:
            self.delete = Delete(self)
            self.delete.show()
            self.delete.normalizeSizeWidget()
            self.connect(self.delete, QtCore.SIGNAL("deleteFinished()"), self.deleteFinished)
            self.delete.processDelete(series = self.getSeriesFromItem(item))
            
    def exportActionExec(self, window, item):
        lastdir = "{0}{1}{2}".format(profile.get_last_directory_action_new(), os.path.sep, "exporter.st")
        caption = QtGui.QApplication.translate(
            "ImportWindow", "Select the output directory", None,
            QtGui.QApplication.UnicodeUTF8)
        file = "{0}{1}{2}".format(lastdir, os.path.sep, "Export.st") 
        dialog = QtGui.QFileDialog.getSaveFileName(self, caption, lastdir, "File (*.st)")
        if dialog[0]:
            outputDirectory = os.path.abspath(dialog[0])
            msg = QtGui.QMessageBox()
            msg.setText(QtGui.QApplication.translate(
                                "ImportWindow", "Would you like to export Dicom Images?", None,
                                QtGui.QApplication.UnicodeUTF8))
            msg.setStandardButtons(msg.No | msg.Yes)
            msg.setDefaultButton(msg.No)
            msg.show()
            dicomImages = msg.exec_() == msg.Yes
            series = self.getSeriesFromItem(item)
            exporter = SerieExporter(self, outputDirectory, series, dicomImages)
            exporter.start()
            
    def resetActionExec(self, window, item):
        msg = QtGui.QMessageBox()
        msg.setText(QtGui.QApplication.translate(
                                "ImportWindow", "Are you sure you want to reset selected serie?", None,
                                QtGui.QApplication.UnicodeUTF8))
        msg.setStandardButtons(msg.No | msg.Yes)
        msg.setDefaultButton(msg.No)
        msg.show()
        msgResult = msg.exec_()
        if msgResult == msg.Yes:
            series = self.getSeriesFromItem(item)
            reset = Reset(self)
            reset.processReset(series[0])
            
    def duplicateSerieActionExec(self, window, item):
        self.rename.action = self.duplicateSerieAction
        self.rename.setWindowTitle(QtGui.QApplication.translate(
                                "ImportWindow", "Duplicate Serie:", None,
                                QtGui.QApplication.UnicodeUTF8))
        self.rename.label.setText(QtGui.QApplication.translate(
                                "ImportWindow", "New Serie Description:", None,
                                QtGui.QApplication.UnicodeUTF8))
        self.rename.serie = self.getSeriesFromItem(item)[0]
        self.rename.setWindowIcon(self.duplicateSerieAction.icon())
        self.rename.newName.setText(self.rename.serie.description)
        self.rename.show()
    
    def renameSerieActionExec(self, window, item):
        self.rename.serie = self.getSeriesFromItem(item)[0]
        self.rename.setWindowTitle(QtGui.QApplication.translate(
                                "ImportWindow", "Rename Serie", None,
                                QtGui.QApplication.UnicodeUTF8))
        self.rename.label.setText(QtGui.QApplication.translate(
                                "ImportWindow", "Description:", None,
                                QtGui.QApplication.UnicodeUTF8))
        self.rename.setWindowIcon(self.renameSerieAction.icon())
        self.rename.action = self.renameSerieAction
        self.rename.newName.setText(self.rename.serie.description)
        self.rename.show()
        
    def getTreeContextMenuActions(self, window, item):
        result = []
        if item:
            result.append((self.deleteAction, self.deleteActionExec))
            result.append((self.exportAction, self.exportActionExec))
            if isinstance(self.seriesDictionary[item], Serie):
                result.append((self.resetAction, self.resetActionExec))
                result.append((self.duplicateSerieAction, self.duplicateSerieActionExec))
                result.append((self.renameSerieAction, self.renameSerieActionExec))
        for provider in self._contextMenuProviders:
            actions = provider(window, item)
            if actions:
                result = result + actions
        return result
        
    def treeContextEvent(self, event):
        logging.debug("In ImportWindow::treeContextEvent()")
        item = self.treeWidget.itemAt(event.pos())
        if item:
            actions = self.getTreeContextMenuActions(self, item)
            self.treeMenu.clear()
            for action, callback in actions:
                self.treeMenu.addAction(action)
            result = self.treeMenu.exec_(QtGui.QCursor.pos())
            if result:
                for action, callback in actions:
                    if action == result:
                        callback(self, item)
                        break
                    
                    
    def getSeriesFromItem(self, item):
        series = []
        if isinstance(self.seriesDictionary[item], Patient) :
            for study in self.seriesDictionary[item].studies:
                for serie in study.series:
                    series.append(serie)
        elif isinstance(self.seriesDictionary[item], Study) :
            for serie in self.seriesDictionary[item].series:
                series.append(serie)
        elif isinstance(self.seriesDictionary[item], Serie) :
            series.append(self.seriesDictionary[item])
        return series 
    
    def deleteFinished(self):
        self.updateTree()
        self.image.setImage(None)
        self.image.removeAllTexts()
        self.setSliderRange(0, 0)
           
    def slotTreeWidgetExpanded(self, item):
        logging.debug("In ImportWindow::slotTreeWidgetExpanded()")
        self.resizeTreeColumns()
    
    def resizeTreeColumns(self):
        logging.debug("In ImportWindow::resizeTreeColumns()")
        for i in range(self.treeWidget.columnCount()):
            self.treeWidget.resizeColumnToContents(i)

    def cleanPreviewWidgets(self):
        logging.debug("In ImportWindow::cleanPreviewWidgets()")
        for preview in self.previewWidgets:
            self.removePreview(preview)
        self.previewWidgets = []
        self.previewWidgetsMap = {}

    def removePreview(self, preview):
        logging.debug("In ImportWindow::removePreview()")
        preview.close()

    def showPreview(self):
        logging.debug("In ImportWindow::showPreview()")
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(len(self.series))
        folder = os.path.join(self.series[self.spinBox.value()-1].study.patient.directory, "{0}/images/".format(hashStr(self.series[self.spinBox.value()-1].uid)))
        files = os.listdir(folder)
        minRange = sys.maxint
        maxRange = 0 
        for f in files:
            try:
                value = int (f[:-4])
                minRange = min(minRange, value)
                maxRange = max(maxRange, value)
            except:
                pass

        self.setSliderRange(minRange, maxRange)
        
        self.horizontalSlider.setValue(minRange)
        self.slotSliderMoved(minRange)
        self.image.removeAllTexts()
        self.image.addText(self.series[self.spinBox.value()-1].study.patient.name, y=0.10)
        self.image.addText(self.series[self.spinBox.value()-1].description, y=0.05)
   
    
    def organizePreviews(self):
        logging.debug("In ImportWindow::organizePreviews()")
        if self.previewWidgets:
            w = self.previewWidgets[0].width()
            h = self.previewWidgets[0].height()
            n = len(self.previewWidgets)
            lines = int(self.scrollArea.width()/w)
            if lines:
                columns = (n/lines)+1
                self.previewWidget.resize(self.scrollArea.width(),columns*h)
                i = 0
                j=-1
                for preview in self.previewWidgets:
                    if i%lines == 0:
                        j = j+1
                    preview.setGeometry((i%lines)*w, j*h, w, h)
                    preview.update()
                    i = i+1

    def slotSliderMoved(self, i):
        logging.debug("In ImportWindow::slotSliderMoved()")
        try:
            self.image.setImage(os.path.join(self.series[self.spinBox.value()-1].study.patient.directory, "{0}/images/{1}.dcm".format(hashStr(self.series[self.spinBox.value()-1].uid), i)))
        except:
            pass
    
    def slotSpinChanged(self, i):
        logging.debug("In ImportWindow::slotSpinChanged()")
        self.showPreview()
    
    def slotSearchButtonClicked(self):
        logging.debug("In ImportWindow::slotSearchButtonClicked()")
        self.importSearch.show()
    
    def slotSearchTextChanged(self):
        logging.debug("In ImportWindow::slotSearchTextChanged()")
        self.importSearch.clearFields()
        self.importSearch.patientName.setText(self.searchText.text())
        self.updateTree()
    
    def slotImportSearchButtonClicked(self):
        logging.debug("In ImportWindow::slotImportSearchButtonClicked()")
        self.importSearch.hide()
        self.updateTree()
    
    def slotImportCancelButtonClicked(self):
        logging.debug("In ImportWindow::slotImportCancelButtonClicked()")
        self.importSearch.hide()

    def slotResetButtonClicked(self):
        logging.debug("In ImportWindow::slotImportCancelButtonClicked()")
        self.importSearch.clearFields()
        self.searchText.setText("")
        self.updateTree()

    def slotImportClicked(self):
        logging.debug("In ImportWindow::slotImportClicked()")
        curr = self.seriesDictionary.get(self.treeWidget.currentItem())
        if curr:
            series = []
            if isinstance(curr, Patient):
                for study in curr.studies:
                    for serie in study.series:
                        series.append(serie)
            elif isinstance(curr, Study):
                for serie in curr.series:
                    series.append(serie)
            elif isinstance(curr, Serie):
                series.append(curr)
            else:
                logging.warning("Is not instance of: (Patient, Study, Serie)")
                raise Exception("Is not instance of: (Patient, Study, Serie)")
            self.emit(self.confirmImportSignal, series, 
                      self.qualityComboBox.currentIndex(), self.generate3DCheckbox.isChecked())
        else:
            logging.warning("There's no dicom to be importer =(")
            raise Exception("There's no dicom to be importer =(")
        
    def addContextMenuProvider(self, provider):
        self._contextMenuProviders.append(provider)
    
    def removeContextMenuProvider(self, provider):
        if self._contextMenuProviders.count(provider):
            self._contextMenuProviders.remove(provider)
    