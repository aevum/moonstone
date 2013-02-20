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
import shutil
import os

from PySide import QtCore, QtGui

from ...bloodstone.importer.database.serie import Serie
from .widget.saveas_ui import Ui_SaveAs
from ...utils import constant
from ...utils.strUtils import hashStr, normalizeId


class SaveAs(QtGui.QDialog, Ui_SaveAs):

    def __init__(self, serie, mwindow, slotSave, parent=None):
        logging.debug("In SaveAs::__init__()")
        super(SaveAs, self).__init__(parent)
        self._slotSave = slotSave
        self._mwindow = mwindow
        self._serie = serie
        self.setupUi(self)
        self.name.setText(serie.description)
        self.createComponents()
        self.createSignals()

    def createComponents(self):
        logging.debug("In SaveAs::createComponents()")

    def createSignals(self):
        logging.debug("In SaveAs::createSignals()")
        self.connect(self.cancelButton, QtCore.SIGNAL("clicked ( bool)"),
                     self.slotActionCancel)
        self.connect(self.okButton, QtCore.SIGNAL("clicked ( bool)"),
                     self.slotActionOk)
        
    def slotActionCancel(self, checked):
        self.close()
    
    def slotActionOk(self, checked):
        text = normalizeId(self.name.text())
        if text == self._serie.description:
            self._slotSave()
        else:
            serie = Serie(uid=self._serie.uid,
                  study=self._serie.study,
                  dicomImages=self._serie.dicomImages,
                  file= os.path.join("{0}{1}".format(hashStr(self._serie.uid), hashStr(text)), "{0}{1}".format(hashStr(self._serie.uid), ".yaml")),
                  description=text,
                  thickness=self._serie.thickness,
                  size=self._serie.size,
                  zSpacing=self._serie.zSpacing,
                  tmp=self._serie.tmp)
            for tab in self._mwindow.allTabs():
                if tab.vtiPath:
                    tab.vtiPath = tab.vtiPath.replace("{0}{1}".format(hashStr(self._serie.uid), hashStr(self._serie.description)), "{0}{1}".format(hashStr(self._serie.uid), hashStr(text)))
            self._mwindow.parent().parent().serie = serie
            self._mwindow.serie = serie
            self._mwindow.parent().parent().setWindowTitle("{0} :: {1} - {2}".format(constant.NAME_PROGRAM, serie.study.patient.name, serie.description))
            self._mwindow.yamlPath = self._mwindow.yamlPath.replace(hashStr(self._serie.uid)+hashStr(self._serie.description), hashStr(self._serie.uid)+hashStr(text), 1)
            self._mwindow.parent().parent().ilsa.pluginYamlPath = self._mwindow.yamlPath.replace(".yaml", ".plugin.yaml")
            oldPath = os.path.join(self._serie.study.patient.directory, hashStr(self._serie.uid)+hashStr(self._serie.description))
            newPath = os.path.join(self._serie.study.patient.directory, hashStr(self._serie.uid)+hashStr(text))
            shutil.copytree(oldPath, newPath)
            self._serie = serie
            self._slotSave()
        self.close()
