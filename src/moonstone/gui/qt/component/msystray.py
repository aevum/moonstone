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

from PySide import QtCore, QtGui


class MSystray(QtCore.QObject):

    def __init__(self, parent=None):
        logging.debug("In MSystray::__init__()")
        super(MSystray, self).__init__(parent)
        self.createActions()
        self.createTrayIcon()
        self.createMenu()
        self.addWindow(parent)
        

    def show(self):
        logging.debug("In MSystray::show()")
        self.trayIcon.show()

    def isVisible(self):
        logging.debug("In MSystray::isVisible()")
        return self.trayIcon.isVisible()

    def createActions(self):
        self.quitAction = QtGui.QAction(QtGui.QApplication.translate(
            "MainWindow", "&Quit", None,
            QtGui.QApplication.UnicodeUTF8), self.parent())
        iconQuit = QtGui.QIcon()
        iconQuit.addPixmap(QtGui.QPixmap(
            ":/static/default/icon/22x22/application-exit.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.quitAction.setIcon(iconQuit)
        self.quitAction.setObjectName("quitAction")
        self.connect(self.quitAction, QtCore.SIGNAL("triggered()"),
                     QtGui.QApplication.instance(), QtCore.SLOT("quit()"))
        
    def createTrayIcon(self):
        logging.debug("In MSystray::createTrayIcon()")
        trayIconMenu = QtGui.QMenu(self.parent())
        trayIconMenu.addSeparator()
        trayIconMenu.addAction(self.quitAction)

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(
            ":/static/default/icon/256x256/moonstone.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.trayIcon = QtGui.QSystemTrayIcon(self.parent())
        self.trayIcon.setContextMenu(trayIconMenu)
        self.trayIcon.setIcon(icon)
        self.connect(self.trayIcon,
            QtCore.SIGNAL("activated(QSystemTrayIcon::ActivationReason)"),
            self.slotActivationReason)


    def slotActivationReason(self, reason):
        logging.debug("In MSystray::slotActivationReason()")
        if reason == QtGui.QSystemTrayIcon.Trigger:
            if self.parent().isVisible():
                self.parent().hide()
            else:
                self.parent().show()
    
                
    def createMenu(self):
        logging.debug("In MSystray::createMenu()")
        self.windows = {}
#        self.trayIcon.

    def addWindow(self, window=None):
        logging.debug("In MSystray::addWindow()")
        if window == None:
            return 
        self.windows[window] = SystrayMenu()
        trayMenu = self.windows[window]
        
        iconMinimize = QtGui.QIcon()
        iconMinimize.addPixmap(QtGui.QPixmap(
            ":/static/default/icon/22x22/moonstone.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        trayMenu.minimizeAction = QtGui.QAction(QtGui.QApplication.translate(
            "MainWindow", "Mi&nimize", None,
            QtGui.QApplication.UnicodeUTF8), window)
        trayMenu.minimizeAction.setIcon(iconMinimize)
        trayMenu.minimizeAction.setObjectName("minimizeAction")
        self.connect(trayMenu.minimizeAction, QtCore.SIGNAL("triggered()"),
                     window, QtCore.SLOT("hide()"))

        trayMenu.maximizeAction = QtGui.QAction(QtGui.QApplication.translate(
            "MainWindow", "Ma&ximize", None,
            QtGui.QApplication.UnicodeUTF8), window)
        iconMaximize = QtGui.QIcon()
        iconMaximize.addPixmap(QtGui.QPixmap(
            ":/static/default/icon/22x22/moonstone.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        trayMenu.maximizeAction.setIcon(iconMaximize)
        trayMenu.maximizeAction.setObjectName("maximizeAction")
        self.connect(trayMenu.maximizeAction, QtCore.SIGNAL("triggered()"),
                     window, QtCore.SLOT("showMaximized()"))

        trayMenu.restoreAction = QtGui.QAction(QtGui.QApplication.translate(
            "MainWindow", "&Restore", None,
            QtGui.QApplication.UnicodeUTF8), window)
        iconRestore = QtGui.QIcon()
        iconRestore.addPixmap(QtGui.QPixmap(
            ":/static/default/icon/22x22/moonstone.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        trayMenu.restoreAction.setIcon(iconRestore)
        trayMenu.restoreAction.setObjectName("restoreAction")
        self.connect(trayMenu.restoreAction, QtCore.SIGNAL("triggered()"),
                     window, QtCore.SLOT("showNormal()"))
        if window.type == "main":
            title = "&Quit"
        else :
            title = "&Exit" 
        trayMenu.quitAction = QtGui.QAction(QtGui.QApplication.translate(
            "MainWindow", title, None,
            QtGui.QApplication.UnicodeUTF8), window)
        iconQuit = QtGui.QIcon()
        iconQuit.addPixmap(QtGui.QPixmap(
            ":/static/default/icon/22x22/application-exit.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        trayMenu.quitAction.setIcon(iconQuit)
        trayMenu.quitAction.setObjectName("quitAction")
        self.connect(trayMenu.quitAction, QtCore.SIGNAL("triggered()"),
                     window.quit)
        trayIconMenu = self.trayIcon.contextMenu()
        windowMenu = QtGui.QMenu(trayIconMenu)
        windowMenu.addAction(trayMenu.minimizeAction)
        windowMenu.addAction(trayMenu.maximizeAction)
        windowMenu.addAction(trayMenu.restoreAction)
        windowMenu.addSeparator()
        windowMenu.addAction(trayMenu.quitAction)
        trayMenu.parentMenu = windowMenu;
        if window.type == "main":
            title = "Main"
        else :
            title = window.serie.description
        windowMenu.setTitle(title)
        trayIconMenu.addAction(windowMenu.menuAction())
        trayIconMenu.removeAction(self.quitAction)
        trayIconMenu.addAction(self.quitAction)
        
    def removeWindow(self, window):
        if not self.windows.has_key(window):
            return
        trayMenu = self.windows[window]
        trayIconMenu = self.trayIcon.contextMenu()
        trayIconMenu.removeAction(trayMenu.parentMenu.menuAction())
        if self.windows.has_key(window):
            self.windows.pop(window)
            
    def renameWindow(self, window):
        if not self.windows.has_key(window):
            return
        trayMenu = self.windows[window]
        parentMenu = trayMenu.parentMenu
        parentMenu.setTitle(window.serie.description)
        
class SystrayMenu(object):
    def __init__(self):
        logging.debug("In SystrayMenu::__init__()")      
        pass