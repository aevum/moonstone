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
import hashlib
import logging
import logging.handlers
import logging.config

import constant as constant

def sys_logging():
    logging.debug("In sys_logging()")
    if constant.LOGGING:
        filelog = os.path.join(constant.LOGGING_DIR,
                               "{0}.log".format(constant.NAME_UNIX))
        logdir = os.path.abspath(os.path.split(filelog)[0])
        if not os.path.exists(logdir):
            os.makedirs(logdir)
        if not os.path.exists(filelog):
            with open(filelog, "w+") as fl:
                fl.write("")
        resources = constant.RESOURCES_DIR
        if not os.path.exists(resources):
            os.makedirs(resources)
        fileconfbase = os.path.join(constant.BASE_DIR, "resources", 
                                    "logging.conf")
        if not os.path.exists(fileconfbase):
            fileconfbase = os.path.join(
                os.path.abspath(os.path.dirname(__file__)), 
                "resources", "logging.conf")
        if not os.path.exists(fileconfbase):
            fileconfbase = os.path.join(os.path.abspath(os.getcwd()), 
                                        "resources", "logging.conf")
        fileconf = constant.LOGGING_FILE_CONF
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
        if os.path.exists(fileconf):
        #if False:
            logging.config.fileConfig(fileconf, {
                "LOGGING_FILENAME":  os.path.abspath(filelog).replace("\\","\\\\"),
            })
        else:
            level = constant.LOGGING_LEVEL
            logging.basicConfig(
                filename=filelog,
                filemode="w+",
                format="%(asctime)s %(levelname)-8s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                level=level
            )
    logging.debug("** Initialize logging **")

sys_logging()