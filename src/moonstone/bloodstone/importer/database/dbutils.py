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
from sqlobject import sqlhub, connectionForURI
import os
import patient, serie, study
from ....utils import constant
from ....utils import utils

class DBUtils(object):
    
    def __init__(self):
        self._dbFolder = utils.decode_string(os.path.join(constant.INSTALL_DIR, "data"))
        self._dbFile = os.path.join(self._dbFolder, "moonstone.db")

    
    def createConnection(self):
        connectionString = "sqlite:" + self._dbFile.replace("\\", "/").replace("C:","///C|/")
        connection = connectionForURI(connectionString)
        sqlhub.processConnection = connection
        if not os.path.exists(self._dbFile):
            if not os.path.exists(self._dbFolder):
                os.makedirs(self._dbFolder)
            self.createDatabase()
        else:
            self.clearDB()
    
    def clearDB(self):
        pass
             
    def createDatabase(self):   
        patient.Patient.createTable()
        study.Study.createTable()
        serie.Serie.createTable()
        #dicomimage.DicomImage.createTable()
    
    def deleteDatabase(self):
        os.remove(self._dbFile)
    
if __name__ == "__main__":
    con = DBUtils()
    con.deleteDatabase()
    con.createConnection()