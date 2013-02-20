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

from .widget.importsearch_ui import Ui_ImportSearch 
from ...utils import constant


class ImportSearch(QtGui.QWidget, Ui_ImportSearch):

    def __init__(self, parent=None):
        logging.debug("In ImportSearch::__init__()")
        super(ImportSearch, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(constant.TITLE_PROGRAM)
        self.createComponents()
        self.createSignals()


    def createComponents(self):
        logging.debug("In ImportSearch::createComponents()")


    def createSignals(self):
        logging.debug("In ImportSearch::createSignals()")

    def clearFields(self):
        logging.debug("In ImportSearch::clearFields()")
        self.patientName.setText("")
        self.studyDescription.setText("")
        self.serieDescription.setText("")
        self.modality.setText("")
        
    def anyFieldFilled(self):
        return True