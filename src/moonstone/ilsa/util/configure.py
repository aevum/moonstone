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
import shutil
import hashlib
import logging

from ...utils import constant
    
def init_resources():
    logging.debug("In resources()")
    resources = constant.RESOURCES_DIR
    plugins = constant.PLUGINS_RESOURCES_DIR
    if not os.path.exists(resources):
        os.makedirs(resources)
    if not os.path.exists(plugins):
        os.makedirs(plugins)
    fileconfbase = os.path.join(constant.BASE_DIR, "moonstone", "ilsa", "resources", 
                                "plugin.conf")
    if not os.path.exists(fileconfbase):
        fileconfbase = os.path.join(os.path.abspath(os.path.dirname(__file__)), 
                                    constant.RESOURCES_PACKAGE, "ilsa", 
                                    "plugin.conf")
    if not os.path.exists(fileconfbase):
        fileconfbase = os.path.join(os.path.abspath(os.getcwd()), 
                                    constant.RESOURCES_PACKAGE, "ilsa", 
                                    "plugin.conf")
    fileconf = constant.PLUGINS_FILE_CONFIG
    d1, d2 = "", ""
    with open(fileconfbase) as f:
        md5 = hashlib.md5()
        md5.update(f.read())
        d1 = md5.hexdigest()
    if os.path.exists(fileconf):
        with open(fileconf) as f:
            md5 = hashlib.md5()
            md5.update(f.read())
            d2 = md5.hexdigest()
    if d1 != d2:
        shutil.copy2(fileconfbase, fileconf)