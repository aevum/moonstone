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

from sqlobject import SQLObject, StringCol, DateCol, MultipleJoin, IntCol

class Patient(SQLObject):
    uid = StringCol(alternateID=True, length=100)
    studies = MultipleJoin("Study")
    name = StringCol(length=100)
    birthdate = DateCol()
    sex = StringCol(length=1)
    directory = StringCol(length=100)
    tmp = IntCol(default=0)
    
    def delete(self):
        logging.debug("In Patient::delete()")
        toRemove = [self.directory]
        super(Patient, self).destroySelf()
        return toRemove
    
    def allSeries(self):
        result = []
        for study in self.studies:
            print study.series
            result = result + study.series
        return result
    
    @staticmethod
    def findContaining(name=None):
        logging.debug("In Patient::findContaining()")
        select = ""
        first = True        
        if name:
            if not first:
                select = select + " AND"
            select = select + " name LIKE '%{0}%'".format(name)
            first = False
        
        if first:
            return list(Patient.select())
                   
        return list(Patient.select(select))