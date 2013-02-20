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
import locale
import logging

import constant as constant

def locale_dir():
    logging.debug("In locale_dir()")
    localedir = constant.LOCALE_DIR
    if not os.path.exists(localedir):
        logging.warning("Could not load the file internationalization {0}" \
                        .format(localedir))
        return ""
    return localedir

def gettext_locale(language=None):
    logging.debug("In gettext_locale()")
    if constant.USE_I18N:
        try:
            import gettext
            from gettext import gettext as _
            # TODO: Resolv directory locale system
            if os.path.exists(constant.LOCALE_DIR):
                path = constant.LOCALE_DIR
            else:
                logging.warning("Could not load the file internationalization")
            gettext.install(constant.LOCALE_DOMAIN, localedir=path,
                            unicode=True, codeset=language)
        except Exception, e:
            logging.warning(str(e))
            import __builtin__
            __builtin__.__dict__["_"] = lambda x: x
    else:
        import __builtin__
        __builtin__.__dict__["_"] = lambda x: x

def qt_locale_filename():
    logging.debug("In qt_locale_filename()")
    return "{0}".format(constant.LOCALE_DOMAIN)

def qt_locale_dir(language):
    logging.debug("In qt_locale_dir()")
    logging.debug("++ language: {0}".format(language))
    if not language:
        logging.warning("Invalid language")
        return locale_dir()
    localedir = os.path.join(locale_dir(), language, "LC_MESSAGES")
    if os.path.exists(localedir):
        return localedir
    else:
        logging.warning("Internationalization directory does not exist: {0}" \
                        .format(localedir))
    return locale_dir()

def qt_locale(language=None):
    logging.debug("In qt_locale()")
    logging.debug("++ language: {0}".format(language))
    if constant.USE_I18N:
        from PySide import QtCore, QtGui
        if language is None:
            language = str(QtCore.QLocale.system().name())
        localedir = QtCore.QString(qt_locale_dir(language))
        localefilename = QtCore.QString(qt_locale_filename())
        translator = QtCore.QTranslator()
        trans = translator.load(localefilename, localedir)
        if trans:
            logging.debug(":: Install Qt traslator")
            logging.debug("++ filename: {0}".format(localefilename))
            logging.debug("++ localdir: {0}".format(localedir))
            QtCore.QCoreApplication.installTranslator(translator)
        else:
            logging.warning("Could not load the file internationalization: {0}"\
                            .format(localefilename))
