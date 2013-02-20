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

from PySide import QtCore, QtGui
from .widget.hounsfieldEditor_ui import Ui_HounsfieldEditor
from ...bloodstone.utils.data import load_yaml_file, persist_yaml_file
from ...utils.constant import HOUNSFIELD_FILE_PATH
import copy
from tfwidget import TransferFunctionView
import logging

class HounsfieldEditor(QtGui.QFrame, Ui_HounsfieldEditor):

    def __init__(self, parent, hounsfieldBase, imagedata):

        super(HounsfieldEditor, self).__init__(parent, QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)

        self.parentWindow = parent
        self.setupUi(self)
        self.loadHounsFieldScales()
        self.createDefaultTypeProperties()
        self.createWidgets()
        self.createActions()

        for i in range(self.scalesCombo.count()):

            if self.scalesCombo.itemText(i) == hounsfieldBase:

                self.scalesCombo.setCurrentIndex(i)
                self.setHounsfieldScale(self.scalesCombo.itemData(i))

                break
           
    def loadHounsFieldScales(self):

        self.hounsfieldScales = load_yaml_file(HOUNSFIELD_FILE_PATH)
    
    def saveHounsFieldScales(self):

        persist_yaml_file(HOUNSFIELD_FILE_PATH, self.hounsfieldScales)
    
    def createWidgets(self):

        for scale in self.hounsfieldScales:

            self.scalesCombo.addItem(scale["name"], scale)

        for types in self.defaultTypeProperties:

            self.typeCombo.addItem(types["name"], types)

        self.cancelButton.setVisible(False)
        self.opacityLayout = QtGui.QVBoxLayout()
        self.visualPoints = None
        self.colorLayout = QtGui.QVBoxLayout()
        self.visualColorSegments = None
        self.segment = None

        self.__tfView = TransferFunctionView()
        self.__tfView.loadHounsfieldScale( scale )
        self.verticalLayout_4.addWidget( self.__tfView )
        
    def close(self):

        if self.segment:
            self.segment.close()
        super(HounsfieldEditor, self).close()
        
    def createActions( self ):

        self.connect( self.newScaleButton, QtCore.SIGNAL("clicked()"),
                     self.slotNewScaleClicked )
        self.connect( self.deleteScaleButton, QtCore.SIGNAL("clicked()"),
                     self.slotDeleteScaleClicked )
        self.connect( self.saveButton, QtCore.SIGNAL("clicked()"),
                     self.slotSaveClicked )
        self.connect( self.okButton, QtCore.SIGNAL("clicked()"),
                      self.close )
        self.connect( self.cancelButton, QtCore.SIGNAL("clicked()"),
                     self.slotCancelClicked )
        self.connect( self.scalesCombo, QtCore.SIGNAL("currentIndexChanged(int)"),
                      self.scalesComboChange )
        self.connect( self.typeCombo, QtCore.SIGNAL("currentIndexChanged(int)"),
                      self.typeComboChange )

        #self.__tfView.getTransferFunction().addTransferFunctionChangeListener( self )
        self.__tfView.addTransferViewListener( self )

    def scalesComboChange( self ):

        scalesComboIndex = self.scalesCombo.currentIndex()
        if scalesComboIndex >= 0:
            self.setHounsfieldScale(self.scalesCombo.itemData(scalesComboIndex))
            
    def typeComboChange(self):

        prop = self.typeCombo.itemData(self.typeCombo.currentIndex())
        self.mapperProperties = prop["mapper_properties"]
        self.volumeProperties = prop["volume_properties"]
        self.preview()
        
    def slotDeleteScaleClicked(self):

        msg = QtGui.QMessageBox()
        msg.setText(QtGui.QApplication.translate("HounsfieldEditor", "Are you sure you want to delete selected item?", None, QtGui.QApplication.UnicodeUTF8))
        msg.setStandardButtons(msg.No | msg.Yes)
        msg.setDefaultButton(msg.No)
        msg.show()
        msgResult = msg.exec_()
        if msgResult == msg.Yes:
            index = self.scalesCombo.currentIndex()
            self.scalesCombo.removeItem(index)
            self.hounsfieldScales.remove(self.hounsfieldScales[index])
            self.saveHounsFieldScales()
            self.parentWindow.loadHounsFieldScales()
            self.preview()        
    
    def slotNewScaleClicked(self):
        text, ok = QtGui.QInputDialog.getText(self, QtGui.QApplication.translate("HounsfieldEditor", 
                                                     "New Scale", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8), 
                                                     QtGui.QApplication.translate("HounsfieldEditor", 
                                                     "Name:", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8))
        if ok:

            if self.checkUniqueName(text):
                scalesComboIndex = self.scalesCombo.currentIndex()
                if scalesComboIndex >= 0:
                    scale = copy.deepcopy(self.hounsfieldScales[scalesComboIndex])
                    if scale.has_key("permanent"):
                        scale.pop("permanent")
                else:
                    scale = {'mapper_properties': {'blend_mode_to_maximum_intensity': True}, 'color_points': [[{'x': 0.0, 'r': 0.0, 'b': 0.0, 'g': 0.0}, {'x': 1.0, 'r': 1.0, 'b': 1.0, 'g': 1.0}]], 'volume_properties': {'shade': False}, 'name': "Mip", 'opacity_points': [{'y': 0.0, 'x': 0.0}, {'y': 1.0, 'x': 1.0}]}
                scale["name"] = text                    
                self.scalesCombo.addItem(text, scale)
                self.newScaleButton.setVisible(False)
                self.deleteScaleButton.setVisible(False)
                self.cancelButton.setVisible(True)
                self.scalesCombo.setCurrentIndex(self.scalesCombo.count() -1 )
                self.scalesCombo.setEnabled(False)                
                self.saveButton.setEnabled(True)
                self.deleteScaleButton.setEnabled(True)

            else:

                msgBox = QtGui.QMessageBox()
                msgBox.setText(QtGui.QApplication.translate("HounsfieldEditor", "Name already exist!", None, QtGui.QApplication.UnicodeUTF8))
                msgBox.exec_()
                
    def checkUniqueName( self, name ):

        for scale in self.hounsfieldScales:
            if scale["name"] == name:
                return False
        return True
    
    def slotCancelClicked( self ):

        index = self.scalesCombo.currentIndex()
        self.scalesCombo.setCurrentIndex(0)
        self.scalesCombo.setEnabled(True)
        self.scalesCombo.removeItem(index)
        self.newScaleButton.setVisible(True)
        self.deleteScaleButton.setVisible(True)
        self.cancelButton.setVisible(False)
   
    def preview(self):

        self.parentWindow.setHounsfieldScalePreview(self.getCurrentScaleValue())

    def slotSaveClicked(self):

        value =  self.getCurrentScaleValue()
        if len(self.hounsfieldScales) < self.scalesCombo.count():
            self.hounsfieldScales.append(value)
        else:
            self.hounsfieldScales[self.scalesCombo.currentIndex()] = value
        self.scalesCombo.setItemData(self.scalesCombo.currentIndex(), value)
        self.saveHounsFieldScales()
        self.scalesCombo.setEnabled(True)
        self.newScaleButton.setVisible(True)
        self.deleteScaleButton.setVisible(True)
        self.cancelButton.setVisible(False)
        self.parentWindow.loadHounsFieldScales()
        msgBox = QtGui.QMessageBox()
        msgBox.setText(QtGui.QApplication.translate("HounsfieldEditor", "Hounsfield scale saved successfully!", None, QtGui.QApplication.UnicodeUTF8))
        msgBox.exec_()
        name = value["name"]
        for i in range(self.scalesCombo.count()):
            if self.scalesCombo.itemText(i) == name:
                self.scalesCombo.setCurrentIndex(i)
                self.setHounsfieldScale(self.scalesCombo.itemData(i))   
    
    def getCurrentScaleValue(self):

        result = self.scalesCombo.itemData(self.scalesCombo.currentIndex())
        result["opacity_points"] = self.__tfView.getOpacityPoints()
        result["color_points"] = self.__tfView.getColorPoints()
        result["mapper_properties"] = self.getMapperProperties()
        result["volume_properties"] = self.getVolumeProperties()
        result["default_window"] = self.parentWindow.getActualWindow()
        result["default_level"] = self.parentWindow.getActualLevel()

        return result
    
    def getMapperProperties( self ):

        return self.mapperProperties

    def getVolumeProperties( self ):

        return self.volumeProperties
        
    def setHounsfieldScale( self, scale ):

        mapperProperties = {}
        self.parentWindow.changeHounsfieldMode(scale["name"])
        if scale.has_key("mapper_properties"):
            mapperProperties = scale["mapper_properties"]
        volumeProperties = {}
        if scale.has_key("volume_properties"):
            volumeProperties = scale["volume_properties"]
        opacityPoints = []
        if scale.has_key("opacity_points"):
            opacityPoints = scale["opacity_points"]
        colorSegments = []
        if scale.has_key("color_points"):
            colorSegments = scale["color_points"]
        self.setTypeByProperties( mapperProperties, volumeProperties )

        window = 4095.0
        if scale.has_key("default_window"):

            window = scale["default_window"]

        level = 1047.5
        if scale.has_key("default_level"):

            level = scale["default_level"]
        self.parentWindow.setWindowLevel( window, level )

        if scale.has_key("permanent") and scale["permanent"]:

            self.saveButton.setEnabled(False)
            self.deleteScaleButton.setEnabled(False)

        else:

            self.saveButton.setEnabled(True)
            self.deleteScaleButton.setEnabled(True)

        self.__tfView.loadHounsfieldScale( scale )
        self.preview()
    
    def setTypeByProperties(self, mapperProperties, volumeProperties):

        result = len(self.defaultTypeProperties) -1
        i = 0
        for type in self.defaultTypeProperties:
            if mapperProperties == type["mapper_properties"] and volumeProperties == type["volume_properties"]:
                result = i
                break
            i = i +1
        self.typeCombo.setCurrentIndex(result)
        self.mapperProperties = mapperProperties
        self.volumeProperties = volumeProperties
    
    def createDefaultTypeProperties( self ):

        normalVolumeProperties = {"shade": False}
        normalMapperProperties = {"blend_mode_to_maximum_intensity": True}
        
        shadeVolumeProperties = {"shade": True}
        shadelMapperProperties = {"blend_mode_to_composite": True}
        
        compositeVolumeProperties = {"shade": False}
        compositeMapperProperties = {"blend_mode_to_composite": True}
        
        customVolumeProperties = {"ambient": 0.1, "difuse": 0.9, "scalar_opacity_unit_distance": 0.8919,
                                  "shade": True, "specular": 0.2, "specular_power": 10.0}
        customMapperProperties = {"blend_mode_to_composite": True}
        
        self.defaultTypeProperties = []
        self.defaultTypeProperties.append({"name" : "Normal", "mapper_properties" : normalMapperProperties, "volume_properties" : normalVolumeProperties})
        self.defaultTypeProperties.append({"name" : "Shade", "mapper_properties" : shadelMapperProperties, "volume_properties" : shadeVolumeProperties})
        self.defaultTypeProperties.append({"name" : "Composite", "mapper_properties" : compositeMapperProperties, "volume_properties" : compositeVolumeProperties})
        self.defaultTypeProperties.append({"name" : "Custom", "mapper_properties" : customMapperProperties, "volume_properties" : customVolumeProperties})

    def onTransferFunctionPointInserted( self ):

        logging.debug( "HounsfieldEditor::onTransferFunctionPointInserted" )

        self.preview()

    def onTransferFunctionPointRemoved( self ):

        logging.debug( "HounsfieldEditor::onTransferFunctionPointRemoved" )

        self.preview()

    def onTransferFunctionPointChanged( self ):

        logging.debug( "HounsfieldEditor::onTransferFunctionPointChanged" )

    def onTransferFunctionPointDragStop( self ):

        logging.debug( "HounsfieldEditor::onTransferFunctionPointStopDrag" )

        self.preview()

    def onTransferFunctionPointColorChange( self ):

        logging.debug( "HounsfieldEditor::onTransferFunctionPointColorChange" )

        self.preview()

    def onTransferFunctionCreated( self ):

        logging.debug( "TFListener::onTransferFunctionDeletion" )

        self.preview()

    def onTransferFunctionDeletion( self ):

        logging.debug( "HounsfieldEditor::onTransferFunctionDeletion" )

        self.preview()
