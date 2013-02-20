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

from widget.flipproperties_ui import Ui_FlipProperties


class FlipProperties(QtGui.QWidget, Ui_FlipProperties):

    def __init__(self, parent=None):
        logging.debug("In FlipProperties::__init__()")
        super(FlipProperties, self).__init__(parent)
        self.setupUi(self)
        self.createActions()

    def createActions(self):
        logging.debug("In FlipProperties::createActions()")
    

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    win = FlipProperties()
    win.show()
    sys.exit(app.exec_())

