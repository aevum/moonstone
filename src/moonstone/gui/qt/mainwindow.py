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
import traceback
import logging
from multiprocessing import Process, Value
from PySide import QtCore, QtGui

from .widget.mainwindow_ui import Ui_MainWindow
from .component.msystray import MSystray
from .component.mwindow import MWindow
from .component.mscreen import MScreen
from .qdicomprocess import QDicomProcess
from .saveas import SaveAs
from .importwindow import ImportWindow
from ...bloodstone.importer.importchooser import ImportChooser
from ...ilsa.ilsa import Ilsa
from ...gui.qt.widget.genericload import GenericProgressBar
from ...utils import constant as constant
from ...utils import profile as profile
from ...utils import constant
from ...bloodstone.scenes.imageplane import VtkImagePlane
from ...bloodstone.utils.data import persist_yaml_file
from ...bloodstone.importer.serieimporter import SerieImporter

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):

    def __init__(self, type, serie=None, parent=None, mainMainWindow=None):
        logging.debug("In MainWindow::__init__()")
        super(MainWindow, self).__init__(parent)
        self.mainMainWindow = mainMainWindow
        self.importWindow = None
        self._serie = serie
        self.setupUi(self)
        self.type = type
        self.createActions()
        self.createSignals()
        self.createSystray()
        if type == "main":
            self.createImportWindow()
        self.createPlugins()
        self.updateWidgets()
        #self.toolLayout = QtGui.QHBoxLayout()
        #self.scrollAreaWidgetContents.setLayout(self.toolLayout)
        

    def resizeEvent(self, event):
        logging.debug("In MainWindow::resizeEvent()")
        super(MainWindow, self).resizeEvent(event)

    def closeEvent(self, event):
        logging.debug("In MainWindow::closeEvent()")
        MainWindow.systray.removeWindow(self)
        for children in self.centralwidget.children():
            if isinstance(children, MWindow):
                children.setParent(None)
                children.close()
                children.destroy()
                self.mWindow = None
            children = None
            del children
        super(MainWindow, self).closeEvent(event)

    def setVisible(self, visible):
        logging.debug("In MainWindow::setVisible()")
        if MainWindow.systray and MainWindow.systray.windows.has_key(self):
            if(MainWindow.systray.windows[self]):
                MainWindow.systray.windows[self].minimizeAction.setEnabled(visible)
                MainWindow.systray.windows[self].maximizeAction.setEnabled(not self.isMaximized())
                MainWindow.systray.windows[self].restoreAction.setEnabled(self.isMaximized() or not visible)
        super(MainWindow, self).setVisible(visible)

    def createActions(self):
        logging.debug("In MainWindow::createActions()")

        # actions menu file
        self.connect(self.actionNew, QtCore.SIGNAL("triggered()"),
                     self.slotActionNew)
        self.connect(self.actionOpenProject, QtCore.SIGNAL("triggered()"),
                     self.slotActionOpenProject)
        self.connect(self.actionSave, QtCore.SIGNAL("triggered()"),
                     self.slotActionSave)
        self.connect(self.actionSaveAs, QtCore.SIGNAL("triggered()"),
                     self.slotActionSaveAs)
        self.connect(self.actionSaveAll, QtCore.SIGNAL("triggered()"),
                     self.slotActionSaveAll)
        self.connect(self.actionPrint, QtCore.SIGNAL("triggered()"),
                     self.slotActionPrint)
        self.connect(self.actionClose, QtCore.SIGNAL("triggered()"),
                     self.slotActionClose)
        self.connect(self.actionQuit, QtCore.SIGNAL("triggered()"),
                     self.slotActionQuit)

        # actions menu edit
        self.connect(self.actionPreferences, QtCore.SIGNAL("triggered()"),
                     self.slotActionPreferences)

        # actions menu view
        self.connect(self.actionSplitLeftNew, QtCore.SIGNAL("triggered()"),
                     self.slotActionSplitLeftNew)
        self.connect(self.actionSplitLeftClose, QtCore.SIGNAL("triggered()"),
                     self.slotActionSplitLeftClose)
        self.connect(self.actionFullScreen, QtCore.SIGNAL("triggered()"),
                     self.slotActionFullScreen)
        # actions menu help
        self.connect(self.actionHelpContents, QtCore.SIGNAL("triggered()"),
                     self.slotActionHelpContents)
        self.connect(self.actionReleaseNotes, QtCore.SIGNAL("triggered()"),
                     self.slotActionReleaseNotes)
        self.connect(self.actionReportBugs, QtCore.SIGNAL("triggered()"),
                     self.slotActionReportBugs)
        self.connect(self.actionCheckForUpdates, QtCore.SIGNAL("triggered()"),
                     self.slotActionCheckForUpdates)
        self.connect(self.actionAbout, QtCore.SIGNAL("triggered()"),
                     self.slotActionAbout)
        self.connect(self.actionLicense, QtCore.SIGNAL("triggered()"),
                     self.slotActionLicense)
        self.connect(self.actionShowPlaneLines, QtCore.SIGNAL("triggered()"),
                     self.slotActionShowPlaneLines)

        # actions panel tool properties
        self.connect(self.toolProperties,
                     QtCore.SIGNAL("visibilityChanged(bool)"),
                     self.slotToolPropertiesVisibilityChanged)

    def createSignals(self):
        logging.debug("In MainWindow::createSignals()")

    def createSystray(self):
        logging.debug("In MainWindow::createSystray()")
        if QtGui.QSystemTrayIcon.isSystemTrayAvailable():
            QtGui.QApplication.setQuitOnLastWindowClosed(True)
            if(self.type == "main"):
                MainWindow.systray = MSystray(self)
                MainWindow.systray.show()
            else :
                MainWindow.systray.addWindow(self)
        else:
            QtGui.QApplication.setQuitOnLastWindowClosed(True)
            MainWindow.systray = None

    def createPlugins(self):
        logging.debug("In MainWindow::createPlugins()")
        self.menuTools.clear()
        self.toolBarTools.clear()
        self.ilsa = Ilsa(self)
        if self.type == "main":
            self.toolBarTools.setVisible(False)
        else :
            self.menuFile.removeAction(self.actionNew)
            self.menuFile.removeAction(self.actionOpenProject)
            self.menuFile.removeAction(self.actionRecentProjects)
            self.toolBarActions.removeAction(self.actionNew)
            self.toolBarActions.removeAction(self.actionOpenProject)
            self.toolBarTools.setVisible(True)
        self.toolProperties.setVisible(False)
        #self.ilsa.notify(None)
        self.groupTools = QtGui.QActionGroup(self.menuTools)
        self.groupTools.setExclusive(False)
        for action in self.menuTools.actions():
            self.groupTools.addAction(action)
            if self.type == "main":
                action.setDisabled(True)

    def createImportWindow(self):
        logging.debug("In MainWindow::createImportWindow()")
        if not self.importWindow:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(
                    ":/static/default/icon/22x22/moonstone.png"),
                    QtGui.QIcon.Normal, QtGui.QIcon.Off)
            
            self.importWindow = ImportWindow(self.centralwidget)
            self.importWindow.setGeometry(QtCore.QRect(0, 0, 400, 400))
            self.gridLayout.addWidget(self.importWindow, 0, 0, 1, 1)
    
            self.connect(self.importWindow,
                QtCore.SIGNAL("importConfirmed(PyObject, PyObject, PyObject)"),
                self.processDesktopLayoutWindow)
    
            self.importWindow.show()
            self.importWindow.showMaximized()
            self.importWindow.normalizeSizeWidget()
            self.updateMenus(False)
        
    

    def processDesktopLayoutWindow(self, series, quality=0, generate3D=1):
        logging.debug("In MainWindow::processDesktopLayoutWindow()")
        widget = QDicomProcess(self, series, quality, generate3D)
        self.connect(widget,
            QtCore.SIGNAL("processDicomFinished(PyObject, PyObject, PyObject, PyObject)"),
            self.createDesktopLayoutWindow)
        widget.show()
        widget.normalizeSizeWidget()
        widget.startProcess()

    def createDesktopLayoutWindow(self, mwindows, series, generate3D, dicomProcess):
        logging.debug("In MainWindow::createDesktopLayoutWindow()")
        #mwindows[0]["imagedata"].ReleaseData()
        #return
        try:
            mainWindows = []
            for i, mwindow in enumerate(mwindows):
                dicomProcess.setProgress(50 + i*50/len(mwindows), 
                            QtGui.QApplication.translate("MainWindow", 
                                                         "Loading serie: {0}", 
                                                         None, 
                                                         QtGui.QApplication.UnicodeUTF8).format(i+1))
                mainWindow = MainWindow("import", series[i], mainMainWindow = self)
                mainWindow.setWindowTitle("{0} :: {1} - {2}".format(constant.NAME_PROGRAM, 
                                                                    series[i].study.patient.name, 
                                                                    series[i].description))
                
                widget = MWindow(mainWindow.ilsa, mainWindow.centralwidget, series[i])
                mainWindow.mWindow = widget
                widget.vtiPath = mwindow["vti"]
                widget.mainImageData = mwindow["imagedata"]
                
                mainWindow.gridLayout.addWidget(widget, 0, 0, 1, 1)
                mainWindow.updateMenus(True)
                mainWindow.toolBarTools.setVisible(True)
                                 
                widget.yamlPath = mwindow["yaml"]
                mainWindow.ilsa.pluginYamlPath = mwindow["pluginYaml"]
                for j, mscreen in  enumerate(mwindow["mScreens"]):
                    if not mscreen.has_key("scenes"):
                        mscreen["scenes"] = None
                    dicomProcess.setProgress(50 + i*50/len(mwindows) + (j*50/len(mwindows))/len(mwindow)/2, 
                                             QtGui.QApplication.translate("MainWindow", 
                                                         "Loading screen: {0}", 
                                                         None, 
                                                         QtGui.QApplication.UnicodeUTF8).format(i+1)) 
                    if not mscreen.has_key("cubeCorners"):
                        mscreen["cubeCorners"] = None
                        
                    if mscreen.has_key("creationTime"):
                        creationTime = mscreen["creationTime"]
                    else:
                        creationTime = -1
                        
                    screen = MScreen(mWindow=widget, vtkImageData=mwindow["imagedata"], name=mscreen["name"], cubeCorners=mscreen["cubeCorners"], creationTime=creationTime)
                    widget.addTab(screen, mscreen["name"])
                    if mscreen["scenes"]:
                        for scene in mscreen["scenes"]:
                            if not scene.has_key("data"):
                                scene["data"] = None
                            screen.createScene(int(scene["planeOrientation"]), data=scene["data"])

                        # each scene is created one after the other, so after all scenes had
                        # been created we must reload all planes so the slice widgets are
                        # loaded correctly
                        lst = [scene["data"] for scene in mscreen["scenes"]]
                        for scenedata in lst:
                            for plane in screen._planes:
                                if scenedata["id"] == plane.scene._id:
                                    plane.load( scenedata )

                    else :
                        screen.createScene(VtkImagePlane.PLANE_ORIENTATION_AXIAL)
                        if generate3D:  
                            screen.createScene(VtkImagePlane.PLANE_ORIENTATION_VOLUME)
                        screen.createScene(VtkImagePlane.PLANE_ORIENTATION_CORONAL)
                        screen.createScene(VtkImagePlane.PLANE_ORIENTATION_SAGITTAL)
                    if not mscreen.has_key("main"):
                        mscreen["main"] = True
                    screen.main = mscreen["main"]
                    screen.restoreDockGeometry()
                    if mscreen.has_key("lastChildId"):
                        screen.lastChildId = mscreen["lastChildId"]


                    progress =  50 + i*50/len(mwindows) +((j+1)*50/len(mwindows))/len(mwindow)/2
                    dicomProcess.setProgress(progress, QtGui.QApplication.translate("MainWindow", 
                                                         "Loading screen: {0}", 
                                                         None, 
                                                         QtGui.QApplication.UnicodeUTF8).format(i+1)) 
                mainWindow.loadPlugins(dicomProcess, progress, ((j+1)*50/len(mwindows))/len(mwindow)/2)
                mainWindows.append(mainWindow)
            dicomProcess.setProgress(100, QtGui.QApplication.translate("MainWindow", 
                                                         "Loading finished", 
                                                         None, 
                                                         QtGui.QApplication.UnicodeUTF8))
            for mainwindow in mainWindows:
                mainwindow.restoreSavedGeometry()
                mainwindow.showMaximized()
                mainwindow.slotActionSplitLeftNew()
            dicomProcess.close()
        except Exception as ex:
            traceback.print_exc(file=sys.stdout)
            self.close()
            QtGui.QMessageBox.critical(self, QtGui.QApplication.translate("ImportChooser", 
                                                     "Error", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8), 
                                                     QtGui.QApplication.translate("QDicomProcess", 
                                                     "Error founded during loading!", 
                                                     None, 
                                                     QtGui.QApplication.UnicodeUTF8))
        
    def loadPlugins(self, dicomReader, start, range):
        self.ilsa.loadFromFile(dicomReader, start, range)
        
    def updateWidgets(self):
        logging.debug("In MainWindow::updateWidgets()")
        self.setWindowTitle(constant.TITLE_PROGRAM)
        self.updateMenus(False)

    def updateMenus(self, flag=False):
        logging.debug("In MainWindow::updateMenus()")
        # menu file
        self.actionSave.setEnabled(flag)
        self.actionSaveAs.setEnabled(flag)
        self.actionSaveAll.setEnabled(flag)
        self.actionPrint.setEnabled(flag)
        self.actionClose.setEnabled(flag)

        # menu edit
        self.actionPreferences.setEnabled(flag)

        # menu view
        self.actionSplitLeftNew.setEnabled(flag)
        self.actionSplitLeftNew.setVisible(not flag)
        self.actionShowPlaneLines.setVisible(flag)
        self.actionSplitLeftClose.setEnabled(flag)
        self.actionSplitLeftClose.setVisible(flag)
        self.actionFullScreen.setEnabled(True)


    def slotActionShowPlaneLines(self):
        logging.debug("In MainWindow::actionShowPlaneLines()")
        for mscreen in self.mWindow.allTabs():
            for plane in mscreen.planes:
                if self.actionShowPlaneLines.isChecked():
                    plane.activateAllPlanes()
                else:
                    plane.desactivateAllPlanes()


    # actions menu file
    def slotActionNew(self):
        logging.debug("In MainWindow::slotActionNew()")
        self.importer = ImportChooser(self, self.importWindow.updateTree, -1)
        self.importer.show()

    def slotActionOpenProject(self):
        logging.debug("In MainWindow::slotActionOpenProject()")
        lastdir = "{0}{1}{2}".format(profile.get_last_directory_action_new(), 
                                     os.path.sep, 
                                     "exporter.st")
        caption = QtGui.QApplication.translate("MainWindow", 
                                               "Select the project file", 
                                                None, 
                                                QtGui.QApplication.UnicodeUTF8)
        inputFile = QtGui.QFileDialog.getOpenFileName(self, 
                                                      caption, 
                                                      lastdir, 
                                                      "File (*.st)")
        if inputFile[0]:
            if (sys.platform == 'win32'):
                filePath = os.path.abspath(inputFile[0])
                filePath = inputFile[0].encode('latin-1')
            else:
                filePath = os.path.abspath(str(inputFile[0]))
                
            importer  = SerieImporter(self, filePath, self.importWindow.updateTree)
            importer.start()
        

    def slotActionSave(self):
        logging.debug("In MainWindow::slotActionSave()")
        #busyCursor = QtGui.QCursor(QtCore.Qt.BusyCursor)
        #QtGui.QApplication.setOverrideCursor(busyCursor)
        try :
            self._saveLoad = GenericProgressBar(self, progressBar=False, stopButton=False)
            self._saveLoad.updateProgress(0, QtGui.QApplication.translate(
                    "MainWindow", "Saving...",
                    None, QtGui.QApplication.UnicodeUTF8))
            self._saveStatus = Value("c", "r")
            save(self, self._saveStatus, self.mWindow, self.ilsa)
            QtCore.QTimer.singleShot(500, self.verifySave)
        except Exception as inst:
            QtGui.QMessageBox.critical(self, QtGui.QApplication.translate(
                    "MainWindow", "Error",
                    None, QtGui.QApplication.UnicodeUTF8), QtGui.QApplication.translate(
                    "MainWindow", "Error saving study!",
                    None, QtGui.QApplication.UnicodeUTF8))
            #QtGui.QApplication.restoreOverrideCursor()
            print "Error saving:", inst
            
    def verifySave(self):
        if self._saveStatus.value != "r":
            #QtGui.QApplication.restoreOverrideCursor()
            self._saveLoad.stopProcess()
            if self._saveStatus.value == "e":
                QtGui.QMessageBox.critical(self, QtGui.QApplication.translate(
                    "MainWindow", "Error",
                    None, QtGui.QApplication.UnicodeUTF8), QtGui.QApplication.translate(
                    "MainWindow", "Error saving study!",
                    None, QtGui.QApplication.UnicodeUTF8))
        else:
            QtCore.QTimer.singleShot(500, self.verifySave)
            
    def slotActionSaveAs(self):
        logging.debug("In MainWindow::slotActionSaveAs()")
        self.saveAs = SaveAs(self._serie, self.mWindow, self.slotActionSave, self)
        self.saveAs.show()

    def slotActionSaveAll(self):
        logging.debug("In MainWindow::slotActionSaveAll()")

    def slotActionPrint(self):
        logging.debug("In MainWindow::slotActionPrint()")

    def slotActionClose(self):
        logging.debug("In MainWindow::slotActionClose()")

    def slotActionQuit(self):
        logging.debug("In MainWindow::slotActionQuit()")
        QtGui.QApplication.quit()

    def slotActionPreferences(self):
        logging.debug("In MainWindow::slotActionPreferences()")

    # actions menu view
    def slotActionSplitLeftNew(self):
        logging.debug("In MainWindow::slotActionSplitLeftNew()")
        if self.actionSplitLeftNew.isVisible():
            self.actionSplitLeftNew.setVisible(False)
            self.actionSplitLeftClose.setVisible(True)
            self.toolProperties.setVisible(True)
        else:
            self.actionSplitLeftNew.setVisible(True)
            self.actionSplitLeftClose.setVisible(False)
            self.toolProperties.setVisible(False)

    def slotActionSplitLeftClose(self):
        logging.debug("In MainWindow::slotActionSplitLeftClose()")
        if self.actionSplitLeftClose.isVisible():
            self.actionSplitLeftNew.setVisible(True)
            self.actionSplitLeftClose.setVisible(False)
            self.toolProperties.setVisible(False)
        else:
            self.actionSplitLeftNew.setVisible(False)
            self.actionSplitLeftClose.setVisible(True)
            self.toolProperties.setVisible(True)

    def slotActionFullScreen(self):
        logging.debug("In MainWindow::slotActionFullScreen()")
        if self.actionFullScreen.isChecked():
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(
                ":/static/default/icon/22x22/view-restore.png"),
                QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.actionFullScreen.setIcon(icon)
            self.actionFullScreen.setText(
                QtGui.QApplication.translate(
                    "MainWindow", "&Normalscreen",
                    None, QtGui.QApplication.UnicodeUTF8))
            self.actionFullScreen.setShortcut(
                QtGui.QApplication.translate(
                    "MainWindow", "F11", None,
                    QtGui.QApplication.UnicodeUTF8))
            self.showFullScreen()
        else:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(
                ":/static/default/icon/22x22/view-fullscreen.png"),
                QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.actionFullScreen.setIcon(icon)
            self.actionFullScreen.setText(
                QtGui.QApplication.translate(
                    "MainWindow", "&Fullscreen",
                    None, QtGui.QApplication.UnicodeUTF8))
            self.actionFullScreen.setShortcut(
                QtGui.QApplication.translate(
                    "MainWindow", "F11", None,
                    QtGui.QApplication.UnicodeUTF8))
            self.showNormal()

    # actions menu help
    def slotActionHelpContents(self):
        logging.debug("In MainWindow::slotActionHelpContents()")

    def slotActionReleaseNotes(self):
        logging.debug("In MainWindow::slotActionReleaseNotes()")

    def slotActionReportBugs(self):
        logging.debug("In MainWindow::slotActionReportBugs()")

    def slotActionCheckForUpdates(self):
        logging.debug("In MainWindow::slotActionCheckForUpdates()")

    def slotActionAbout(self):
        logging.debug("In MainWindow::slotActionAbout()")

    def slotActionLicense(self):
        logging.debug("In MainWindow::slotActionLicense()")

    # action panel tool properties
    def slotToolPropertiesVisibilityChanged(self, visible):
        logging.debug("In MainWindow::slotToolPropertiesVisibilityChanged()")
        if visible:
            self.actionSplitLeftNew.setVisible(False)
            self.actionSplitLeftClose.setVisible(True)
        else:
            self.actionSplitLeftNew.setVisible(True)
            self.actionSplitLeftClose.setVisible(False)

    # action subwindow
    def slotImportWindowStateChenged(self, oldState, newState):
        logging.debug("In MainWindow::slotImportWindowStateChenged()")

    def slotDesktopWindowStateChenged(self, oldState, newState):
        logging.debug("In MainWindow::slotSubWindowStateChenged()")
        subWindow = self.windowArea.activeSubWindow()
        if subWindow:
            self.ilsa.update(subWindow)

    def revertVisible(self):
        if self.parent().isVisible():
            self.hide()
        else:
            self.show()
    
    def quit(self, reason=None):
        if (self.type == "main"):
            QtGui.QApplication.instance().quit()
        else:
            self.close()

    @property
    def serie(self):
        return self._serie
    
    @serie.setter
    def serie(self, serie):
        self._serie = serie
        MainWindow.systray.renameWindow(self)
    
    def saveGeometrySettings(self):
        settings = QtCore.QSettings("Moonstone", "Medical")
        settings.setValue("serie-{0}-geometry".format(self.serie.id), self.saveGeometry())
        settings.setValue("serie-{0}-state".format(self.serie.id), self.saveState())
    
    def restoreSavedGeometry(self):
        settings = QtCore.QSettings("Moonstone", "Medical");
        self.restoreGeometry(settings.value("serie-{0}-geometry".format(self.serie.id)));
        self.restoreState(settings.value("serie-{0}-state".format(self.serie.id)));
       
def save(mainWindow, sharedStatus, mWindow, ilsa):
    try :
        mainWindow.saveGeometrySettings()
        windowYaml = mWindow.save()
        pluguinYaml = ilsa.save()
        persist_yaml_file(mWindow.yamlPath, windowYaml)
        persist_yaml_file(ilsa.pluginYamlPath, pluguinYaml)
        sharedStatus.value = "c"
    except Exception as ex:
        print "ex", ex
        sharedStatus.value = "e"
        
        