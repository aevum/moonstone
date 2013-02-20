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
import main
import sys
        
if __name__ in ("__main__", "moonstone.macmain"):
    moonstone = main.Moonstone(sys.argv)
                    # TODO: BUG PySide! Remove this impl!
    from moonstone.utils import i18n
    from PySide import QtCore
    language = str(QtCore.QLocale.system().name())
    localedir = i18n.qt_locale_dir(language)
    localefilename = i18n.qt_locale_filename()
    translator = QtCore.QTranslator()
    trans = translator.load(localefilename, localedir)
    if trans:
        QtCore.QCoreApplication.installTranslator(translator)
    sys.exit(moonstone.exec_())
