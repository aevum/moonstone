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
import shutil
import glob
import locale
import logging
import logging.handlers
import logging.config

import constant as constant

def sys_coding():
    logging.debug("In sys_coding()")
    locale.setlocale(locale.LC_ALL, '')
    try:
        sys.setappdefaultencoding(constant.CODING)
    except AttributeError:
        try:
            reload(sys)
            sys.setdefaultencoding(constant.CODING)
        except LookupError:
            pass
        
sys_coding()

def qt_coding():
    logging.debug("In qt_coding()")
    from PySide import QtCore, QtGui
    try:
        QtGui.qApp.Encoding(QtGui.qApp.UnicodeUTF8)
        QtCore.QCoreApplication.Encoding(QtCore.QCoreApplication.UnicodeUTF8)
    except AttributeError:
        pass
    QtCore.QTextCodec.setCodecForTr(
        QtCore.QTextCodec.codecForName(constant.QT_CODING))
    QtCore.QTextCodec.setCodecForCStrings(
        QtCore.QTextCodec.codecForName(constant.QT_CODING))
    
def init_resources():
    logging.debug("In resources()")
    resources = constant.RESOURCES_DIR
    if not os.path.exists(resources):
        os.makedirs(resources)
        
    #if not os.path.exists(constant.HOUNSFIELD_FILE_PATH):
    #    shutil.copy2(constant.HOUNSFIELD_BASE_FILE_PATH, constant.HOUNSFIELD_FILE_PATH)
    
    
