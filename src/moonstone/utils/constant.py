# -*- coding: utf-8 -*-
#
# Moonstone is platform for processing of medical images (DICOM).
# Copyright (C) 2009-2011 by Neppo Tecnologia da Informa√ß√£o LTDA
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
import logging
import ConfigParser
import utils

config = ConfigParser.ConfigParser()
config.read(os.path.abspath(os.path.join(os.getcwd(), "resources", "moonstone.conf")))

# if python code is compiled by py2exe the base dir is the dir containing the main .exe file
if hasattr( sys, 'frozen' ) and sys.frozen in ( 'windows_exe', 'console_exe' ):
    BASE_DIR = os.path.dirname( os.path.abspath( sys.executable ) )
# otherwise if interpreted python code the base dir is src dir
else:
    BASE_DIR = os.path.join( os.path.abspath(os.path.dirname(__file__)), os.pardir, os.pardir )

DEBUG = False
LOGGING = True

NAME_PROGRAM = "Moonstone"
SENTENCE_PROGRAM = "Platform for analysis, processing and visualization " \
                   "of medical images (DICOM)"
TITLE_PROGRAM = "{0} :: {1}".format(NAME_PROGRAM, SENTENCE_PROGRAM)
VERSION_PROGRAM = "0.1"
NAME_BATTLE = "Killer Dolphin"
NAME_UNIX = config.get("moonstone", "name_unix")



HOME_DIR = os.path.abspath(os.path.expanduser(config.get("moonstone", "home_dir")))
INSTALL_DIR = os.path.join(HOME_DIR, config.get("moonstone", "install_dir"))

PACKAGE_DIR = config.get("moonstone", "install_dir")
USER_CONFIG_DIR = os.path.join(HOME_DIR, PACKAGE_DIR)

RESOURCES_DIR = os.path.join(USER_CONFIG_DIR, "resources")


HOUNSFIELD_FILE = "hounsfield.yaml"
fileconfbase = os.path.join(BASE_DIR, "moonstone", "resources",
                               HOUNSFIELD_FILE)
if not os.path.exists(fileconfbase):
    fileconfbase = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                               "resources",
                               "plugin.conf")
if not os.path.exists(fileconfbase):
    fileconfbase = os.path.join(os.path.abspath(os.getcwd()),
                               "resources" ,
                               HOUNSFIELD_FILE)
HOUNSFIELD_FILE_PATH = fileconfbase
    
LOGGING_LEVELS = {
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG
}
LOGGING_DIR = os.path.join(USER_CONFIG_DIR, "log")
LOGGING_LEVEL = LOGGING_LEVELS.get("debug", logging.NOTSET)
LOGGING_FILE_CONF = os.path.join(RESOURCES_DIR, "logging.conf")

DATA_DIR = os.path.join(USER_CONFIG_DIR, "data")

USE_I18N = True
CODING = "utf-8"
QT_CODING = "utf8"
LOCALE_DOMAIN = NAME_UNIX
LOCALE_DIR = os.path.abspath(os.path.join(BASE_DIR, "resources", "locale"))
if not os.path.exists(LOCALE_DIR):
    LOCALE_DIR = os.path.join(os.path.abspath(os.curdir), "resources", "locale")

RESOURCES_PACKAGE = "resources"
RESOURCES_DIR = os.path.join(USER_CONFIG_DIR, RESOURCES_PACKAGE, "ilsa")

PLUGINS_PACKAGE = "plugins"
PLUGINS_DIR = os.path.join(BASE_DIR, PLUGINS_PACKAGE)
PLUGINS_FILE_CONFIG = os.path.join(RESOURCES_DIR, "plugin.conf")
PLUGINS_RESOURCES_DIR = os.path.join(RESOURCES_DIR, "plugins")
