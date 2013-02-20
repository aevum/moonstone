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
from ..utils.strUtils import hashStr


from sqlobject import SQLObject, StringCol, ForeignKey, IntCol, FloatCol

class Serie(SQLObject):
    uid = StringCol()
    study = ForeignKey("Study", cascade = True)
    dicomImages = IntCol(default=0)
    file = StringCol()
    description = StringCol()
    thickness = StringCol()
    size = StringCol()
    zSpacing = FloatCol()
    tmp = IntCol(default=0)
    
    def delete(self):
        logging.debug("In Serie::delete()")
        toRemove = [os.path.join(self.study.patient.directory, hashStr(self.uid) + hashStr(self.description))]
        super(Serie, self).destroySelf()
        return toRemove
    
    @staticmethod
    def findContaining(study=None, file=None, description=None):
        logging.debug("In Serie::findContaining()")
        select = ""
        first = True
        if study:
            select = "study_id={0}".format(study.id)
            first = False
        
        if description:
            if not first:
                select = select + " AND"
            select = select + " description LIKE '%{0}%'".format(description)
            first = False
       
        if file:
            if not first:
                select = select + " and"
            select = select + " file LIKE '%{0}%'".format(file)
            first = False
            
        if first:
            return list(Serie.select())
        
        return list(Serie.select(select))
    
    
    def getFolder(self):
        return os.path.join(self.study.patient.directory, "{0}{1}".format(hashStr(self.uid), hashStr(self.description)))
   
