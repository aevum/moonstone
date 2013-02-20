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
import unittest

# Add Moonstone in Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.pardir, os.pardir, 
                                                os.pardir, os.pardir)))

import vtk
from PySide import QtCore, QtGui

from mwindow import MWindow
from mscreen import MScreen
from moonstone.gui.qt.axialplane import AxialPlane
from moonstone.gui.qt.volumeplane import VolumePlane
from moonstone.gui.qt.coronalplane import CoronalPlane
from moonstone.gui.qt.sagittalplane import SagittalPlane


class MWindowTest(unittest.TestCase):
    
    def setUp(self):
        logging.debug("In MWindowTest::setUp()")
        
    def test_mwindow(self):
        logging.debug("In MWindowTest::test_mwindow()")
        app = QtGui.QApplication(sys.argv)
        
        self.dockWidget1 = QtGui.QDockWidget()
        self.dockWidget1.setObjectName("dockWidget1")
        self.dockWidgetContents1 = QtGui.QWidget()
        self.dockWidgetContents1.setObjectName("dockWidgetContents1")
        self.dockWidget1.setWidget(self.dockWidgetContents1)
        
        self.dockWidget2 = QtGui.QDockWidget()
        self.dockWidget2.setObjectName("dockWidget2")
        self.dockWidgetContents2 = QtGui.QWidget()
        self.dockWidgetContents2.setObjectName("dockWidgetContents2")
        self.dockWidget2.setWidget(self.dockWidgetContents2)
        
        self.dockWidget3 = QtGui.QDockWidget()
        self.dockWidget3.setObjectName("dockWidget3")
        self.dockWidgetContents3 = QtGui.QWidget()
        self.dockWidgetContents3.setObjectName("dockWidgetContents3")
        self.dockWidget3.setWidget(self.dockWidgetContents3)
        
        self.dockWidget4 = QtGui.QDockWidget()
        self.dockWidget4.setObjectName("dockWidget4")
        self.dockWidgetContents4 = QtGui.QWidget()
        self.dockWidgetContents4.setObjectName("dockWidgetContents4")
        self.dockWidget4.setWidget(self.dockWidgetContents4)
        
        scenes = [self.dockWidget1, self.dockWidget2,
                  self.dockWidget3, self.dockWidget4]
        
        screen = MScreen()
        screen.layout2x2(scenes)
        
        widget = MWindow()
        widget.setWindowTitle("Test MWindow")
        widget.addTab(screen, "MScreen 1")
        widget.addTab(screen, "MScreen 2")
        widget.addTab(screen, "MScreen 3")
        widget.addTab(screen, "MScreen 4")
        widget.setGeometry(QtCore.QRect(500, 400, 300, 300))
        widget.show()
        
        app.exec_()
        
    def test_mwindow_with_actor(self):
        logging.debug("In MWindowTest::test_mwindow_with_actor()")
        app = QtGui.QApplication(sys.argv)
        
        cone = vtk.vtkConeSource()
        cone.SetResolution(8)
        coneMapper = vtk.vtkPolyDataMapper()
        coneMapper.SetInput(cone.GetOutput())
        coneActor = vtk.vtkActor()
        coneActor.SetMapper(coneMapper)
        
        self.dockWidget1 = AxialPlane()
        self.dockWidget1.setObjectName("dockWidget1")
        self.dockWidget1.scene.actor = coneActor
        self.dockWidget1.scene.renderer.ResetCamera()
        
        self.dockWidget2 = VolumePlane()
        self.dockWidget2.setObjectName("dockWidget2")
        self.dockWidget2.scene.actor = coneActor
        self.dockWidget2.scene.renderer.ResetCamera()
        
        self.dockWidget3 = CoronalPlane()
        self.dockWidget3.setObjectName("dockWidget3")
        self.dockWidget3.scene.actor = coneActor
        self.dockWidget3.scene.renderer.ResetCamera()
        
        self.dockWidget4 = SagittalPlane()
        self.dockWidget4.setObjectName("dockWidget4")
        self.dockWidget4.scene.actor = coneActor
        self.dockWidget4.scene.renderer.ResetCamera()
        
        scenes = [self.dockWidget1, self.dockWidget2,
                  self.dockWidget3, self.dockWidget4]
        
        screen = MScreen()
        screen.layout2x2(scenes)
        
        widget = MWindow()
        widget.setWindowTitle("Test MWindow")
        widget.addTab(screen, "MScreen 1")
        widget.addTab(screen, "MScreen 2")
        widget.addTab(screen, "MScreen 3")
        widget.addTab(screen, "MScreen 4")
        widget.setGeometry(QtCore.QRect(500, 400, 300, 300))
        widget.show()
        
        app.exec_()


class MScreenTest(unittest.TestCase):
    
    def setUp(self):
        logging.debug("In MScreenTest::setUp()")
        
    """def test_mscreen(self):
        logging.debug("In MScreenTest::test_mscreen()")
        app = QtGui.QApplication(sys.argv)
        
        print "test_mscreen: ..."
        
        widget = MScreen()
        widget.setWindowTitle("Test MScreen")
        widget.setGeometry(QtCore.QRect(500, 400, 300, 300))
        widget.show()
        
        app.exec_()"""
        
    def test_mscreen_layout2x2(self):
        logging.debug("In MScreenTest::test_mscreen()")
        app = QtGui.QApplication(sys.argv)
        
        print "test_mscreen_layout2x2: ..."
        
        vtkReader = vtk.vtkXMLImageDataReader()
        vtkReader.SetFileName("/home/nycholas/.moonstone/data/Juliana Felice^/1.76.380.18.2.389.14096.vti")
        vtkReader.Update()
        
        dockWidget1 = AxialPlane()
        dockWidget1.setObjectName("dockWidget1")
        
        dockWidget2 = VolumePlane()
        dockWidget2.setObjectName("dockWidget2")
        
        dockWidget3 = CoronalPlane()
        dockWidget3.setObjectName("dockWidget3")
        
        dockWidget4 = SagittalPlane()
        dockWidget4.setObjectName("dockWidget4")
        
        scenes = [dockWidget1, dockWidget2, dockWidget3, dockWidget4]
        
        widget = MScreen(vtkImageData=vtkReader.GetOutput())
        widget.setWindowTitle("Test MScreen")
        widget.layout2x2(scenes)
        widget.setGeometry(QtCore.QRect(500, 400, 300, 300))
        widget.show()
        
        app.exec_()
        
    """def test_mscreen1(self):
        logging.debug("In MScreenTest::test_mscreen()")
        app = QtGui.QApplication(sys.argv)
        
        print "test_mscreen: 0x0"
        
        widget = MScreen()
        widget.setWindowTitle("Test MScreen")
        widget.addScene(QtGui.QDockWidget("MScene 1"), 0, 0)
        widget.show()
        
        app.exec_()
    
    def test_mscreen1x1(self):
        logging.debug("In MScreenTest::test_mscreen()")
        app = QtGui.QApplication(sys.argv)
        
        print "test_mscreen: 1x1"
        
        widget = MScreen()
        widget.setWindowTitle("Test MScreen")
        widget.addScene(QtGui.QDockWidget("MScene 1"), 0, 0)
        widget.addScene(QtGui.QDockWidget("MScene 2"), 1, 0)
        widget.show()
        
        app.exec_()
        
    def test_mscreen1x1(self):
        logging.debug("In MScreenTest::test_mscreen()")
        app = QtGui.QApplication(sys.argv)
        
        print "test_mscreen: 1x1"
        
        widget = MScreen()
        widget.setWindowTitle("Test MScreen")
        widget.addScene(QtGui.QDockWidget("MScene 1"), 0, 0)
        widget.addScene(QtGui.QDockWidget("MScene 2"), 0, 1)
        widget.show()
        
        app.exec_()
        
    def test_mscreen2x1(self):
        logging.debug("In MScreenTest::test_mscreen()")
        app = QtGui.QApplication(sys.argv)
        
        print "test_mscreen: 2x1"
        
        widget = MScreen()
        widget.setWindowTitle("Test MScreen")
        widget.addScene(QtGui.QDockWidget("MScene 1"), 0, 0)
        widget.addScene(QtGui.QDockWidget("MScene 2"), 0, 1)
        widget.addScene(QtGui.QDockWidget("MScene 3"), 1, 0)
        widget.show()
        
        app.exec_()
        
    def test_mscreen2x1(self):
        logging.debug("In MScreenTest::test_mscreen()")
        app = QtGui.QApplication(sys.argv)
        
        print "test_mscreen: 2x1"
        
        widget = MScreen()
        widget.setWindowTitle("Test MScreen")
        widget.addScene(QtGui.QDockWidget("MScene 1"), 0, 0)
        widget.addScene(QtGui.QDockWidget("MScene 2"), 1, 0)
        widget.addScene(QtGui.QDockWidget("MScene 3"), 1, 1)
        widget.show()
        
        app.exec_()
        
    def test_mscreen2x2(self):
        logging.debug("In MScreenTest::test_mscreen()")
        app = QtGui.QApplication(sys.argv)
        
        print "test_mscreen: 2x2"
        
        widget = MScreen()
        widget.setWindowTitle("Test MScreen")
        widget.addScene(QtGui.QDockWidget("MScene 1"), 0, 0)
        widget.addScene(QtGui.QDockWidget("MScene 2"), 0, 1)
        widget.addScene(QtGui.QDockWidget("MScene 3"), 1, 0)
        widget.addScene(QtGui.QDockWidget("MScene 4"), 1, 1)
        widget.setGeometry(QtCore.QRect(500, 400, 300, 300))
        widget.show()
        
        app.exec_()
        
    def test_mscreen3x3(self):
        logging.debug("In MScreenTest::test_mscreen()")
        app = QtGui.QApplication(sys.argv)
        
        print "test_mscreen: 3x3"
        
        widget = MScreen()
        widget.setWindowTitle("Test MScreen 3x3")
        widget.addScene(QtGui.QDockWidget("MScene 0x0"), 0, 0)
        widget.addScene(QtGui.QDockWidget("MScene 0x1"), 0, 1)
        widget.addScene(QtGui.QDockWidget("MScene 0x2"), 0, 2)
        widget.addScene(QtGui.QDockWidget("MScene 1x0"), 1, 0)
        widget.addScene(QtGui.QDockWidget("MScene 1x1"), 1, 1)
        widget.addScene(QtGui.QDockWidget("MScene 1x2"), 1, 2)
        widget.addScene(QtGui.QDockWidget("MScene 2x0"), 2, 0)
        widget.addScene(QtGui.QDockWidget("MScene 2x1"), 2, 1)
        widget.addScene(QtGui.QDockWidget("MScene 2x2"), 2, 2)
        widget.setGeometry(QtCore.QRect(500, 400, 300, 300))
        widget.show()
        
        app.exec_()
    """


if __name__ == "__main__":
    unittest.main()