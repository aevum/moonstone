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
import sys
import unicodedata
import hashlib

def normalizePath(path):
    if path:
        path = path.strip(" ^")
        path = path.replace(" /","/").replace(" \\", "\\")
        path = path.replace("^", "")
        path = os.path.normpath(path)
        if (sys.platform == 'win32'):
            if type(path) == unicode:
                path = path.encode('latin-1')
        else:
            path = str(path)
    else:
        path = ""
    return path
def normalizeStr(path):
    if path:
        path = path.strip(" ^")
        path = path.replace("^", "")
        path = os.path.normpath(path)
        if (sys.platform == 'win32'):
            if type(path) == unicode:
                path = path.encode('latin-1')
        else:
            path = str(path)
    return path

def filterStr(strr):
    if strr:
        if type(strr) == unicode:
            strr = unicodedata.normalize('NFKD', strr).encode("ascii", "ignore")
    return strr

def normalizeId(strr):
    if strr == None:
        return ""
    if strr:
        strr = strr.replace("/", "_").replace("\\", "_")
    return normalizeStr(filterStr(strr))


def hashStr(str, size=10):
    if not str:
        str = ''
    hash = hashlib.sha1()
    hash.update(str)
    return hash.hexdigest()[:size]

