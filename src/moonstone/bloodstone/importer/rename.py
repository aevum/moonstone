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

from widget.rename_ui import Ui_Rename
import importer


class Rename(QtGui.QDialog, Ui_Rename):

    def __init__(self, parent=None):
        logging.debug("In Ui_Rename::__init__()")
        super(Rename, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Rename Serie")
        self.createActions()
        self._serie = None
        self._updater = None

    def createActions(self):
        logging.debug("In ImportChooser::createActions()")
        self.connect(self.Cancel, QtCore.SIGNAL("clicked()"),
                     self.slotActionCancel)
        self.connect(self.Ok, QtCore.SIGNAL("clicked()"),
                     self.slotActionOk)
    
    def renameSerie(self, serie, updater):
        self._serie = serie
        self._updater = updater
        self.newName.setText(self._serie["serieDescription"])
        self.show()
    
    def slotActionCancel(self):
        self.hide()
    
    def slotActionOk(self):
        self._serie["serieDescription"] = self.newName.text()
        self._serie["exists"] = importer.serieExists(self._serie["uid"], self._serie["serieDescription"])
        self._updater()
        self.hide()
