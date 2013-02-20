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

from sqlobject import SQLObject, StringCol, ForeignKey, MultipleJoin, IntCol

class Study(SQLObject):
    uid = StringCol(alternateID=True)
    patient = ForeignKey("Patient", cascade = True)
    series = MultipleJoin("Serie")
    modality = StringCol(length=30)
    description = StringCol(length=100)
    institution = StringCol()
    tmp = IntCol(default=0)
    
    def delete(self):
        logging.debug("In Study::delete()")
        toRemove = []
        for serie in self.series:
            aux = serie.delete()
            toRemove = toRemove + aux
        super(Study, self).destroySelf()
        return toRemove
    
    @staticmethod
    def findContaining(patient=None, description=None, modality=None, institution=None):
        logging.debug("In Study::findContaining()")
        select = ""
        first = True
        if patient:
            select = "patient_id={0}".format(patient.id)
            first = False
        
        if description:
            if not first:
                select = select + " AND"
            select = select + " description LIKE '%{0}%'".format(description)
            first = False
       
        if modality:
            if not first:
                select = select + " and"
            select = select + " modality LIKE '%{0}%'".format(modality)
            first = False
            
        if institution:
            if not first:
                select = select + " and"
            select = select + " institution LIKE '%{0}%'".format(institution)
            first = False    
        
        if first:
            return list(Study.select())
          
        return list(Study.select(select))
