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
import logging
import optparse

if sys.hexversion < 0x02070000:
    print("This script requires Python 2.7 or later.")
    print("Currently run with version: {0}".format(sys.version))
    print("Please install it. The source for Python can be found at: " \
          "http://www.python.org/.")
    sys.exit(-1)
try:
    from PySide import QtCore, QtGui, QtOpenGL
except ImportError, e:
    print("This script requires PySide")
    print("Please install it. The source for PySide can be found at: " \
          "http://www.pyside.org")
    print("Error: {0}".format(e))
    sys.exit(-1)
try:
    import gdcm

    gdcm.Trace.DebugOff()
    gdcm.Trace.WarningOff()
    gdcm.Trace.ErrorOff()
except ImportError, e:
    print("This script requires GDCM 2.x.x")
    print("Please install it. The source for GDCM can be found at: " \
          "http://gdcm.sourceforge.net/.")
    print("Error: {0}".format(e))
    sys.exit(-1)
if gdcm.Version.GetMajorVersion() != 2:
    print("This script requires GDCM 2.x.x")
    print("Currently run with version: {0}".format(gdcm.Version.GetVersion()))
    print("Please upgrade your GDCM library. The " \
          "source for GDCM can be found at: http://gdcm.sourceforge.net/.")
    sys.exit(-1)
try:
    import vtk
    vtk.vtkObject.GlobalWarningDisplayOff()
except ImportError, e:
    print("This script requires VTK 5.8.x or later")
    print("Please install it. The source for VTK can be found at: " \
          "http://www.vtk.org/.")
    print("Error: {0}".format(e))
    sys.exit(-1)
if vtk.vtkVersion.GetVTKMajorVersion() != 5 \
        or vtk.vtkVersion.GetVTKMinorVersion() < 8:
    print("This script requires VTK 5.8.x or later")
    print("Currently run with version: {0}" \
          .format(vtk.vtkVersion.GetVTKVersion()))
    print("Please upgrade your VTK library. The " \
          "source for VTK can be found at: http://www.vtk.org/.")
    sys.exit(-1)
try:
    import vtkgdcm
except ImportError, e:
    print("This script requires GDCM 2.x.x with vtk")
    print("Please install it. The source for GDCM can be found at: " \
          "http://gdcm.sourceforge.net/.")
    print("Error: {0}".format(e))
    sys.exit(-1)

from .utils import constant as constant
from .utils import debuger as debuger
from .utils import logger as logger
from .utils import configure as configure
from .utils.versionconverter import convertToActualVersion
from .utils import i18n as i18n
from bloodstone.importer.database.dbutils import DBUtils


class Moonstone(QtGui.QApplication):

    def __init__(self, args):
        logging.debug("In Moonstone::__init__()")
        super(Moonstone, self).__init__(args)
        self.startDragTime()
        self.startDragDistance()
        # TODO: BUG PySide! Remove this impl!
        #self.locale()
        logging.debug(":: qt_locale")
        language = str(QtCore.QLocale.system().name())
        localedir = i18n.qt_locale_dir(language)
        localefilename = i18n.qt_locale_filename()
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

        self.showSplashScreen()
        align = QtCore.Qt.AlignTop | QtCore.Qt.AlignRight
        color = QtGui.QColor()
        color.setRgb(240, 240, 216)

        self.splash.showMessage(QtGui.QApplication.translate(
            "MainWindow", "Setting up the main window...", None,
            QtGui.QApplication.UnicodeUTF8), align, color)
        self.processEvents()

        self.splash.showMessage(QtGui.QApplication.translate(
            "MainWindow", "Configure moonstone...", None,
            QtGui.QApplication.UnicodeUTF8), align, color)
        self.configure()
        self.processEvents()
        
        self.splash.showMessage(QtGui.QApplication.translate(
            "MainWindow", "Checking database...", None,
            QtGui.QApplication.UnicodeUTF8), align, color)
        self.checkDatabase()
        self.processEvents()
        self.verifyVersion()
        

        self.splash.showMessage(QtGui.QApplication.translate(
            "MainWindow", "Show main window...", None,
            QtGui.QApplication.UnicodeUTF8), align, color)
        self.showMainWindow()

        if not QtGui.QSystemTrayIcon.isSystemTrayAvailable():
            self.connect(self, QtCore.SIGNAL("lastWindowClosed()"),
                         self, QtCore.SLOT("quit()"))

        self.hideSplashScreen()
        

    def showSplashScreen(self):
        logging.debug("In Moonstone::showSplashScreen()")
        from .gui.qt.widget import resources_rc
        self.splash = QtGui.QSplashScreen()
        self.splash.setPixmap(QtGui.QPixmap(
            ":/static/default/splashscreen/splashscreen.png"))
        self.splash.show()

    def hideSplashScreen(self):
        logging.debug("In Moonstone::hideSplashScreen()")
        self.splash.clearMessage()
        self.splash.finish(self.mainWindow)
        if self.splash:
            del self.splash

    def configure(self):
        logging.debug("In Moonstone::configure()")
        configure.qt_coding()
        configure.init_resources()

    def locale(self):
        logging.debug("In Moonstone::locale()")
        i18n.gettext_locale()
        #i18n.qt_locale()

    def showMainWindow(self):
        logging.debug("In Moonstone::showMainWindow()")
        from .gui.qt.mainwindow import MainWindow
        import time
        time.sleep(2)
        self.mainWindow = MainWindow("main")
        #self.mainWindow.createImportWindow()
        self.mainWindow.showMaximized()

    def checkDatabase(self):
        logging.debug("In Moonstone::checkDataBase()")
        dbUtil = DBUtils()
        dbUtil.createConnection()
        
    def verifyVersion(self):
        convertToActualVersion()
#        
#        
#
#if __name__ in ("__main__", "moonstone.main"):
#    Moonstone(sys.argv)
